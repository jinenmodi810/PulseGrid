# Event Contracts (Phase 1)

Phase 1 uses JSON Schema contracts per event type. Contracts validate the full publish envelope.

Contract location:
- `app/domain/event_contracts/incident.created.schema.json`
- `app/domain/event_contracts/incident.assigned.schema.json`
- `app/domain/event_contracts/incident.accepted.schema.json`
- `app/domain/event_contracts/incident.completed.schema.json`
- `app/domain/event_contracts/organization.capacity_updated.schema.json`
- `app/domain/event_contracts/volunteer.task_completed.schema.json`

## Common envelope fields
- `event_id` (string UUID)
- `event_type` (domain event string)
- `event_version` (integer, per event semantic version)
- `schema_version` (integer, schema contract generation)
- `aggregate_type` (`incident`, `organization`, `volunteer`)
- `aggregate_id` (entity id string)
- `enqueued_at` (ISO timestamp string)
- `payload` (event-specific object)

## Example valid event
```json
{
  "event_id": "38cd59cf-e075-4544-922e-9fb93a71cc71",
  "event_type": "incident.created",
  "event_version": 1,
  "schema_version": 1,
  "aggregate_type": "incident",
  "aggregate_id": "c3349ab7-1a23-43b1-a372-655cc17df3ad",
  "enqueued_at": "2026-04-25T03:06:16.207Z",
  "payload": {
    "incident_id": "c3349ab7-1a23-43b1-a372-655cc17df3ad",
    "zone_id": "zone-central",
    "status": "open",
    "priority_label": "CRITICAL",
    "reporter_user_id": "victim-user-123",
    "occurred_at": "2026-04-25T03:06:16Z",
    "rejection_count": 0
  }
}
```

## Example invalid event
Invalid because `incident_id` is missing from payload:
```json
{
  "event_id": "x",
  "event_type": "incident.created",
  "event_version": 1,
  "schema_version": 1,
  "aggregate_type": "incident",
  "aggregate_id": "abc",
  "enqueued_at": "2026-04-25T03:06:16.207Z",
  "payload": {
    "zone_id": "zone-central",
    "status": "open",
    "priority_label": "CRITICAL",
    "reporter_user_id": "victim-user-123",
    "occurred_at": "2026-04-25T03:06:16Z",
    "rejection_count": 0
  }
}
```

Publisher behavior for invalid messages:
- marks attempt count up
- stores `last_error` with `validation_failed: ...`
- eventually sets status to `failed` after max attempts
- logs `outbox_event_validation_failed`

