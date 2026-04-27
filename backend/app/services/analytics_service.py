"""DuckDB-backed analytics service over Gold parquet marts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import threading
import time
from typing import Any

import boto3
import duckdb
import pandas as pd

from app.core.config import get_settings


class AnalyticsDataNotReadyError(RuntimeError):
    """Raised when Gold parquet datasets are not available yet."""


@dataclass
class AnalyticsFilters:
    zone_id: str | None = None
    organization_id: str | None = None
    volunteer_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None


_SYNC_LOCK = threading.Lock()
_LAST_SYNC_TS = 0.0


def _s3_client() -> Any:
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.BRONZE_S3_ENDPOINT_URL,
        aws_access_key_id=s.BRONZE_S3_ACCESS_KEY,
        aws_secret_access_key=s.BRONZE_S3_SECRET_KEY,
        region_name=s.BRONZE_S3_REGION,
        use_ssl=bool(s.BRONZE_S3_USE_SSL),
    )


def _download_gold_to_local(local_dir: Path) -> None:
    s = get_settings()
    client = _s3_client()
    local_dir.mkdir(parents=True, exist_ok=True)
    token = None
    prefix = f"{s.GOLD_PREFIX}/"
    while True:
        kwargs: dict[str, Any] = {"Bucket": s.GOLD_BUCKET, "Prefix": prefix, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        resp = client.list_objects_v2(**kwargs)
        for obj in resp.get("Contents") or []:
            key = str(obj.get("Key") or "")
            if not key.endswith(".parquet"):
                continue
            target = local_dir / key
            target.parent.mkdir(parents=True, exist_ok=True)
            client.download_file(s.GOLD_BUCKET, key, str(target))
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
        if not token:
            break


def _sync_gold_if_stale(local_dir: Path) -> None:
    global _LAST_SYNC_TS
    s = get_settings()
    min_seconds = max(0, int(getattr(s, "ANALYTICS_SYNC_MIN_SECONDS", 30)))
    now = time.time()
    if now - _LAST_SYNC_TS < float(min_seconds):
        return
    with _SYNC_LOCK:
        now = time.time()
        if now - _LAST_SYNC_TS < float(min_seconds):
            return
        _download_gold_to_local(local_dir)
        _LAST_SYNC_TS = time.time()


def _local_gold_root() -> Path:
    s = get_settings()
    root = Path(getattr(s, "ANALYTICS_LOCAL_GOLD_ROOT", "backend/data/gold_cache")).resolve()
    if bool(getattr(s, "ANALYTICS_AUTO_SYNC", True)):
        _sync_gold_if_stale(root)
    return root


def _dataset_glob(root: Path, dataset: str) -> str:
    return (root / "gold" / dataset / "**" / "*.parquet").as_posix()


def _ensure_gold_ready(root: Path) -> None:
    required = [
        root / "gold" / "fact_incident_lifecycle",
        root / "gold" / "fact_volunteer_performance",
        root / "gold" / "fact_org_capacity",
    ]
    for p in required:
        if not p.exists():
            raise AnalyticsDataNotReadyError(
                "Gold marts not found yet. Run gold ETL first (python -m app.jobs.gold_etl)."
            )


def _register_views(conn: duckdb.DuckDBPyConnection, root: Path) -> None:
    conn.execute(f"CREATE OR REPLACE VIEW fact_incident_lifecycle AS SELECT * FROM read_parquet('{_dataset_glob(root, 'fact_incident_lifecycle')}')")
    conn.execute(
        f"CREATE OR REPLACE VIEW fact_volunteer_performance AS SELECT * FROM read_parquet('{_dataset_glob(root, 'fact_volunteer_performance')}')"
    )
    conn.execute(f"CREATE OR REPLACE VIEW fact_org_capacity AS SELECT * FROM read_parquet('{_dataset_glob(root, 'fact_org_capacity')}')")
    dim_glob = _dataset_glob(root, "dim_time")
    if (root / "gold" / "dim_time").exists():
        conn.execute(f"CREATE OR REPLACE VIEW dim_time AS SELECT * FROM read_parquet('{dim_glob}')")


def _normalize_df_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    out: list[dict[str, Any]] = []
    for r in df.to_dict(orient="records"):
        clean: dict[str, Any] = {}
        for k, v in r.items():
            if pd.isna(v):
                clean[k] = None
            elif hasattr(v, "item"):
                try:
                    clean[k] = v.item()
                except Exception:  # noqa: BLE001
                    clean[k] = v
            else:
                clean[k] = v
        out.append(clean)
    return out


def _incident_where(filters: AnalyticsFilters) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if filters.zone_id:
        clauses.append("zone_id = ?")
        params.append(filters.zone_id)
    if filters.start_date:
        clauses.append("created_at >= ?")
        params.append(filters.start_date)
    if filters.end_date:
        clauses.append("created_at <= ?")
        params.append(filters.end_date)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


def query_overview(filters: AnalyticsFilters) -> dict[str, Any]:
    root = _local_gold_root()
    _ensure_gold_ready(root)
    conn = duckdb.connect(database=":memory:")
    _register_views(conn, root)
    incident_where, params = _incident_where(filters)

    incident_sql = f"""
      SELECT
        COUNT(*) AS incidents_total,
        AVG(time_to_assignment_seconds) FILTER (WHERE time_to_assignment_seconds IS NOT NULL) AS avg_time_to_assignment_seconds,
        AVG(time_to_completion_seconds) FILTER (WHERE time_to_completion_seconds IS NOT NULL) AS avg_time_to_completion_seconds
      FROM fact_incident_lifecycle
      {incident_where}
    """
    vol_sql = "SELECT COUNT(*) AS volunteers_total, SUM(tasks_assigned) AS tasks_assigned_total, SUM(tasks_completed) AS tasks_completed_total FROM fact_volunteer_performance"
    org_sql = """
      WITH latest AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY organization_id ORDER BY captured_at DESC) AS rn
        FROM fact_org_capacity
      )
      SELECT COUNT(*) AS organizations_total, SUM(COALESCE(beds_available,0)) AS beds_available_total
      FROM latest WHERE rn = 1
    """

    incident = _normalize_df_records(conn.execute(incident_sql, params).df())
    volunteer = _normalize_df_records(conn.execute(vol_sql).df())
    organization = _normalize_df_records(conn.execute(org_sql).df())
    conn.close()
    return {
        "incident_operations": incident[0] if incident else {},
        "volunteer_performance": volunteer[0] if volunteer else {},
        "organization_capacity": organization[0] if organization else {},
    }


def query_incidents_by_zone(filters: AnalyticsFilters) -> list[dict[str, Any]]:
    root = _local_gold_root()
    _ensure_gold_ready(root)
    conn = duckdb.connect(database=":memory:")
    _register_views(conn, root)
    where, params = _incident_where(filters)
    sql = f"""
      SELECT zone_id, COUNT(*) AS incidents
      FROM fact_incident_lifecycle
      {where}
      GROUP BY zone_id
      ORDER BY incidents DESC, zone_id
    """
    out = _normalize_df_records(conn.execute(sql, params).df())
    conn.close()
    return out


def query_volunteer_performance(filters: AnalyticsFilters) -> list[dict[str, Any]]:
    root = _local_gold_root()
    _ensure_gold_ready(root)
    conn = duckdb.connect(database=":memory:")
    _register_views(conn, root)
    clauses: list[str] = []
    params: list[Any] = []
    if filters.volunteer_id:
        clauses.append("volunteer_id = ?")
        params.append(filters.volunteer_id)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
      SELECT volunteer_id, tasks_assigned, tasks_accepted, tasks_completed, latest_credits, latest_trust_score, avg_completion_time_seconds
      FROM fact_volunteer_performance
      {where}
      ORDER BY tasks_completed DESC, volunteer_id
    """
    out = _normalize_df_records(conn.execute(sql, params).df())
    conn.close()
    return out


