# Topic Design (Phase 1)

## Topic taxonomy

- `pulsegrid.incident.events`
  - `incident.created`
  - `incident.assigned`
  - `incident.accepted`
  - `incident.completed`

- `pulsegrid.organization.events`
  - `organization.capacity_updated`

- `pulsegrid.volunteer.events`
  - `volunteer.task_completed`

- `pulsegrid.audit.events` (reserved)
  - Intended for security/audit actions, not yet produced.

## Partition key strategy

- Incident domain -> `incident_id`
- Organization domain -> `organization_id`
- Volunteer domain -> `volunteer_id`

Rationale:
- Preserves strict ordering per key entity.
- Enables deterministic lifecycle reconstruction.
- Balances partitions by primary entity cardinality.

## Backward compatibility

Set:
`KAFKA_TOPIC_ROUTING_ENABLED=false`

When disabled, all events publish to:
`KAFKA_OUTBOX_TOPIC` (default `pulsegrid.domain.events`).

## Recommended local Redpanda topic retention

For development:
- Incident topic: 7 days
- Organization topic: 14 days
- Volunteer topic: 14 days
- Audit topic: 30 days

In production, tune by:
- downstream replay requirements
- storage budget
- compliance retention policies

