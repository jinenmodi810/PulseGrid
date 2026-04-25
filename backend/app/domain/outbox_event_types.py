"""Canonical domain event type strings (outbox + Kafka/Redpanda)."""

# --- Incidents (runtime in Neo4j; events are durable signals for analytics / consumers) ---

INCIDENT_CREATED = "incident.created"
INCIDENT_ASSIGNED = "incident.assigned"
INCIDENT_ACCEPTED = "incident.accepted"
INCIDENT_COMPLETED = "incident.completed"

# --- Organization (PostgreSQL canonical for capacity) ---

ORGANIZATION_CAPACITY_UPDATED = "organization.capacity_updated"

# --- Volunteer (PostgreSQL canonical for credits/trust) ---

VOLUNTEER_TASK_COMPLETED = "volunteer.task_completed"

# Aggregate type constants (string tags for consumers)
AGG_INCIDENT = "incident"
AGG_ORGANIZATION = "organization"
AGG_VOLUNTEER = "volunteer"

# Outbox status
STATUS_PENDING = "pending"
STATUS_PUBLISHED = "published"
STATUS_FAILED = "failed"
