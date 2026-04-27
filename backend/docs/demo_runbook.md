# PulseGrid Local Demo Runbook

This runbook provides a repeatable local walkthrough that exercises the full stack:

`FastAPI -> PostgreSQL outbox -> Redpanda/Kafka -> Bronze -> Silver -> Gold -> Analytics API -> /metrics`

## One-command demo

From repo root:

```bash
make demo
```

This executes `backend/scripts/demo_orchestrator.py` and prints PASS/FAIL for each stage.

## What the demo orchestrator does

1. `docker compose up -d` (Redpanda + MinIO)
2. `alembic upgrade head`
3. starts backend (if not already running)
4. idempotent auth setup:
   - victim register-or-login
   - volunteer register-or-login
   - organization register-or-login
5. creates sample incidents (victim flow)
6. triggers organization capacity update
7. runs outbox publish once (`run_once`)
8. runs bronze ingestion once (`run_once`)
9. runs Silver ETL
10. runs Gold ETL
11. calls analytics endpoints
12. checks `/metrics` for required markers

## Expected terminal output

You should see lines like:

- `[PASS] docker_compose_up - ...`
- `[PASS] alembic_upgrade - ...`
- `[PASS] create_incidents - 2 incidents created`
- `[PASS] analytics_api - Core analytics endpoints returned 200`
- `[PASS] metrics_endpoint - /metrics includes core markers`

Final line:

`Demo complete: X/Y steps passed.`

## Useful Makefile targets

Start backend manually:

```bash
make demo-backend
```

Run publisher worker manually:

```bash
make demo-jobs
```

Quick metrics marker check:

```bash
make demo-metrics
```

## Idempotency notes

- Auth seed is register-or-login; reruns reuse same demo accounts.
- Migrations are safe to rerun at head.
- Demo incidents are additive; reruns create new incident events by design.
- Bronze writes are event-id idempotent.

## Troubleshooting

### 1) Demo fails at backend health
- Ensure no conflicting server on `8002`.
- Start manually with `make demo-backend`.
- Verify `GET http://127.0.0.1:8002/health`.

### 2) Analytics endpoints return 503
- Gold may not be ready yet.
- Run:
  - `PYTHONPATH=. python3 -m app.jobs.silver_etl`
  - `PYTHONPATH=. python3 -m app.jobs.gold_etl`

### 3) /metrics missing pipeline gauges
- Run Bronze/Silver/Gold jobs at least once.
- `/metrics` reads runtime counters from:
  - `backend/data/metrics_runtime.json`

### 4) Kafka/MinIO connectivity errors
- Check infra:
  - `docker compose ps`
- Ensure env values are correct:
  - `KAFKA_BOOTSTRAP_SERVERS=localhost:19092`
  - `BRONZE_S3_ENDPOINT_URL=http://localhost:9000`

