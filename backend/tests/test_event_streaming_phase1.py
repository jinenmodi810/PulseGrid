from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app.db.sql.models.event_outbox import EventOutbox
from app.jobs.outbox_publisher import _topic_and_key
from app.services.outbox_service import envelope_for_kafka
from app.domain.event_streaming import (
    topic_for_event_type,
    validate_event_envelope,
)


class TestEventStreamingPhase1(unittest.TestCase):
    def test_valid_incident_created_envelope_passes_schema(self) -> None:
        row = EventOutbox(
            event_type="incident.created",
            aggregate_type="incident",
            aggregate_id="incident-123",
            payload={
                "incident_id": "incident-123",
                "zone_id": "zone-central",
                "status": "open",
                "priority_label": "CRITICAL",
                "reporter_user_id": "victim-1",
                "occurred_at": "2026-04-25T00:00:00Z",
                "rejection_count": 0,
            },
            status="pending",
            attempts=0,
            created_at=datetime.now(tz=timezone.utc),
        )
        envelope = envelope_for_kafka(row)
        validate_event_envelope(__import__("json").loads(envelope.decode("utf-8")))

    def test_invalid_incident_created_envelope_fails_schema(self) -> None:
        row = EventOutbox(
            event_type="incident.created",
            aggregate_type="incident",
            aggregate_id="incident-123",
            payload={
                "zone_id": "zone-central",
                "status": "open",
                "priority_label": "CRITICAL",
                "reporter_user_id": "victim-1",
                "occurred_at": "2026-04-25T00:00:00Z",
                "rejection_count": 0,
            },
            status="pending",
            attempts=0,
            created_at=datetime.now(tz=timezone.utc),
        )
        envelope = envelope_for_kafka(row)
        with self.assertRaises(Exception):
            validate_event_envelope(__import__("json").loads(envelope.decode("utf-8")))

    @patch("app.domain.event_streaming.get_settings")
    def test_topic_routing_enabled(self, mock_settings) -> None:
        class S:
            KAFKA_TOPIC_ROUTING_ENABLED = True
            KAFKA_OUTBOX_TOPIC = "pulsegrid.domain.events"
            KAFKA_TOPIC_INCIDENT_EVENTS = "pulsegrid.incident.events"
            KAFKA_TOPIC_ORGANIZATION_EVENTS = "pulsegrid.organization.events"
            KAFKA_TOPIC_VOLUNTEER_EVENTS = "pulsegrid.volunteer.events"
            KAFKA_TOPIC_AUDIT_EVENTS = "pulsegrid.audit.events"

        mock_settings.return_value = S()
        self.assertEqual(topic_for_event_type("incident.created"), "pulsegrid.incident.events")
        self.assertEqual(topic_for_event_type("organization.capacity_updated"), "pulsegrid.organization.events")
        self.assertEqual(topic_for_event_type("volunteer.task_completed"), "pulsegrid.volunteer.events")

    @patch("app.domain.event_streaming.get_settings")
    def test_topic_routing_disabled_falls_back(self, mock_settings) -> None:
        class S:
            KAFKA_TOPIC_ROUTING_ENABLED = False
            KAFKA_OUTBOX_TOPIC = "pulsegrid.domain.events"
            KAFKA_TOPIC_INCIDENT_EVENTS = "pulsegrid.incident.events"
            KAFKA_TOPIC_ORGANIZATION_EVENTS = "pulsegrid.organization.events"
            KAFKA_TOPIC_VOLUNTEER_EVENTS = "pulsegrid.volunteer.events"
            KAFKA_TOPIC_AUDIT_EVENTS = "pulsegrid.audit.events"

        mock_settings.return_value = S()
        self.assertEqual(topic_for_event_type("incident.created"), "pulsegrid.domain.events")

    @patch("app.jobs.outbox_publisher.topic_for_event_type")
    def test_partition_key_uses_incident_id(self, mock_topic_for_event_type) -> None:
        mock_topic_for_event_type.return_value = "pulsegrid.incident.events"
        row = EventOutbox(
            event_type="incident.completed",
            aggregate_type="incident",
            aggregate_id="incident-123",
            payload={
                "incident_id": "incident-123",
                "volunteer_id": "vol-1",
                "status": "completed",
                "occurred_at": "2026-04-25T00:00:00Z",
            },
            status="pending",
            attempts=0,
            created_at=datetime.now(tz=timezone.utc),
        )
        envelope = __import__("json").loads(envelope_for_kafka(row).decode("utf-8"))
        topic, key = _topic_and_key(row, envelope)
        self.assertEqual(topic, "pulsegrid.incident.events")
        self.assertEqual(key.decode("utf-8"), "incident-123")


if __name__ == "__main__":
    unittest.main()
