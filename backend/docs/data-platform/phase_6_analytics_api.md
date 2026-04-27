# PulseGrid Data Platform - Phase 6 (FastAPI Analytics API)

Phase 6 exposes Gold-mart metrics through FastAPI endpoints so Flutter and dashboard surfaces can consume analytics in JSON form.

## Scope implemented

- New analytics service module:
  - `app/services/analytics_service.py`
- New FastAPI routes:
  - `app/api/routes/analytics_routes.py`
- Typed response models:
  - `app/models/analytics_models.py`
- Main app wiring:
  - `app/main.py` includes `analytics_routes`

## Endpoints

- `GET /analytics/overview`
- `GET /analytics/incidents-by-zone`
- `GET /analytics/volunteer-performance`
- `GET /analytics/organization-capacity`
- `GET /analytics/time-to-response`

## Query parameters

Supported optional filters (where practical):
- `zone_id`
- `organization_id`
- `volunteer_id`
- `start_date`
- `end_date`

Notes:
- Incident-focused endpoints support zone/date filters.
- Organization endpoint supports organization/date filters.
- Volunteer endpoint supports volunteer filter.

## Error handling

If Gold files do not exist yet:
- service raises `AnalyticsDataNotReadyError`
- API returns `503` with actionable message:
  - run Gold ETL first (`python -m app.jobs.gold_etl`)

## Local cache + MinIO sync behavior

Analytics service uses:
- `ANALYTICS_LOCAL_GOLD_ROOT`
- `ANALYTICS_AUTO_SYNC`

When `ANALYTICS_AUTO_SYNC=true`, service syncs Gold parquet from MinIO to local cache before queries.

## Example responses

### `/analytics/overview`
```json
{
  "incident_operations": {
    "incidents_total": 42,
    "avg_time_to_assignment_seconds": 95.2,
    "avg_time_to_completion_seconds": 640.1
  },
  "volunteer_performance": {
    "volunteers_total": 18,
    "tasks_assigned_total": 74,
    "tasks_completed_total": 51
  },
  "organization_capacity": {
    "organizations_total": 6,
    "beds_available_total": 89
  }
}
```

### `/analytics/incidents-by-zone`
```json
[
  {"zone_id": "zone-central", "incidents": 21},
  {"zone_id": "zone-east", "incidents": 13}
]
```

### `/analytics/time-to-response`
```json
{
  "avg_time_to_assignment_seconds": 95.2,
  "avg_time_to_acceptance_seconds": 143.7,
  "avg_time_to_completion_seconds": 640.1
}
```

## Run locally

1) Ensure Gold marts exist:
```bash
cd backend
PYTHONPATH=. python3 -m app.jobs.gold_etl
```

2) Start API:
```bash
cd /Users/jinenmodi/PulseGrid/backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

3) Call endpoints from Swagger:
- `http://127.0.0.1:8002/docs`

## Flutter/dashboard integration guidance

- Flutter organization dashboard can call `/analytics/overview` for top KPI cards.
- Zone charts can consume `/analytics/incidents-by-zone`.
- Volunteer leaderboard widget can consume `/analytics/volunteer-performance`.
- Response-time trend cards can consume `/analytics/time-to-response` with date filters.

This keeps the frontend decoupled from raw Gold table shape and centralizes analytics SQL/logic in backend service code.

