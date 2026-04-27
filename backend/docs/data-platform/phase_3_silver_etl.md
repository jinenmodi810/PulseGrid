# PulseGrid Data Platform - Phase 3 (Silver ETL)

Phase 3 introduces a practical Python micro-batch ETL that reads immutable Bronze events from MinIO, validates/normalizes them, deduplicates by `event_id`, and writes query-ready Silver Parquet outputs.
Phase 3.1 adds incremental checkpointing so runs process only new Bronze objects and are restart-safe.

## Scope implemented

- New ETL job: `app/jobs/silver_etl.py`
- New health script: `scripts/silver_health_check.py`
- Rejection handling for invalid envelopes -> `silver/_rejected/`
- Silver outputs as Parquet:
  - `silver/incident_events/`
  - `silver/organization_events/`
  - `silver/volunteer_events/`
- Partitioning:
  - `event_type=<event_type>/year=<YYYY>/month=<MM>/day=<DD>/`

No Spark/Flink/dbt/Airflow/Silver streaming framework is introduced in this phase.

## Envelope validation

Required fields:
- `event_id`
- `event_type`
- `aggregate_type`
- `aggregate_id`
- `schema_version`
- `event_version`
- `enqueued_at`
- `payload`

Invalid envelopes are written to:
- `silver/_rejected/year=<YYYY>/month=<MM>/day=<DD>/batch_<ts>.json`

Each rejected record includes:
- `reason`
- `source_key` (original Bronze object key)
- `captured_at`

## Normalization

All timestamps are normalized to UTC ISO (`...Z`).

### Incident silver columns
- event fields: `event_id`, `event_type`, `aggregate_type`, `aggregate_id`, `schema_version`, `event_version`, `enqueued_at`
- payload flattening:
  - `incident_id`
  - `zone_id`
  - `status`
  - `priority_label`
  - `reporter_user_id`
  - `volunteer_id`
  - `organization_id`
  - `occurred_at`
- `payload_json` (full payload string for fidelity)

### Organization silver columns
- event fields (same)
- payload flattening:
  - `organization_id`
  - `updated_fields_json`
  - `occurred_at`
- `payload_json`

### Volunteer silver columns
- event fields (same)
- payload flattening:
  - `volunteer_id`
  - `incident_id`
  - `credits`
  - `trust_score`
  - `occurred_at`
- `payload_json`

## Deduplication

Deduplication is done by `event_id` within each run.
If the same `event_id` appears multiple times in scanned Bronze files, only first occurrence is written.

## Phase 3.1 Incremental Checkpointing

Checkpoint object:
- `silver/_checkpoints/bronze_to_silver_checkpoint.json`

Checkpoint fields:
- `processed_object_keys`
- `last_run_started_at`
- `last_run_completed_at`
- `total_processed`
- `total_rejected`
- `total_written`

Behavior:
- default run: skips Bronze object keys already in checkpoint
- new objects only are processed
- `SILVER_FULL_REFRESH=true` ignores checkpoint and scans all Bronze objects
- checkpoint is written after run completion with updated processed keys and totals

Operational logs:
- `discovered_objects`
- `skipped_checkpointed_objects`
- `processed_new_objects`
- `checkpoint_written`

## Configuration

In `backend/.env`:

```bash
SILVER_BUCKET=pulsegrid-bronze
SILVER_BRONZE_PREFIX=events
SILVER_PREFIX=silver
SILVER_REJECTED_PREFIX=silver/_rejected
SILVER_CHECKPOINT_KEY=silver/_checkpoints/bronze_to_silver_checkpoint.json
SILVER_FULL_REFRESH=false
```

S3/MinIO connection reuses Bronze settings:
- `BRONZE_S3_ENDPOINT_URL`
- `BRONZE_S3_ACCESS_KEY`
- `BRONZE_S3_SECRET_KEY`
- `BRONZE_S3_REGION`
- `BRONZE_S3_USE_SSL`

## Run locally

1) Start local infra and generate Bronze events:
```bash
docker compose up -d
```

2) Install deps:
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

3) Run Silver ETL (single micro-batch pass):
```bash
cd backend
PYTHONPATH=. python3 -m app.jobs.silver_etl
```

4) Run Silver health check:
```bash
PYTHONPATH=. python3 scripts/silver_health_check.py
```

5) Force full refresh when needed:
```bash
SILVER_FULL_REFRESH=true PYTHONPATH=. python3 -m app.jobs.silver_etl
```

## Sample output paths

- `silver/incident_events/event_type=incident.created/year=2026/month=04/day=25/batch_20260425T040102Z.parquet`
- `silver/organization_events/event_type=organization.capacity_updated/year=2026/month=04/day=25/batch_20260425T040102Z.parquet`
- `silver/volunteer_events/event_type=volunteer.task_completed/year=2026/month=04/day=25/batch_20260425T040102Z.parquet`
- `silver/_rejected/year=2026/month=04/day=25/batch_20260425T040102Z.json`
- `silver/_checkpoints/bronze_to_silver_checkpoint.json`

## How this prepares for Gold marts and BI

Phase 3 creates stable, typed, deduped, and partitioned datasets that are ready for downstream analytics:
- Gold marts can aggregate incident lifecycle and responder performance from consistent Silver schemas.
- BI dashboards can query Silver directly for near-term visibility and migrate to Gold as business logic expands.
- Rejected tracking provides a quality boundary before dimensional modeling.

