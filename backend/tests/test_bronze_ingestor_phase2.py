from __future__ import annotations

import unittest
from unittest.mock import patch

from app.jobs.bronze_ingestor import (
    _dead_letter_key,
    _domain_from_event_type,
    _object_key,
    _route_invalid_envelope_to_dead_letter,
)


class TestBronzeIngestorPhase2(unittest.TestCase):
    def test_domain_mapping(self) -> None:
        self.assertEqual(_domain_from_event_type("incident.created"), "incident")
        self.assertEqual(_domain_from_event_type("organization.capacity_updated"), "organization")
        self.assertEqual(_domain_from_event_type("volunteer.task_completed"), "volunteer")
        self.assertEqual(_domain_from_event_type("security.login"), "audit")

    @patch("app.jobs.bronze_ingestor.get_settings")
    def test_object_key_has_time_and_event_partitions(self, mock_settings) -> None:
        class S:
            BRONZE_PREFIX = "events"
            BRONZE_GZIP_ENABLED = False

        mock_settings.return_value = S()
        key = _object_key(
            {
                "event_id": "evt-123",
                "event_type": "incident.created",
                "enqueued_at": "2026-04-25T03:06:16Z",
            }
        )
        self.assertIn("events/incident/event_type=incident.created", key)
        self.assertIn("/year=2026/month=04/day=25/hour=03/", key)
        self.assertTrue(key.endswith("/evt-123.json"))

    @patch("app.jobs.bronze_ingestor.get_settings")
    def test_dead_letter_key_format(self, mock_settings) -> None:
        class S:
            BRONZE_PREFIX = "events"
            BRONZE_GZIP_ENABLED = False

        mock_settings.return_value = S()
        key = _dead_letter_key()
        self.assertIn("events/_dead_letter/year=", key)
        self.assertIn("/month=", key)
        self.assertIn("/day=", key)
        self.assertIn("/hour=", key)
        self.assertTrue(key.endswith(".json"))

    @patch("app.jobs.bronze_ingestor.get_settings")
    def test_gzip_extension_behavior(self, mock_settings) -> None:
        class S:
            BRONZE_PREFIX = "events"
            BRONZE_GZIP_ENABLED = True

        mock_settings.return_value = S()
        key = _object_key(
            {
                "event_id": "evt-123",
                "event_type": "incident.created",
                "enqueued_at": "2026-04-25T03:06:16Z",
            }
        )
        self.assertTrue(key.endswith(".json.gz"))

    @patch("app.jobs.bronze_ingestor._write_dead_letter")
    def test_invalid_envelope_routed_to_dead_letter_helper(self, mock_dlq) -> None:
        mock_dlq.return_value = "events/_dead_letter/year=2026/month=04/day=25/hour=03/abc.json"
        key = _route_invalid_envelope_to_dead_letter(
            client=object(),
            bucket="pulsegrid-bronze",
            envelope={"bad": "shape"},
            error_code="missing_event_id",
            topic="pulsegrid.incident.events",
            partition=1,
            offset=42,
        )
        self.assertIn("_dead_letter", key)
        mock_dlq.assert_called_once()


if __name__ == "__main__":
    unittest.main()
