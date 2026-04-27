"""Outbox → Kafka/Redpanda publisher (separate process; use SKIP LOCKED for concurrent workers)."""

from __future__ import annotations

import logging
import time
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.sql.models.event_outbox import EventOutbox
from app.db.sql.session import get_session_factory
from app.domain import outbox_event_types as T
from app.observability.metrics import increment_runtime_metric, outbox_publish_attempts_total
from app.domain.event_streaming import (
    partition_key_for_event,
    topic_for_event_type,
    validate_event_envelope,
)
from app.services import outbox_service

_log = logging.getLogger("pulsegrid.outbox_publisher")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_producer: object | None = None


def _ensure_producer() -> object | None:
    global _producer
    if _producer is not None:
        return _producer
    try:
        from kafka import KafkaProducer
    except ImportError as exc:  # noqa: PIE786
        _log.error("outbox_publisher_import_kafka_failed: %s", exc)
        return None
    settings = get_settings()
    brokers = (getattr(settings, "KAFKA_BOOTSTRAP_SERVERS", None) or "").strip()
    if not brokers:
        return None
    _producer = KafkaProducer(
        bootstrap_servers=[b.strip() for b in brokers.split(",") if b.strip()],
        acks="all",
        retries=2,
    )
    return _producer


def _decode_envelope(raw: bytes) -> dict[str, Any]:
    return json.loads(raw.decode("utf-8"))


def _topic_and_key(row: EventOutbox, envelope: dict[str, Any]) -> tuple[str, bytes]:
    topic = topic_for_event_type(row.event_type)
    key = partition_key_for_event(
        event_type=row.event_type,
        aggregate_type=row.aggregate_type,
        aggregate_id=row.aggregate_id,
        payload=envelope.get("payload") or {},
    )
    return topic, key.encode("utf-8")


def _publish_row(session: Session, row: EventOutbox, now: datetime, max_attempts: int) -> bool:
    """Returns True if message was produced and the row is marked published in this session."""
    producer = _ensure_producer()
    if producer is None:
        return False
    outbox_publish_attempts_total.inc()
    increment_runtime_metric("outbox_publish_attempts", 1)
    value = outbox_service.envelope_for_kafka(row)
    try:
        envelope = _decode_envelope(value)
        validate_event_envelope(envelope)
        topic, key = _topic_and_key(row, envelope)
    except Exception as exc:  # noqa: BLE001
        row.attempts = (row.attempts or 0) + 1
        row.last_error = f"validation_failed: {str(exc)[:1900]}"
        if row.attempts >= max_attempts:
            row.status = T.STATUS_FAILED
        session.add(row)
        _log.error(
            "outbox_event_validation_failed",
            extra={"outbox_id": str(row.id), "event_type": row.event_type, "error": str(exc)[:200]},
        )
        return False
    try:
        future = producer.send(topic, key=key, value=value)
        future.get(timeout=30)
    except Exception as exc:  # noqa: BLE001
        row.attempts = (row.attempts or 0) + 1
        row.last_error = str(exc)[:2000]
        if row.attempts >= max_attempts:
            row.status = T.STATUS_FAILED
        session.add(row)
        _log.warning(
            "outbox_publish_failed",
            extra={"outbox_id": str(row.id), "attempts": row.attempts, "error": str(exc)[:200]},
        )
        return False
    row.status = T.STATUS_PUBLISHED
    row.published_at = now
    row.last_error = None
    session.add(row)
    _log.info(
        "outbox_published",
        extra={"outbox_id": str(row.id), "event_type": row.event_type, "topic": topic},
    )
    return True


def run_once() -> int:
    """Select pending outbox rows, publish, commit. Returns count successfully published to broker."""
    factory = get_session_factory()
    if factory is None:
        return 0
    producer = _ensure_producer()
    if producer is None:
        _log.debug("outbox_publisher_kafka_unconfigured_rolling")
        return 0

    settings = get_settings()
    batch = int(getattr(settings, "OUTBOX_PUBLISHER_BATCH_SIZE", 50))
    max_attempts = int(getattr(settings, "OUTBOX_MAX_PUBLISH_ATTEMPTS", 10))
    now = datetime.now(tz=timezone.utc)
    published = 0
    with factory() as session:
        rows: list[EventOutbox] = list(
            session.scalars(
                select(EventOutbox)
                .where(
                    EventOutbox.status == T.STATUS_PENDING,
                    EventOutbox.attempts < max_attempts,
                )
                .order_by(EventOutbox.created_at.asc())
                .limit(batch)
                .with_for_update(skip_locked=True),
            ),
        )
        for row in rows:
            if _publish_row(session, row, now, max_attempts):
                published += 1
        session.commit()
    return published


def main_loop() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    )
    _log.info("outbox_publisher_starting")
    settings = get_settings()
    interval = float(getattr(settings, "OUTBOX_PUBLISHER_POLL_SECONDS", 2.0))
    while True:
        try:
            n = run_once()
            if n:
                _log.info("outbox_publisher_batch published=%s", n)
        except Exception:  # noqa: BLE001
            _log.exception("outbox_publisher_iteration_failed")
        time.sleep(interval)


if __name__ == "__main__":
    main_loop()
