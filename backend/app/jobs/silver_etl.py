"""Phase 3 Silver ETL: Bronze raw envelopes -> Silver parquet datasets."""

from __future__ import annotations

import gzip
import io
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import boto3
import pandas as pd
from dotenv import load_dotenv

from app.core.config import get_settings
from app.observability.lineage import emit_lineage_event
from app.observability.metrics import (
    silver_processed_total,
    silver_rejected_total,
    update_runtime_metric,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_log = logging.getLogger("pulsegrid.silver_etl")

REQUIRED_FIELDS = {
    "event_id",
    "event_type",
    "aggregate_type",
    "aggregate_id",
    "schema_version",
    "event_version",
    "enqueued_at",
    "payload",
}

DOMAIN_TO_DATASET = {
    "incident": "incident_events",
    "organization": "organization_events",
    "volunteer": "volunteer_events",
}

DEFAULT_CHECKPOINT = {
    "processed_object_keys": [],
    "last_run_started_at": None,
    "last_run_completed_at": None,
    "total_processed": 0,
    "total_rejected": 0,
    "total_written": 0,
}


@dataclass
class NormalizedRecord:
    dataset: str
    record: dict[str, Any]


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


def _parse_iso(ts: str | None) -> datetime:
    if not ts:
        return datetime.now(tz=timezone.utc)
    raw = str(ts).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return datetime.now(tz=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso_utc(ts: str | None) -> str:
    return _parse_iso(ts).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _domain_from_event_type(event_type: str) -> str:
    et = str(event_type or "").strip()
    if et.startswith("incident."):
        return "incident"
    if et.startswith("organization."):
        return "organization"
    if et.startswith("volunteer."):
        return "volunteer"
    return "unknown"


def _decode_object_body(key: str, blob: bytes) -> dict[str, Any]:
    if key.endswith(".gz"):
        blob = gzip.decompress(blob)
    return json.loads(blob.decode("utf-8"))


def _validate_envelope(envelope: dict[str, Any]) -> tuple[bool, str]:
    if not isinstance(envelope, dict):
        return False, "envelope_not_object"
    missing = sorted([f for f in REQUIRED_FIELDS if f not in envelope])
    if missing:
        return False, f"missing_required_fields:{','.join(missing)}"
    if not isinstance(envelope.get("payload"), dict):
        return False, "payload_not_object"
    if not str(envelope.get("event_id") or "").strip():
        return False, "missing_event_id"
    if not str(envelope.get("event_type") or "").strip():
        return False, "missing_event_type"
    return True, ""


def _flatten_incident(envelope: dict[str, Any]) -> dict[str, Any]:
    payload = envelope["payload"]
    return {
        "event_id": str(envelope["event_id"]),
        "event_type": str(envelope["event_type"]),
        "aggregate_type": str(envelope["aggregate_type"]),
        "aggregate_id": str(envelope["aggregate_id"]),
        "schema_version": int(envelope["schema_version"]),
        "event_version": int(envelope["event_version"]),
        "enqueued_at": _iso_utc(str(envelope["enqueued_at"])),
        "incident_id": str(payload.get("incident_id") or envelope["aggregate_id"]),
        "zone_id": payload.get("zone_id"),
        "status": payload.get("status"),
        "priority_label": payload.get("priority_label"),
        "reporter_user_id": payload.get("reporter_user_id"),
        "volunteer_id": payload.get("volunteer_id"),
        "organization_id": payload.get("organization_id"),
        "occurred_at": _iso_utc(str(payload.get("occurred_at") or envelope["enqueued_at"])),
        "payload_json": json.dumps(payload, separators=(",", ":"), ensure_ascii=True),
    }


def _flatten_organization(envelope: dict[str, Any]) -> dict[str, Any]:
    payload = envelope["payload"]
    updated = payload.get("updated") if isinstance(payload.get("updated"), dict) else {}
    return {
        "event_id": str(envelope["event_id"]),
        "event_type": str(envelope["event_type"]),
        "aggregate_type": str(envelope["aggregate_type"]),
        "aggregate_id": str(envelope["aggregate_id"]),
        "schema_version": int(envelope["schema_version"]),
        "event_version": int(envelope["event_version"]),
        "enqueued_at": _iso_utc(str(envelope["enqueued_at"])),
        "organization_id": str(payload.get("organization_id") or envelope["aggregate_id"]),
        "updated_fields_json": json.dumps(updated, separators=(",", ":"), ensure_ascii=True),
        "occurred_at": _iso_utc(str(payload.get("occurred_at") or envelope["enqueued_at"])),
        "payload_json": json.dumps(payload, separators=(",", ":"), ensure_ascii=True),
    }


def _flatten_volunteer(envelope: dict[str, Any]) -> dict[str, Any]:
    payload = envelope["payload"]
    return {
        "event_id": str(envelope["event_id"]),
        "event_type": str(envelope["event_type"]),
        "aggregate_type": str(envelope["aggregate_type"]),
        "aggregate_id": str(envelope["aggregate_id"]),
        "schema_version": int(envelope["schema_version"]),
        "event_version": int(envelope["event_version"]),
        "enqueued_at": _iso_utc(str(envelope["enqueued_at"])),
        "volunteer_id": str(payload.get("volunteer_id") or envelope["aggregate_id"]),
        "incident_id": payload.get("incident_id"),
        "credits": payload.get("credits"),
        "trust_score": payload.get("trust_score"),
        "occurred_at": _iso_utc(str(payload.get("occurred_at") or envelope["enqueued_at"])),
        "payload_json": json.dumps(payload, separators=(",", ":"), ensure_ascii=True),
    }


def normalize_envelope(envelope: dict[str, Any]) -> tuple[NormalizedRecord | None, str]:
    ok, reason = _validate_envelope(envelope)
    if not ok:
        return None, reason
    domain = _domain_from_event_type(str(envelope["event_type"]))
    if domain == "incident":
        return NormalizedRecord(dataset=DOMAIN_TO_DATASET[domain], record=_flatten_incident(envelope)), ""
    if domain == "organization":
        return NormalizedRecord(dataset=DOMAIN_TO_DATASET[domain], record=_flatten_organization(envelope)), ""
    if domain == "volunteer":
        return NormalizedRecord(dataset=DOMAIN_TO_DATASET[domain], record=_flatten_volunteer(envelope)), ""
    return None, "unsupported_domain"


def _list_bronze_objects(client: Any, bucket: str, prefix: str) -> list[str]:
    out: list[str] = []
    token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        resp = client.list_objects_v2(**kwargs)
        for obj in resp.get("Contents") or []:
            key = str(obj.get("Key") or "")
            if "/_dead_letter/" in key:
                continue
            if key.endswith(".json") or key.endswith(".json.gz"):
                out.append(key)
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
        if not token:
            break
    return out


def _load_checkpoint(client: Any, bucket: str, checkpoint_key: str) -> dict[str, Any]:
    try:
        obj = client.get_object(Bucket=bucket, Key=checkpoint_key)
        payload = json.loads(obj["Body"].read().decode("utf-8"))
        if not isinstance(payload, dict):
            return dict(DEFAULT_CHECKPOINT)
        merged = dict(DEFAULT_CHECKPOINT)
        merged.update(payload)
        if not isinstance(merged.get("processed_object_keys"), list):
            merged["processed_object_keys"] = []
        return merged
    except Exception:  # noqa: BLE001
        return dict(DEFAULT_CHECKPOINT)


def _save_checkpoint(client: Any, bucket: str, checkpoint_key: str, checkpoint: dict[str, Any]) -> None:
    body = (json.dumps(checkpoint, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    client.put_object(Bucket=bucket, Key=checkpoint_key, Body=body, ContentType="application/json")


def _select_objects_for_run(
    all_keys: list[str],
    processed_keys: list[str],
    *,
    full_refresh: bool,
) -> tuple[list[str], int]:
    if full_refresh:
        return list(all_keys), 0
    done = set(str(k) for k in processed_keys)
    selected = [k for k in all_keys if k not in done]
    skipped = max(0, len(all_keys) - len(selected))
    return selected, skipped


def _silver_partition_key(event_type: str, occurred_at: str) -> str:
    dt = _parse_iso(occurred_at)
    return f"event_type={event_type}/year={dt:%Y}/month={dt:%m}/day={dt:%d}"


def _write_dataset_parquet(
    client: Any,
    bucket: str,
    *,
    silver_prefix: str,
    dataset: str,
    rows: list[dict[str, Any]],
) -> list[str]:
    if not rows:
        return []
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        p = _silver_partition_key(str(row["event_type"]), str(row["occurred_at"]))
        groups.setdefault(p, []).append(row)
    written_keys: list[str] = []
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for partition, part_rows in groups.items():
        df = pd.DataFrame(part_rows)
        buf = io.BytesIO()
        df.to_parquet(buf, engine="pyarrow", index=False)
        key = f"{silver_prefix}/{dataset}/{partition}/batch_{ts}.parquet"
        client.put_object(Bucket=bucket, Key=key, Body=buf.getvalue(), ContentType="application/octet-stream")
        written_keys.append(key)
    return written_keys


def _write_rejected(client: Any, bucket: str, *, rejected_prefix: str, records: list[dict[str, Any]]) -> str | None:
    if not records:
        return None
    ts = datetime.now(tz=timezone.utc)
    key = f"{rejected_prefix}/year={ts:%Y}/month={ts:%m}/day={ts:%d}/batch_{ts:%Y%m%dT%H%M%SZ}.json"
    body = (json.dumps(records, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    client.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
    return key


def process_envelopes_for_run(items: list[tuple[str, dict[str, Any]]]) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], int]:
    seen_event_ids: set[str] = set()
    datasets: dict[str, list[dict[str, Any]]] = {
        "incident_events": [],
        "organization_events": [],
        "volunteer_events": [],
    }
    rejected: list[dict[str, Any]] = []
    for key, envelope in items:
        try:
            normalized, reason = normalize_envelope(envelope)
            if normalized is None:
                rejected.append(
                    {
                        "reason": reason,
                        "source_key": key,
                        "captured_at": datetime.now(tz=timezone.utc).isoformat(),
                    }
                )
                continue
            eid = str(normalized.record["event_id"])
            if eid in seen_event_ids:
                continue
            seen_event_ids.add(eid)
            datasets[normalized.dataset].append(normalized.record)
        except Exception as exc:  # noqa: BLE001
            rejected.append(
                {
                    "reason": f"parse_failure:{str(exc)[:200]}",
                    "source_key": key,
                    "captured_at": datetime.now(tz=timezone.utc).isoformat(),
                }
            )
    return datasets, rejected, len(seen_event_ids)


def run_once() -> dict[str, Any]:
    s = get_settings()
    client = _s3_client()
    checkpoint = _load_checkpoint(client, s.SILVER_BUCKET, s.SILVER_CHECKPOINT_KEY)
    all_keys = _list_bronze_objects(client, s.SILVER_BUCKET, f"{s.SILVER_BRONZE_PREFIX}/")
    keys, skipped_checkpointed = _select_objects_for_run(
        all_keys,
        checkpoint.get("processed_object_keys") or [],
        full_refresh=bool(s.SILVER_FULL_REFRESH),
    )
    run_started_at = datetime.now(tz=timezone.utc).isoformat()
    _log.info(
        "silver_etl_discovery discovered_objects=%s skipped_checkpointed_objects=%s processed_new_objects=%s full_refresh=%s",
        len(all_keys),
        skipped_checkpointed,
        len(keys),
        bool(s.SILVER_FULL_REFRESH),
    )
    items: list[tuple[str, dict[str, Any]]] = []
    for key in keys:
        obj = client.get_object(Bucket=s.SILVER_BUCKET, Key=key)
        raw = obj["Body"].read()
        try:
            envelope = _decode_object_body(key, raw)
            if isinstance(envelope, dict):
                items.append((key, envelope))
            else:
                items.append((key, {}))
        except Exception as exc:  # noqa: BLE001
            _log.warning("silver_decode_failed key=%s error=%s", key, str(exc)[:200])
            items.append((key, {}))
    datasets, rejected, deduped = process_envelopes_for_run(items)
    written: dict[str, list[str]] = {}
    for dataset, rows in datasets.items():
        written[dataset] = _write_dataset_parquet(
            client,
            s.SILVER_BUCKET,
            silver_prefix=s.SILVER_PREFIX,
            dataset=dataset,
            rows=rows,
        )
    rejected_key = _write_rejected(client, s.SILVER_BUCKET, rejected_prefix=s.SILVER_REJECTED_PREFIX, records=rejected)
    total_written = sum(len(v) for v in written.values())
    run_completed_at = datetime.now(tz=timezone.utc).isoformat()
    new_processed_keys = sorted(set((checkpoint.get("processed_object_keys") or []) + keys))
    checkpoint_out = {
        "processed_object_keys": new_processed_keys,
        "last_run_started_at": run_started_at,
        "last_run_completed_at": run_completed_at,
        "total_processed": int(len(keys)),
        "total_rejected": int(len(rejected)),
        "total_written": int(total_written),
    }
    _save_checkpoint(client, s.SILVER_BUCKET, s.SILVER_CHECKPOINT_KEY, checkpoint_out)
    _log.info("silver_etl_checkpoint_written key=%s processed_keys=%s", s.SILVER_CHECKPOINT_KEY, len(new_processed_keys))
    summary = {
        "discovered_objects": len(all_keys),
        "skipped_checkpointed_objects": skipped_checkpointed,
        "processed_new_objects": len(keys),
        "bronze_objects_scanned": len(keys),
        "deduped_events": deduped,
        "incident_rows": len(datasets["incident_events"]),
        "organization_rows": len(datasets["organization_events"]),
        "volunteer_rows": len(datasets["volunteer_events"]),
        "rejected_rows": len(rejected),
        "rejected_key": rejected_key,
        "written_keys": written,
        "checkpoint_written": s.SILVER_CHECKPOINT_KEY,
    }
    silver_processed_total.inc(float(len(keys)))
    silver_rejected_total.inc(float(len(rejected)))
    update_runtime_metric("silver_processed", int(len(keys)))
    update_runtime_metric("silver_rejected", int(len(rejected)))
    _log.info("silver_etl_run_summary %s", summary)
    emit_lineage_event(
        job_name="silver_etl",
        status="success",
        inputs=[f"s3://{s.SILVER_BUCKET}/{s.SILVER_BRONZE_PREFIX}/"],
        outputs=[
            f"s3://{s.SILVER_BUCKET}/{s.SILVER_PREFIX}/incident_events/",
            f"s3://{s.SILVER_BUCKET}/{s.SILVER_PREFIX}/organization_events/",
            f"s3://{s.SILVER_BUCKET}/{s.SILVER_PREFIX}/volunteer_events/",
        ],
        run_stats=summary,
    )
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
    run_once()


if __name__ == "__main__":
    main()
