# PulseGrid Data Platform - Phase 7 (Lightweight Observability)

Phase 7 adds production-style observability with Prometheus-compatible metrics and practical job counters, while staying local-dev friendly.

## Scope implemented

- Prometheus endpoint: `GET /metrics`
- FastAPI request metrics middleware
- Outbox health metrics (pending/published/failed + publish attempts)
- Data pipeline runtime metrics (Bronze/Silver/Gold counters)
- Analytics API error counters
- Shared runtime metrics snapshot for job->API visibility

## Metrics included

### API metrics
- `pulsegrid_api_requests_total{method,route,status_code}`
- `pulsegrid_api_request_latency_seconds{method,route}` (histogram)
- `pulsegrid_api_errors_total{method,route}`

### Outbox metrics
- `pulsegrid_outbox_pending_events` (gauge)
- `pulsegrid_outbox_published_events` (gauge)
- `pulsegrid_outbox_failed_events` (gauge)
- `pulsegrid_outbox_publish_attempts_total` (counter)

### Data jobs metrics
Counters:
- `pulsegrid_bronze_ingestor_written_total`
- `pulsegrid_bronze_ingestor_dead_letter_total`
- `pulsegrid_silver_processed_total`
- `pulsegrid_silver_rejected_total`
- `pulsegrid_gold_processed_total`
- `pulsegrid_gold_rejected_total`

Runtime gauges exposed via `/metrics`:
- `pulsegrid_bronze_runtime_written`
- `pulsegrid_bronze_runtime_dead_letter`
- `pulsegrid_silver_runtime_processed`
- `pulsegrid_silver_runtime_rejected`
- `pulsegrid_gold_runtime_processed`
- `pulsegrid_gold_runtime_rejected`

### Analytics API error metrics
- `pulsegrid_analytics_data_not_ready_total{endpoint}`
- `pulsegrid_analytics_query_failure_total{endpoint}`

## Implementation notes

- Metrics definitions live in `app/observability/metrics.py`.
- `/metrics` endpoint refreshes:
  - outbox DB gauges (best effort query)
  - job runtime gauges from local snapshot file:
    - `backend/data/metrics_runtime.json`
- Jobs update snapshot through `update_runtime_metric(...)`.
- This keeps implementation simple without needing a Pushgateway or multiprocess setup.

## Structured logging conventions

Use consistent event-style logs with key fields:
- event name first (for easy grep), then key/value context
- examples:
  - `bronze_event_written topic=... partition=... offset=... key=...`
  - `silver_etl_run_summary {...}`
  - `gold_etl_run_summary {...}`

## Local run instructions

1) Install dependencies:
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

2) Start backend:
```bash
cd backend
PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

3) Open metrics endpoint:
- [http://127.0.0.1:8002/metrics](http://127.0.0.1:8002/metrics)

4) Run jobs in separate terminals to update counters:
```bash
# outbox publisher
cd backend
PYTHONPATH=. python3 -m app.jobs.outbox_publisher

# bronze
PYTHONPATH=. python3 -m app.jobs.bronze_ingestor

# silver
PYTHONPATH=. python3 -m app.jobs.silver_etl

# gold
PYTHONPATH=. python3 -m app.jobs.gold_etl
```

5) Refresh `/metrics` and verify values change:
- request metrics increase after API calls
- outbox gauges reflect DB status
- runtime gauges reflect Bronze/Silver/Gold recent run totals

## Smoke-check guidance

- Call any API endpoint repeatedly and verify:
  - `pulsegrid_api_requests_total` increments
  - latency histogram buckets increase
- Trigger analytics endpoint errors intentionally (e.g. no Gold data):
  - verify `pulsegrid_analytics_data_not_ready_total` increments

