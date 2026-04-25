"""Outbox → Kafka/Redpanda publisher (separate process; use SKIP LOCKED for concurrent workers)."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.sql.models.event_outbox import EventOutbox
from app.db.sql.session import get_session_factory
from app.domain import outbox_event_types as T
from app.services import outbox_service

_log = logging.getLogger("pulsegrid.outbox_publisher")

_producer: object | None = None
_producer_topic: str | None = None


def _ensure_producer() -> tuple[object | None, str | None]:
    global _producer, _producer_topic
    if _producer is not None and _producer_topic is not None:
        return _producer, _producer_topic
    try:
        from kafka import KafkaProducer
    except ImportError as exc:  # noqa: PIE786
        _log.error("outbox_publisher_import_kafka_failed: %s", exc)
        return None, None
    settings = get_settings()
    brokers = (getattr(settings, "KAFKA_BOOTSTRAP_SERVERS", None) or "").strip()
    if not brokers:
        return None, None
    topic = (getattr(settings, "KAFKA_OUTBOX_TOPIC", None) or "pulsegrid.domain.events").strip()
    _producer = KafkaProducer(
        bootstrap_servers=[b.strip() for b in brokers.split(",") if b.strip()],
        acks="all",
        retries=2,
    )
    _producer_topic = topic
    return _producer, _producer_topic


def _publish_row(session: Session, row: EventOutbox, now: datetime, max_attempts: int) -> bool:
    """Returns True if message was produced and the row is marked published in this session."""
    producer, topic = _ensure_producer()
    if producer is None or not topic:
        return False
    value = outbox_service.envelope_for_kafka(row)
    key = f"{row.aggregate_type}:{row.aggregate_id}".encode("utf-8")
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
    producer, _topic = _ensure_producer()
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
