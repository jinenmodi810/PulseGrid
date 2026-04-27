# PulseGrid Data Platform - Phase 4 (Gold Marts & Star Schema)

Phase 4 builds business-ready Gold marts from Silver Parquet datasets using a startup-practical Python batch transformation.

## Scope implemented

- Gold ETL job: `app/jobs/gold_etl.py`
- Gold health check: `scripts/gold_health_check.py`
- Fact outputs:
  - `gold/fact_incident_lifecycle/`
  - `gold/fact_volunteer_performance/`
  - `gold/fact_org_capacity/`
- Dimension output:
  - `gold/dim_time/`
- Rejected records:
  - `gold/_rejected/`

No Spark/Flink/Airflow/dbt/BI orchestration is introduced in this phase.

## Source inputs

Silver datasets read from MinIO:
- `silver/incident_events/*.parquet`
- `silver/organization_events/*.parquet`
- `silver/volunteer_events/*.parquet`

## Gold outputs

### fact_incident_lifecycle
Fields:
- `incident_id`
- `created_at`
- `assigned_at`
- `accepted_at`
- `completed_at`
- `time_to_assignment_seconds`
- `time_to_acceptance_seconds`
- `time_to_completion_seconds`
- `zone_id`
- `priority_label`
- `assigned_volunteer_id`
- `assigned_organization_id`
- `final_status`

Lifecycle derived from event types:
- `incident.created`
- `incident.assigned`
- `incident.accepted`
- `incident.completed`

### fact_volunteer_performance
Fields:
- `volunteer_id`
- `tasks_assigned`
- `tasks_accepted`
- `tasks_completed`
- `latest_credits`
- `latest_trust_score`
- `avg_completion_time_seconds` (from lifecycle where available)

### fact_org_capacity
Fields:
- `organization_id`
- `captured_at`
- `beds_available`
- `oxygen_units`
- `ambulances_available`
- `shelter_units`
- `food_capacity_units`
- `rescue_units`

### dim_time
Fields:
- `date_key`
- `date`
- `year`
- `month`
- `day`
- `hour`

## Partition strategy

Gold Parquet outputs are written under:
- `gold/<dataset>/year=<YYYY>/month=<MM>/day=<DD>/batch_<ts>.parquet`

When `event_type` exists in output schema, partition includes event_type:
- `gold/<dataset>/event_type=<event_type>/year=<YYYY>/month=<MM>/day=<DD>/batch_<ts>.parquet`

## Data quality checks

Implemented quality filters:
- `incident_id` required in `fact_incident_lifecycle`
- `volunteer_id` required in `fact_volunteer_performance`
- `organization_id` required in `fact_org_capacity`
- negative lifecycle durations rejected

Rejected records are written to:
- `gold/_rejected/year=<YYYY>/month=<MM>/day=<DD>/batch_<ts>.json`

## Local configuration

In `backend/.env`:

```bash
GOLD_BUCKET=pulsegrid-bronze
GOLD_PREFIX=gold
GOLD_REJECTED_PREFIX=gold/_rejected
```

S3/MinIO connection reuses Bronze settings.

## Run locally

1) Ensure local infra and Silver outputs exist:
```bash
docker compose up -d
```

2) Install dependencies:
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

3) Run Gold ETL:
```bash
cd backend
PYTHONPATH=. python3 -m app.jobs.gold_etl
```

4) Run health check:
```bash
PYTHONPATH=. python3 scripts/gold_health_check.py
```

## Sample output paths

- `gold/fact_incident_lifecycle/year=2026/month=04/day=25/batch_20260425T050102Z.parquet`
- `gold/fact_volunteer_performance/year=2026/month=04/day=25/batch_20260425T050102Z.parquet`
- `gold/fact_org_capacity/year=2026/month=04/day=25/batch_20260425T050102Z.parquet`
- `gold/dim_time/year=2026/month=04/day=25/batch_20260425T050102Z.parquet`
- `gold/_rejected/year=2026/month=04/day=25/batch_20260425T050102Z.json`

## Why this is analytics-ready

This phase creates stable, denormalized marts aligned with operational KPIs:
- incident lifecycle SLA metrics
- volunteer effectiveness metrics
- organization capacity trends
- reusable time dimension for rollups

These Gold marts provide direct foundations for BI dashboards and later dbt semantic modeling.

