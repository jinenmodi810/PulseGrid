"""Phase 4 Gold marts: build star-schema facts/dim from Silver parquet."""

from __future__ import annotations

import io
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import boto3
import pandas as pd
from dotenv import load_dotenv

from app.core.config import get_settings
from app.observability.lineage import emit_lineage_event
from app.observability.metrics import (
    gold_processed_total,
    gold_rejected_total,
    update_runtime_metric,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_log = logging.getLogger("pulsegrid.gold_etl")


def _s3_client():
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.BRONZE_S3_ENDPOINT_URL,
        aws_access_key_id=s.BRONZE_S3_ACCESS_KEY,
        aws_secret_access_key=s.BRONZE_S3_SECRET_KEY,
        region_name=s.BRONZE_S3_REGION,
        use_ssl=bool(s.BRONZE_S3_USE_SSL),
    )


def _parse_ts(v: Any) -> datetime | None:
    if v is None or str(v).strip() == "":
        return None
    s = str(v).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(v: Any) -> str | None:
    dt = _parse_ts(v)
    if dt is None:
        return None
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _duration_seconds(start: Any, end: Any) -> float | None:
    s = _parse_ts(start)
    e = _parse_ts(end)
    if s is None or e is None:
        return None
    return (e - s).total_seconds()


def _list_keys(client: Any, bucket: str, prefix: str) -> list[str]:
    out: list[str] = []
    token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        resp = client.list_objects_v2(**kwargs)
        for obj in resp.get("Contents") or []:
            k = str(obj.get("Key") or "")
            if k.endswith(".parquet"):
                out.append(k)
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
        if not token:
            break
    return out


def _read_silver_dataset(client: Any, bucket: str, silver_prefix: str, dataset: str) -> pd.DataFrame:
    keys = _list_keys(client, bucket, f"{silver_prefix}/{dataset}/")
    if not keys:
        return pd.DataFrame()
    frames: list[pd.DataFrame] = []
    for key in keys:
        obj = client.get_object(Bucket=bucket, Key=key)
        data = obj["Body"].read()
        frames.append(pd.read_parquet(io.BytesIO(data), engine="pyarrow"))
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if "event_id" in df.columns:
        df = df.drop_duplicates(subset=["event_id"], keep="first")
    return df


