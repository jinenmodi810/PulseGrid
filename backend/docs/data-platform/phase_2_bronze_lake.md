# PulseGrid Data Platform - Phase 2 (Bronze Lake Ingestion)

Phase 2 adds a local Bronze layer using MinIO (S3-compatible) and a Kafka consumer that stores full raw event envelopes.
Phase 2.1 adds reliability hardening (dead-letter routing, gzip, health checks, and richer counters).

## Scope implemented

- Added MinIO to `docker-compose.yml`.
- Added `minio-init` bootstrap step to ensure bucket and domain prefixes exist.
- Added Bronze consumer job: `app/jobs/bronze_ingestor.py`.
- Added config/env fields for Bronze ingestion.
- Added unit tests for key path partitioning.

No Silver/Gold, Flink/Spark, dbt, or orchestration is introduced in this phase.

## Local storage layout

Bucket:
- `pulsegrid-bronze`

Logical roots:
- `pulsegrid-bronze/events/incident/`
- `pulsegrid-bronze/events/organization/`
- `pulsegrid-bronze/events/volunteer/`

Object key partitioning:
- `event_type=<event_type>`
- `year=<YYYY>/month=<MM>/day=<DD>/hour=<HH>`

Example keys:
- `events/incident/event_type=incident.created/year=2026/month=04/day=25/hour=03/38cd59cf-e075-4544-922e-9fb93a71cc71.json`
- `events/organization/event_type=organization.capacity_updated/year=2026/month=04/day=25/hour=03/ae21....json`
- `events/volunteer/event_type=volunteer.task_completed/year=2026/month=04/day=25/hour=03/9f41....json`

## Idempotency approach

- Deterministic object key uses `event_id`.
- Before writing, consumer checks `head_object`.
- If object already exists, event is skipped (no duplicate file write).

This is practical idempotency for local Bronze and works well with replayed Kafka offsets.

## Monitoring logs

Consumer emits:
- per-write success logs (topic/partition/offset/object key)
- write failure logs with error snippet
- rolling stats: `consumed`, `written`, `skipped_duplicate`, `failed`, `dead_letter_written`

## Phase 2.1 hardening

### Dead-letter routing

Invalid records are written to:
- `events/_dead_letter/year=<YYYY>/month=<MM>/day=<DD>/hour=<HH>/<generated_id>.json`
- if gzip is enabled: same path with `.json.gz`

Invalid categories routed to dead-letter:
- malformed JSON
- missing `event_id`
- missing `event_type`
- invalid/unexpected envelope shape (e.g., missing `payload`)

Dead-letter object includes:
- `error_type`
- `error_message`
- `raw_value` (safe serialized form)
- `topic`
- `partition`
- `offset`
- `captured_at`

### Optional gzip output

Env toggle:
- `BRONZE_GZIP_ENABLED=true|false`

Behavior:
- `false` -> writes `.json`
- `true` -> writes `.json.gz`

## Configuration

Add in `backend/.env` (or use defaults from `.env.example`):

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:19092
BRONZE_KAFKA_CONSUMER_GROUP=pulsegrid-bronze-consumer
BRONZE_KAFKA_TOPICS=pulsegrid.incident.events,pulsegrid.organization.events,pulsegrid.volunteer.events
BRONZE_BUCKET=pulsegrid-bronze
BRONZE_PREFIX=events
BRONZE_S3_ENDPOINT_URL=http://localhost:9000
BRONZE_S3_ACCESS_KEY=minioadmin
BRONZE_S3_SECRET_KEY=minioadmin
BRONZE_S3_REGION=us-east-1
BRONZE_S3_USE_SSL=false
BRONZE_POLL_TIMEOUT_MS=1000
BRONZE_GZIP_ENABLED=false
```

## Run locally

1) Start infra:
```bash
docker compose up -d
```

2) Ensure backend deps:
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

3) Run API + outbox publisher (Phase 1 flow), produce events.

4) Run Bronze ingestor:
```bash
cd backend
PYTHONPATH=. python3 -m app.jobs.bronze_ingestor
```

5) Open MinIO Console:
- [http://localhost:9001](http://localhost:9001)
- user/pass: `minioadmin` / `minioadmin`

6) Verify files under `pulsegrid-bronze/events/...`.

7) Optional health check:
```bash
cd backend
PYTHONPATH=. python3 scripts/bronze_health_check.py
```

Health check prints:
- bucket availability
- configured topics / bucket / prefix
- raw object count (practical estimate)
- dead-letter object count

## Quick test commands

Run unit tests:
```bash
source venv/bin/activate
PYTHONPATH=backend python3 -m unittest backend.tests.test_bronze_ingestor_phase2
```

Run Phase 2.1 tests:
```bash
source venv/bin/activate
PYTHONPATH=backend python3 -m unittest backend.tests.test_bronze_ingestor_phase2
```

