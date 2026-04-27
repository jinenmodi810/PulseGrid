"""Event streaming contracts, routing, and validation helpers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

from app.core.config import get_settings
from app.domain import outbox_event_types as T

TOPIC_INCIDENT_EVENTS = "pulsegrid.incident.events"
TOPIC_ORGANIZATION_EVENTS = "pulsegrid.organization.events"
TOPIC_VOLUNTEER_EVENTS = "pulsegrid.volunteer.events"
TOPIC_AUDIT_EVENTS = "pulsegrid.audit.events"

EVENT_VERSIONS: dict[str, int] = {
    T.INCIDENT_CREATED: 1,
    T.INCIDENT_ASSIGNED: 1,
    T.INCIDENT_ACCEPTED: 1,
    T.INCIDENT_COMPLETED: 1,
    T.ORGANIZATION_CAPACITY_UPDATED: 1,
    T.VOLUNTEER_TASK_COMPLETED: 1,
}

EVENT_TOPIC_MAP: dict[str, str] = {
    T.INCIDENT_CREATED: TOPIC_INCIDENT_EVENTS,
    T.INCIDENT_ASSIGNED: TOPIC_INCIDENT_EVENTS,
    T.INCIDENT_ACCEPTED: TOPIC_INCIDENT_EVENTS,
    T.INCIDENT_COMPLETED: TOPIC_INCIDENT_EVENTS,
    T.ORGANIZATION_CAPACITY_UPDATED: TOPIC_ORGANIZATION_EVENTS,
    T.VOLUNTEER_TASK_COMPLETED: TOPIC_VOLUNTEER_EVENTS,
}

_SCHEMA_FILE_BY_EVENT: dict[str, str] = {
    T.INCIDENT_CREATED: "incident.created.schema.json",
    T.INCIDENT_ASSIGNED: "incident.assigned.schema.json",
    T.INCIDENT_ACCEPTED: "incident.accepted.schema.json",
    T.INCIDENT_COMPLETED: "incident.completed.schema.json",
    T.ORGANIZATION_CAPACITY_UPDATED: "organization.capacity_updated.schema.json",
    T.VOLUNTEER_TASK_COMPLETED: "volunteer.task_completed.schema.json",
}


@lru_cache(maxsize=32)
def _load_event_schema(event_type: str) -> dict[str, Any]:
    schema_file = _SCHEMA_FILE_BY_EVENT.get(event_type)
    if not schema_file:
        raise ValueError(f"No schema contract registered for event_type={event_type!r}")
    p = Path(__file__).resolve().parent / "event_contracts" / schema_file
    return json.loads(p.read_text(encoding="utf-8"))


def event_version_for(event_type: str) -> int:
    return int(EVENT_VERSIONS.get(event_type, 1))


def topic_for_event_type(event_type: str) -> str:
    settings = get_settings()
    if not settings.KAFKA_TOPIC_ROUTING_ENABLED:
        return settings.KAFKA_OUTBOX_TOPIC
    routed = EVENT_TOPIC_MAP.get(event_type, settings.KAFKA_OUTBOX_TOPIC)
    if routed == TOPIC_INCIDENT_EVENTS:
        return settings.KAFKA_TOPIC_INCIDENT_EVENTS
    if routed == TOPIC_ORGANIZATION_EVENTS:
        return settings.KAFKA_TOPIC_ORGANIZATION_EVENTS
    if routed == TOPIC_VOLUNTEER_EVENTS:
        return settings.KAFKA_TOPIC_VOLUNTEER_EVENTS
    if routed == TOPIC_AUDIT_EVENTS:
        return settings.KAFKA_TOPIC_AUDIT_EVENTS
    return settings.KAFKA_OUTBOX_TOPIC


def partition_key_for_event(
    *,
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
) -> str:
    if event_type in {
        T.INCIDENT_CREATED,
        T.INCIDENT_ASSIGNED,
        T.INCIDENT_ACCEPTED,
        T.INCIDENT_COMPLETED,
    }:
        return str(payload.get("incident_id") or aggregate_id or "")
    if event_type == T.ORGANIZATION_CAPACITY_UPDATED:
        return str(payload.get("organization_id") or aggregate_id or "")
    if event_type == T.VOLUNTEER_TASK_COMPLETED:
        return str(payload.get("volunteer_id") or aggregate_id or "")
    return f"{aggregate_type}:{aggregate_id}"


def validate_event_envelope(envelope: dict[str, Any]) -> None:
    event_type = str(envelope.get("event_type") or "").strip()
    if not event_type:
        raise ValidationError("event_type is required")
    schema = _load_event_schema(event_type)
    validate(instance=envelope, schema=schema)