def build_fact_incident_lifecycle(incident_df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rejected: list[dict[str, Any]] = []
    if incident_df.empty:
        return pd.DataFrame(), rejected
    out_rows: list[dict[str, Any]] = []
    work = incident_df.copy()
    work["occurred_at"] = work["occurred_at"].map(_iso)
    def _first_or_none(df: pd.DataFrame, col: str) -> Any:
        if col not in df.columns or df.empty:
            return None
        series = df[col].dropna()
        return series.iloc[0] if not series.empty else None

    def _last_or_none(df: pd.DataFrame, col: str) -> Any:
        if col not in df.columns or df.empty:
            return None
        series = df[col].dropna()
        return series.iloc[-1] if not series.empty else None

    for incident_id, grp in work.groupby("incident_id", dropna=False):
        if incident_id is None or str(incident_id).strip() == "":
            rejected.append({"reason": "incident_id_null", "record": grp.to_dict(orient="records")[0]})
            continue
        grp = grp.sort_values("occurred_at")
        created_at = grp.loc[grp["event_type"] == "incident.created", "occurred_at"].min() if "event_type" in grp else None
        assigned_at = grp.loc[grp["event_type"] == "incident.assigned", "occurred_at"].min() if "event_type" in grp else None
        accepted_at = grp.loc[grp["event_type"] == "incident.accepted", "occurred_at"].min() if "event_type" in grp else None
        completed_at = grp.loc[grp["event_type"] == "incident.completed", "occurred_at"].min() if "event_type" in grp else None
        time_to_assignment = _duration_seconds(created_at, assigned_at)
        time_to_acceptance = _duration_seconds(assigned_at or created_at, accepted_at)
        time_to_completion = _duration_seconds(created_at, completed_at)
        durations = [d for d in [time_to_assignment, time_to_acceptance, time_to_completion] if d is not None]
        if any(d < 0 for d in durations):
            rejected.append({"reason": "negative_duration", "incident_id": str(incident_id)})
            continue
        created_row = grp[grp["event_type"] == "incident.created"].head(1)
        latest_row = grp.tail(1)
        assigned_volunteer = grp["volunteer_id"].dropna() if "volunteer_id" in grp.columns else pd.Series(dtype=object)
        assigned_org = grp["organization_id"].dropna() if "organization_id" in grp.columns else pd.Series(dtype=object)
        out_rows.append(
            {
                "incident_id": str(incident_id),
                "created_at": created_at,
                "assigned_at": assigned_at,
                "accepted_at": accepted_at,
                "completed_at": completed_at,
                "time_to_assignment_seconds": time_to_assignment,
                "time_to_acceptance_seconds": time_to_acceptance,
                "time_to_completion_seconds": time_to_completion,
                "zone_id": _first_or_none(created_row, "zone_id"),
                "priority_label": _first_or_none(created_row, "priority_label"),
                "assigned_volunteer_id": (assigned_volunteer.iloc[-1] if not assigned_volunteer.empty else None),
                "assigned_organization_id": (assigned_org.iloc[-1] if not assigned_org.empty else None),
                "final_status": _last_or_none(latest_row, "status"),
            }
        )
    return pd.DataFrame(out_rows), rejected


def build_fact_volunteer_performance(
    incident_df: pd.DataFrame,
    volunteer_df: pd.DataFrame,
    lifecycle_df: pd.DataFrame,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rejected: list[dict[str, Any]] = []
    vol_ids: set[str] = set()
    if not incident_df.empty and "volunteer_id" in incident_df:
        vol_ids |= set(str(v) for v in incident_df["volunteer_id"].dropna() if str(v).strip())
    if not volunteer_df.empty and "volunteer_id" in volunteer_df:
        vol_ids |= set(str(v) for v in volunteer_df["volunteer_id"].dropna() if str(v).strip())
    rows: list[dict[str, Any]] = []
    for vid in sorted(vol_ids):
        assigned = int(((incident_df["event_type"] == "incident.assigned") & (incident_df["volunteer_id"] == vid)).sum()) if not incident_df.empty else 0
        accepted = int(((incident_df["event_type"] == "incident.accepted") & (incident_df["volunteer_id"] == vid)).sum()) if not incident_df.empty else 0
        completed = int(((incident_df["event_type"] == "incident.completed") & (incident_df["volunteer_id"] == vid)).sum()) if not incident_df.empty else 0

        latest_credits = None
        latest_trust = None
        if not volunteer_df.empty:
            vg = volunteer_df[volunteer_df["volunteer_id"] == vid].sort_values("occurred_at")
            if not vg.empty:
                latest_credits = vg["credits"].dropna().iloc[-1] if not vg["credits"].dropna().empty else None
                latest_trust = vg["trust_score"].dropna().iloc[-1] if not vg["trust_score"].dropna().empty else None

        avg_completion = None
        if not lifecycle_df.empty and "assigned_volunteer_id" in lifecycle_df.columns:
            lg = lifecycle_df[lifecycle_df["assigned_volunteer_id"] == vid]
            vals = lg["time_to_completion_seconds"].dropna().tolist() if "time_to_completion_seconds" in lg.columns else []
            vals = [float(v) for v in vals if float(v) >= 0]
            if vals:
                avg_completion = float(sum(vals) / len(vals))

        if not vid.strip():
            rejected.append({"reason": "volunteer_id_null", "record": {"volunteer_id": vid}})
            continue
        rows.append(
            {
                "volunteer_id": vid,
                "tasks_assigned": assigned,
                "tasks_accepted": accepted,
                "tasks_completed": completed,
                "latest_credits": latest_credits,
                "latest_trust_score": latest_trust,
                "avg_completion_time_seconds": avg_completion,
            }
        )
    df = pd.DataFrame(rows)
    return df, rejected


def build_fact_org_capacity(org_df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rejected: list[dict[str, Any]] = []
    if org_df.empty:
        return pd.DataFrame(), rejected
    rows: list[dict[str, Any]] = []
    for _, r in org_df.iterrows():
        org_id = str(r.get("organization_id") or "").strip()
        if not org_id:
            rejected.append({"reason": "organization_id_null", "record": r.to_dict()})
            continue
        updated = {}
        try:
            updated = json.loads(str(r.get("updated_fields_json") or "{}"))
            if not isinstance(updated, dict):
                updated = {}
        except Exception:  # noqa: BLE001
            updated = {}
        rows.append(
            {
                "organization_id": org_id,
                "captured_at": _iso(r.get("occurred_at")),
                "beds_available": updated.get("beds_available"),
                "oxygen_units": updated.get("oxygen_units"),
                "ambulances_available": updated.get("ambulances_available"),
                "shelter_units": updated.get("shelter_units"),
                "food_capacity_units": updated.get("food_capacity_units"),
                "rescue_units": updated.get("rescue_units"),
            }
        )
    return pd.DataFrame(rows), rejected


def build_dim_time(*dfs: pd.DataFrame) -> pd.DataFrame:
    ts_values: list[str] = []
    for df in dfs:
        if df.empty:
            continue
        for c in ["created_at", "assigned_at", "accepted_at", "completed_at", "captured_at"]:
            if c in df.columns:
                ts_values.extend([str(x) for x in df[c].dropna().tolist() if str(x).strip()])
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for ts in ts_values:
        dt = _parse_ts(ts)
        if dt is None:
            continue
        date_key = int(dt.strftime("%Y%m%d"))
        key = f"{date_key}:{dt:%H}"
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "date_key": date_key,
                "date": dt.strftime("%Y-%m-%d"),
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": dt.hour,
            }
        )
    return pd.DataFrame(rows)


def _write_parquet_dataset(client: Any, bucket: str, *, prefix: str, dataset: str, df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    out: list[str] = []
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # event_type partition if available, else run_date partition.
    if "event_type" in df.columns:
        parts = sorted(set(str(x) for x in df["event_type"].dropna().tolist() if str(x).strip()))
        for et in parts:
            sub = df[df["event_type"] == et]
            if sub.empty:
                continue
            run_dt = datetime.now(tz=timezone.utc)
            key = f"{prefix}/{dataset}/event_type={et}/year={run_dt:%Y}/month={run_dt:%m}/day={run_dt:%d}/batch_{ts}.parquet"
            buf = io.BytesIO()
            sub.to_parquet(buf, engine="pyarrow", index=False)
            client.put_object(Bucket=bucket, Key=key, Body=buf.getvalue(), ContentType="application/octet-stream")
            out.append(key)
        return out
    run_dt = datetime.now(tz=timezone.utc)
    key = f"{prefix}/{dataset}/year={run_dt:%Y}/month={run_dt:%m}/day={run_dt:%d}/batch_{ts}.parquet"
    buf = io.BytesIO()
    df.to_parquet(buf, engine="pyarrow", index=False)
    client.put_object(Bucket=bucket, Key=key, Body=buf.getvalue(), ContentType="application/octet-stream")
    out.append(key)
    return out


def _write_rejected(client: Any, bucket: str, rejected_prefix: str, records: list[dict[str, Any]]) -> str | None:
    if not records:
        return None
    now = datetime.now(tz=timezone.utc)
    key = f"{rejected_prefix}/year={now:%Y}/month={now:%m}/day={now:%d}/batch_{now:%Y%m%dT%H%M%SZ}.json"
    body = (json.dumps(records, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    client.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
    return key


def run_once() -> dict[str, Any]:
    s = get_settings()
    client = _s3_client()
    incident_silver = _read_silver_dataset(client, s.SILVER_BUCKET, s.SILVER_PREFIX, "incident_events")
    org_silver = _read_silver_dataset(client, s.SILVER_BUCKET, s.SILVER_PREFIX, "organization_events")
    volunteer_silver = _read_silver_dataset(client, s.SILVER_BUCKET, s.SILVER_PREFIX, "volunteer_events")

    lifecycle_df, lifecycle_rej = build_fact_incident_lifecycle(incident_silver)
    vol_perf_df, vol_rej = build_fact_volunteer_performance(incident_silver, volunteer_silver, lifecycle_df)
    org_capacity_df, org_rej = build_fact_org_capacity(org_silver)
    dim_time_df = build_dim_time(lifecycle_df, org_capacity_df)

    rejected = lifecycle_rej + vol_rej + org_rej
    written = {
        "fact_incident_lifecycle": _write_parquet_dataset(client, s.GOLD_BUCKET, prefix=s.GOLD_PREFIX, dataset="fact_incident_lifecycle", df=lifecycle_df),
        "fact_volunteer_performance": _write_parquet_dataset(
            client,
            s.GOLD_BUCKET,
            prefix=s.GOLD_PREFIX,
            dataset="fact_volunteer_performance",
            df=vol_perf_df,
        ),
        "fact_org_capacity": _write_parquet_dataset(client, s.GOLD_BUCKET, prefix=s.GOLD_PREFIX, dataset="fact_org_capacity", df=org_capacity_df),
        "dim_time": _write_parquet_dataset(client, s.GOLD_BUCKET, prefix=s.GOLD_PREFIX, dataset="dim_time", df=dim_time_df),
    }
    rejected_key = _write_rejected(client, s.GOLD_BUCKET, s.GOLD_REJECTED_PREFIX, rejected)
    summary = {
        "incident_rows": int(len(lifecycle_df)),
        "volunteer_rows": int(len(vol_perf_df)),
        "org_rows": int(len(org_capacity_df)),
        "dim_time_rows": int(len(dim_time_df)),
        "rejected_rows": int(len(rejected)),
        "rejected_key": rejected_key,
        "written_keys": written,
    }
    processed_total = int(len(lifecycle_df) + len(vol_perf_df) + len(org_capacity_df))
    gold_processed_total.inc(float(processed_total))
    gold_rejected_total.inc(float(len(rejected)))
    update_runtime_metric("gold_processed", processed_total)
    update_runtime_metric("gold_rejected", int(len(rejected)))
    _log.info("gold_etl_run_summary %s", summary)
    emit_lineage_event(
        job_name="gold_etl",
        status="success",
        inputs=[f"s3://{s.SILVER_BUCKET}/{s.SILVER_PREFIX}/"],
        outputs=[
            f"s3://{s.GOLD_BUCKET}/{s.GOLD_PREFIX}/fact_incident_lifecycle/",
            f"s3://{s.GOLD_BUCKET}/{s.GOLD_PREFIX}/fact_volunteer_performance/",
            f"s3://{s.GOLD_BUCKET}/{s.GOLD_PREFIX}/fact_org_capacity/",
            f"s3://{s.GOLD_BUCKET}/{s.GOLD_PREFIX}/dim_time/",
        ],
        run_stats=summary,
    )
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
    run_once()


if __name__ == "__main__":
    main()
