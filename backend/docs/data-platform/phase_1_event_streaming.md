# PulseGrid Data Platform - Phase 1 (Event Streaming Foundation)

## Current State Audit

### What existed before Phase 1
- Transactional outbox persisted in PostgreSQL table `event_outbox`.
- Outbox publisher worker `app.jobs.outbox_publisher` published to one topic (`KAFKA_OUTBOX_TOPIC`, default `pulsegrid.domain.events`).
- Event envelope included `event_id`, `event_type`, `aggregate_type`, `aggregate_id`, `schema_version`, `enqueued_at`, `payload`.
- No schema contract validation before publish.
- Partition key was coarse (`aggregate_type:aggregate_id`), not domain-optimized.

### Existing event types (verified from code)
- `incident.created`
- `incident.assigned`
- `incident.accepted`
- `incident.completed`
- `organization.capacity_updated`
- `volunteer.task_completed`

## Phase Plan (High-level Roadmap)

### Phase 1 (implemented now)
- Topic taxonomy and routing strategy.
- JSON Schema contracts per event type.
- Envelope versioning (`event_version`, `schema_version`).
- Validation gate before publish.
- Partition keys aligned with primary analytical entities.
- Documentation + tests.

### Phase 2
- Introduce Schema Registry (Avro/Protobuf) and compatibility rules.
- Publish schema IDs in message headers.
- Add producer retries/backoff metrics and DLQ topic.

### Phase 3
- Streaming ETL (Flink/Spark Structured Streaming) to Bronze and Silver tables.
- Late-event handling/watermark strategy.

### Phase 4
- Lakehouse + medallion model and dbt analytics marts.
- Orchestration + DQ + lineage.

## Phase 1 Design Decisions

### Topic strategy
- `pulsegrid.incident.events`
- `pulsegrid.organization.events`
- `pulsegrid.volunteer.events`
- `pulsegrid.audit.events` (reserved for non-domain audit trails)

### Partition strategy
- Incident events partition key -> `incident_id`
- Organization events partition key -> `organization_id`
- Volunteer events partition key -> `volunteer_id`

Tradeoffs:
- Preserves ordering per entity (strong for lifecycle reconstruction).
- Avoids hotspotting by broad entity distribution.
- Cross-entity joins still happen downstream (warehouse/lakehouse), not via partition co-location.

### Backward compatibility
- Existing single-topic mode preserved via `KAFKA_TOPIC_ROUTING_ENABLED=false`.
- Fallback topic remains `KAFKA_OUTBOX_TOPIC`.

## Files added/updated in Phase 1
- `app/domain/event_streaming.py`
- `app/domain/event_contracts/*.schema.json`
- `app/jobs/outbox_publisher.py`
- `app/services/outbox_service.py`
- `app/services/organization_service.py` (adds `organization_id` in capacity payload)
- `app/core/config.py`
- `requirements.txt` (`jsonschema`)
- `tests/test_event_streaming_phase1.py`
- `scripts/validate_event_contracts.py`
- `docs/data-platform/event_contracts.md`
- `docs/data-platform/topic_design.md`

