# PulseGrid Data Platform - Phase 5 (Analytics Serving with DuckDB)

Phase 5 adds a lightweight local analytics serving layer over Gold marts using DuckDB.

## Scope implemented

- DuckDB analytics script: `scripts/analytics_duckdb.py`
- Reusable SQL query catalog for core operations and dashboard-ready KPIs
- Optional CSV export for BI/data-viz tooling ingestion
- Tests for query catalog and sample output DataFrames

No Superset/Metabase deployment is introduced in this phase.

## Data source

Gold parquet datasets:
- `gold/fact_incident_lifecycle/`
- `gold/fact_volunteer_performance/`
- `gold/fact_org_capacity/`
- `gold/dim_time/`

Script syncs parquet from MinIO to local cache (or can run against local cache only).

## Reusable analytics queries

Views read from parquet and support:

1. incident operations overview
2. volunteer performance overview
3. organization capacity overview
4. average time to assignment
5. average time to completion
6. incidents by zone
7. tasks completed by volunteer
8. latest organization capacity

## Run locally

1) Install dependencies:
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

2) Run all analytics queries with MinIO sync:
```bash
cd backend
PYTHONPATH=. python3 scripts/analytics_duckdb.py
```

3) Run locally without sync (already cached parquet):
```bash
PYTHONPATH=. python3 scripts/analytics_duckdb.py --skip-sync --local-gold-root backend/data/gold_cache
```

4) Run specific queries:
```bash
PYTHONPATH=. python3 scripts/analytics_duckdb.py --query incidents_by_zone --query latest_organization_capacity
```

5) Export outputs to CSV:
```bash
PYTHONPATH=. python3 scripts/analytics_duckdb.py --export-csv-dir backend/data/analytics_exports
```

## Output behavior

- prints query results to console (demo-friendly)
- optional CSV exports:
  - `average_time_to_assignment.csv`
  - `average_time_to_completion.csv`
  - `incidents_by_zone.csv`
  - `tasks_completed_by_volunteer.csv`
  - `latest_organization_capacity.csv`
  - plus overview query exports

## Why this supports future Superset/Metabase

- Query logic is centralized and reusable.
- Gold marts are already denormalized and KPI-ready.
- CSV export provides immediate compatibility for lightweight dashboard demos.
- Next step can swap DuckDB in-memory execution for:
  - DuckDB persistent DB file with saved views, or
  - direct BI connector over warehouse/Lakehouse once introduced.

