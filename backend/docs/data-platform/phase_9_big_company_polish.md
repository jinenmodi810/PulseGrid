# Phase 9: Big-Company Polish

This phase adds five enterprise-style capabilities while keeping the existing startup-practical architecture stable.

## 1) Schema Registry (Avro Contracts)

- Avro schemas are stored in `app/domain/avro_schemas/*.avsc`.
- Schema Registry is exposed via Redpanda on `http://localhost:18081`.
- Registration script:

```bash
cd backend
python scripts/schema_registry_sync.py --registry-url http://localhost:18081
```

- Local contract validation:

```bash
python scripts/validate_avro_contracts.py --file /path/to/event.json
```

## 2) Orchestration (Dagster)

- Definitions file: `orchestration/dagster_defs.py`
- Pipelines:
  - `pulsegrid_hourly_pipeline`: outbox -> bronze -> silver -> gold
  - `pulsegrid_backfill_pipeline`: Silver full refresh + Gold rebuild

Run:

```bash
cd backend
dagster dev -f orchestration/dagster_defs.py
```

## 3) dbt Semantic/Metric Layer

- dbt project: `dbt_project/`
- Staging + metric models:
  - `models/staging/stg_gold_incident_lifecycle.sql`
  - `models/marts/metrics_incident_response.sql`
- Tests in `models/schema.yml`

Run:

```bash
cd backend/dbt_project
cp profiles.yml.example ~/.dbt/profiles.yml
dbt run
dbt test
```

## 4) Lineage/Catalog

- ETL jobs emit lineage to `backend/data/lineage/events.jsonl`.
- Catalog build script:

```bash
cd backend
python scripts/build_data_catalog.py
```

- Output: `docs/data-platform/data_catalog.md`

## 5) Performance Benchmark Report

- Benchmark script: `scripts/benchmark_platform.py`
- Generates report: `docs/data-platform/performance_benchmark_report.md`

Run:

```bash
cd backend
python scripts/benchmark_platform.py --base-url http://127.0.0.1:8002 --samples 20
```

## Integration Notes

- No existing API behavior is changed.
- Bronze/Silver/Gold jobs remain runnable standalone.
- New features are additive and can be adopted incrementally.
