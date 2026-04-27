"""Phase 5 analytics serving CLI using analytics_service queries."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

QUERY_CATALOG: dict[str, str] = {
    "incident_operations_overview": """
        SELECT
          COUNT(*) AS incidents_total,
          AVG(time_to_assignment_seconds) FILTER (WHERE time_to_assignment_seconds IS NOT NULL) AS avg_time_to_assignment_seconds,
          AVG(time_to_completion_seconds) FILTER (WHERE time_to_completion_seconds IS NOT NULL) AS avg_time_to_completion_seconds
        FROM fact_incident_lifecycle
    """,
    "volunteer_performance_overview": """
        SELECT
          COUNT(*) AS volunteers_total,
          SUM(tasks_assigned) AS tasks_assigned_total,
          SUM(tasks_accepted) AS tasks_accepted_total,
          SUM(tasks_completed) AS tasks_completed_total,
          AVG(avg_completion_time_seconds) FILTER (WHERE avg_completion_time_seconds IS NOT NULL) AS avg_completion_time_seconds
        FROM fact_volunteer_performance
    """,
    "organization_capacity_overview": """
        WITH latest AS (
          SELECT *,
                 ROW_NUMBER() OVER (PARTITION BY organization_id ORDER BY captured_at DESC) AS rn
          FROM fact_org_capacity
        )
        SELECT
          COUNT(*) AS organizations_total,
          SUM(COALESCE(beds_available, 0)) AS beds_available_total,
          SUM(COALESCE(oxygen_units, 0)) AS oxygen_units_total,
          SUM(COALESCE(ambulances_available, 0)) AS ambulances_total
        FROM latest
        WHERE rn = 1
    """,
    "average_time_to_assignment": """
        SELECT AVG(time_to_assignment_seconds) AS avg_time_to_assignment_seconds
        FROM fact_incident_lifecycle
        WHERE time_to_assignment_seconds IS NOT NULL
    """,
    "average_time_to_completion": """
        SELECT AVG(time_to_completion_seconds) AS avg_time_to_completion_seconds
        FROM fact_incident_lifecycle
        WHERE time_to_completion_seconds IS NOT NULL
    """,
    "incidents_by_zone": """
        SELECT zone_id, COUNT(*) AS incidents
        FROM fact_incident_lifecycle
        GROUP BY zone_id
        ORDER BY incidents DESC, zone_id
    """,
    "tasks_completed_by_volunteer": """
        SELECT volunteer_id, tasks_completed
        FROM fact_volunteer_performance
        ORDER BY tasks_completed DESC, volunteer_id
    """,
    "latest_organization_capacity": """
        WITH latest AS (
          SELECT *,
                 ROW_NUMBER() OVER (PARTITION BY organization_id ORDER BY captured_at DESC) AS rn
          FROM fact_org_capacity
        )
        SELECT
          organization_id,
          captured_at,
          beds_available,
          oxygen_units,
          ambulances_available,
          shelter_units,
          food_capacity_units,
          rescue_units
        FROM latest
        WHERE rn = 1
        ORDER BY organization_id
    """,
}


def run_queries(_local_gold_root: Path, query_names: list[str]) -> dict[str, pd.DataFrame]:
    root = Path(_local_gold_root)
    conn = duckdb.connect(database=":memory:")
    conn.execute(
        f"CREATE OR REPLACE VIEW fact_incident_lifecycle AS SELECT * FROM read_parquet('{(root / 'gold' / 'fact_incident_lifecycle' / '**' / '*.parquet').as_posix()}')"
    )
    conn.execute(
        f"CREATE OR REPLACE VIEW fact_volunteer_performance AS SELECT * FROM read_parquet('{(root / 'gold' / 'fact_volunteer_performance' / '**' / '*.parquet').as_posix()}')"
    )
    conn.execute(
        f"CREATE OR REPLACE VIEW fact_org_capacity AS SELECT * FROM read_parquet('{(root / 'gold' / 'fact_org_capacity' / '**' / '*.parquet').as_posix()}')"
    )
    outputs: dict[str, pd.DataFrame] = {}
    for qn in query_names:
        outputs[qn] = conn.execute(QUERY_CATALOG[qn]).df()
    conn.close()
    return outputs


def _default_query_order() -> list[str]:
    return [
        "incident_operations_overview",
        "volunteer_performance_overview",
        "organization_capacity_overview",
        "average_time_to_assignment",
        "average_time_to_completion",
        "incidents_by_zone",
        "tasks_completed_by_volunteer",
        "latest_organization_capacity",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DuckDB analytics queries over Gold parquet.")
    parser.add_argument("--local-gold-root", default="backend/data/gold_cache", help="Local directory containing downloaded gold/")
    parser.add_argument("--skip-sync", action="store_true", help="Skip MinIO sync and use local files only.")
    parser.add_argument("--query", action="append", dest="queries", help="Query name to run (repeatable).")
    parser.add_argument("--export-csv-dir", default="", help="Optional directory to export query results as CSV.")
    args = parser.parse_args()

    local_root = Path(args.local_gold_root).resolve()
    # Local root is kept for backward CLI compatibility; sync behavior is handled in analytics_service.
    _ = local_root

    queries = args.queries or _default_query_order()
    unknown = [q for q in queries if q not in QUERY_CATALOG]
    if unknown:
        raise SystemExit(f"Unknown query names: {unknown}")

    results = run_queries(local_root, queries)
    export_dir = Path(args.export_csv_dir).resolve() if args.export_csv_dir else None
    if export_dir:
        export_dir.mkdir(parents=True, exist_ok=True)

    for name in queries:
        df = results[name]
        print(f"\n=== {name} ===")
        print(df.to_string(index=False) if not df.empty else "(no rows)")
        if export_dir:
            out = export_dir / f"{name}.csv"
            df.to_csv(out, index=False)
            print(f"exported_csv={out}")


if __name__ == "__main__":
    main()