def query_organization_capacity(filters: AnalyticsFilters) -> list[dict[str, Any]]:
    root = _local_gold_root()
    _ensure_gold_ready(root)
    conn = duckdb.connect(database=":memory:")
    _register_views(conn, root)
    clauses: list[str] = []
    params: list[Any] = []
    if filters.organization_id:
        clauses.append("organization_id = ?")
        params.append(filters.organization_id)
    if filters.start_date:
        clauses.append("captured_at >= ?")
        params.append(filters.start_date)
    if filters.end_date:
        clauses.append("captured_at <= ?")
        params.append(filters.end_date)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
      WITH latest AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY organization_id ORDER BY captured_at DESC) AS rn
        FROM fact_org_capacity
        {where}
      )
      SELECT organization_id, captured_at, beds_available, oxygen_units, ambulances_available, shelter_units, food_capacity_units, rescue_units
      FROM latest WHERE rn = 1
      ORDER BY organization_id
    """
    out = _normalize_df_records(conn.execute(sql, params).df())
    conn.close()
    return out


def query_time_to_response(filters: AnalyticsFilters) -> dict[str, Any]:
    root = _local_gold_root()
    _ensure_gold_ready(root)
    conn = duckdb.connect(database=":memory:")
    _register_views(conn, root)
    where, params = _incident_where(filters)
    sql = f"""
      SELECT
        AVG(time_to_assignment_seconds) FILTER (WHERE time_to_assignment_seconds IS NOT NULL) AS avg_time_to_assignment_seconds,
        AVG(time_to_acceptance_seconds) FILTER (WHERE time_to_acceptance_seconds IS NOT NULL) AS avg_time_to_acceptance_seconds,
        AVG(time_to_completion_seconds) FILTER (WHERE time_to_completion_seconds IS NOT NULL) AS avg_time_to_completion_seconds
      FROM fact_incident_lifecycle
      {where}
    """
    out = _normalize_df_records(conn.execute(sql, params).df())
    conn.close()
    return out[0] if out else {}
