"""Transactional outbox for domain events. PostgreSQL is the outbox store; publish is async via worker."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.sql.models.event_outbox import EventOutbox
from app.db.sql.models.responder_profile import ResponderProfile
from app.db.sql.session import get_session_factory
from app.domain import outbox_event_types as T
from app.domain.event_streaming import event_version_for
from app.models.incident_requests import CreateIncidentResponse
from app.models.volunteer_task_requests import AcceptTaskResponse

_log = logging.getLogger("pulsegrid.outbox")


def _iso_now() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def enqueue_in_session(
    db: Session,
    *,
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
) -> uuid.UUID:
    """Add an outbox row in the current session. Caller must commit."""
    oid = uuid.uuid4()
    row = EventOutbox(
        id=oid,
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload,
        status=T.STATUS_PENDING,
        attempts=0,
    )
    db.add(row)
    _log.info(
        "outbox_enqueued",
        extra={
            "outbox_id": str(oid),
            "event_type": event_type,
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
        },
    )
    return oid


def try_commit_outbox_standalone(
    *,
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
) -> None:
    """Open a new session, insert one outbox row, commit. Swallows errors so API paths stay available."""
    factory = get_session_factory()
    if factory is None:
        _log.info(
            "outbox_skipped_no_database",
            extra={"event_type": event_type, "aggregate_id": aggregate_id},
        )
        return
    try:
        with factory() as db:
            enqueue_in_session(
                db,
                event_type=event_type,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                payload=payload,
            )
            db.commit()
    except Exception:  # noqa: BLE001
        _log.exception(
            "outbox_standalone_insert_failed",
            extra={"event_type": event_type, "aggregate_id": aggregate_id},
        )


def record_incident_lifecycle_outbox(
    resp: CreateIncidentResponse,
    *,
    reporter_user_id: str,
) -> None:
    """Emit incident.created and optionally incident.assigned after Neo4j incident create."""
    iid = resp.incident_id
    base = {
        "incident_id": iid,
        "zone_id": resp.zone_id,
        "status": resp.status,
        "priority_label": resp.priority_label,
        "reporter_user_id": reporter_user_id,
        "occurred_at": _iso_now(),
        "rejection_count": len(resp.rejected_candidates) + len(resp.rejected_organization_candidates),
    }
    try_commit_outbox_standalone(
        event_type=T.INCIDENT_CREATED,
        aggregate_type=T.AGG_INCIDENT,
        aggregate_id=iid,
        payload=base,
    )
    helper = resp.assigned_helper
    if helper and helper.get("id"):
        try_commit_outbox_standalone(
            event_type=T.INCIDENT_ASSIGNED,
            aggregate_type=T.AGG_INCIDENT,
            aggregate_id=iid,
            payload={
                "incident_id": iid,
                "volunteer_id": str(helper["id"]),
                "source": "incident_create",
                "occurred_at": _iso_now(),
            },
        )


def record_incident_accepted_outbox(resp: AcceptTaskResponse, *, volunteer_id: str) -> None:
    iid = resp.incident_id
    try_commit_outbox_standalone(
        event_type=T.INCIDENT_ACCEPTED,
        aggregate_type=T.AGG_INCIDENT,
        aggregate_id=iid,
        payload={
            "incident_id": iid,
            "volunteer_id": volunteer_id,
            "status": resp.status,
            "zone_id": resp.zone_id,
            "occurred_at": _iso_now(),
        },
    )


def apply_volunteer_task_completion_in_session(
    db: Session,
    *,
    volunteer_id: str,
    incident_id: str,
    incident_status: str,
    credits: int,
    trust_score: float,
) -> None:
    """Update responder profile, enqueue incident.completed + volunteer.task_completed, commit once."""
    try:
        uid = uuid.UUID(str(volunteer_id).strip())
    except ValueError:
        _log.warning("outbox_volunteer_completion_invalid_uuid", extra={"volunteer_id": volunteer_id})
        return
    profile = db.query(ResponderProfile).filter(ResponderProfile.user_id == uid).one_or_none()
    if profile is None:
        _log.warning("outbox_volunteer_completion_no_profile", extra={"volunteer_id": volunteer_id})
        return
    profile.credits = max(0, int(credits))
    profile.trust_score = min(1.0, max(0.0, float(trust_score)))
    db.add(profile)
    ts = _iso_now()
    enqueue_in_session(
        db,
        event_type=T.INCIDENT_COMPLETED,
        aggregate_type=T.AGG_INCIDENT,
        aggregate_id=incident_id,
        payload={"incident_id": incident_id, "volunteer_id": volunteer_id, "status": incident_status, "occurred_at": ts},
    )
    enqueue_in_session(
        db,
        event_type=T.VOLUNTEER_TASK_COMPLETED,
        aggregate_type=T.AGG_VOLUNTEER,
        aggregate_id=volunteer_id,
        payload={
            "incident_id": incident_id,
            "volunteer_id": volunteer_id,
            "credits": credits,
            "trust_score": float(trust_score),
            "occurred_at": ts,
        },
    )
    db.commit()


def record_coordinator_assigned(*, incident_id: str, new_volunteer_id: str) -> None:
    try_commit_outbox_standalone(
        event_type=T.INCIDENT_ASSIGNED,
        aggregate_type=T.AGG_INCIDENT,
        aggregate_id=incident_id,
        payload={
            "incident_id": incident_id,
            "volunteer_id": new_volunteer_id,
            "source": "coordinator_reassign",
            "occurred_at": _iso_now(),
        },
    )


def envelope_for_kafka(row: EventOutbox) -> bytes:
    """JSON envelope for the broker; stable keys for future schema registry."""
    body = {
        "event_id": str(row.id),
        "event_type": row.event_type,
        "event_version": event_version_for(row.event_type),
        "aggregate_type": row.aggregate_type,
        "aggregate_id": row.aggregate_id,
        "schema_version": 1,
        "enqueued_at": row.created_at.isoformat() if hasattr(row.created_at, "isoformat") else str(row.created_at),
        "payload": row.payload,
    }
    return json.dumps(body, default=str).encode("utf-8")
