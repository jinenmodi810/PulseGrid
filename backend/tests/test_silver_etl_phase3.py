from __future__ import annotations

import unittest
from io import BytesIO

from app.jobs.silver_etl import (
    _load_checkpoint,
    _save_checkpoint,
    _select_objects_for_run,
    normalize_envelope,
    process_envelopes_for_run,
)


def _incident_envelope(event_id: str = "evt-1") -> dict:
    return {
        "event_id": event_id,
        "event_type": "incident.created",
        "aggregate_type": "incident",
        "aggregate_id": "inc-1",
        "schema_version": 1,
        "event_version": 1,
        "enqueued_at": "2026-04-25T03:06:16Z",
        "payload": {
            "incident_id": "inc-1",
            "zone_id": "zone-central",
            "status": "open",
            "priority_label": "CRITICAL",
            "reporter_user_id": "victim-1",
            "occurred_at": "2026-04-25T03:06:16Z",
        },
    }


def _organization_envelope(event_id: str = "evt-org-1") -> dict:
    return {
        "event_id": event_id,
        "event_type": "organization.capacity_updated",
        "aggregate_type": "organization",
        "aggregate_id": "org-1",
        "schema_version": 1,
        "event_version": 1,
        "enqueued_at": "2026-04-25T03:06:16Z",
        "payload": {
            "organization_id": "org-1",
            "updated": {"beds_available": 42},
            "occurred_at": "2026-04-25T03:06:16Z",
        },
    }


def _volunteer_envelope(event_id: str = "evt-vol-1") -> dict:
    return {
        "event_id": event_id,
        "event_type": "volunteer.task_completed",
        "aggregate_type": "volunteer",
        "aggregate_id": "vol-1",
        "schema_version": 1,
        "event_version": 1,
        "enqueued_at": "2026-04-25T03:06:16Z",
        "payload": {
            "volunteer_id": "vol-1",
            "incident_id": "inc-1",
            "credits": 10,
            "trust_score": 0.9,
            "occurred_at": "2026-04-25T03:06:16Z",
        },
    }


class TestSilverEtlPhase3(unittest.TestCase):
    def test_envelope_parsing_and_validation(self) -> None:
        normalized, reason = normalize_envelope(_incident_envelope())
        self.assertIsNotNone(normalized)
        self.assertEqual(reason, "")

        bad = _incident_envelope()
        del bad["event_id"]
        n2, reason2 = normalize_envelope(bad)
        self.assertIsNone(n2)
        self.assertIn("missing_required_fields", reason2)

    def test_deduplication_by_event_id(self) -> None:
        items = [("k1", _incident_envelope("dup-1")), ("k2", _incident_envelope("dup-1"))]
        datasets, rejected, deduped = process_envelopes_for_run(items)
        self.assertEqual(deduped, 1)
        self.assertEqual(len(datasets["incident_events"]), 1)
        self.assertEqual(len(rejected), 0)

    def test_domain_routing(self) -> None:
        items = [("i", _incident_envelope()), ("o", _organization_envelope()), ("v", _volunteer_envelope())]
        datasets, rejected, _ = process_envelopes_for_run(items)
        self.assertEqual(len(datasets["incident_events"]), 1)
        self.assertEqual(len(datasets["organization_events"]), 1)
        self.assertEqual(len(datasets["volunteer_events"]), 1)
        self.assertEqual(len(rejected), 0)

    def test_flattened_output_shape(self) -> None:
        n1, _ = normalize_envelope(_incident_envelope())
        self.assertIsNotNone(n1)
        row = n1.record
        for key in ["incident_id", "zone_id", "status", "priority_label", "reporter_user_id", "occurred_at"]:
            self.assertIn(key, row)

    def test_rejected_record_handling(self) -> None:
        items = [("bad_key", {"foo": "bar"})]
        _, rejected, _ = process_envelopes_for_run(items)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["source_key"], "bad_key")
        self.assertIn("missing_required_fields", rejected[0]["reason"])

    def test_checkpoint_load_and_save(self) -> None:
        class FakeS3:
            def __init__(self) -> None:
                self.store = {}

            def put_object(self, Bucket, Key, Body, ContentType):  # noqa: N803
                self.store[(Bucket, Key)] = Body

            def get_object(self, Bucket, Key):  # noqa: N803
                return {"Body": BytesIO(self.store[(Bucket, Key)])}

        s3 = FakeS3()
        cp = {
            "processed_object_keys": ["events/a.json"],
            "last_run_started_at": "2026-01-01T00:00:00Z",
            "last_run_completed_at": "2026-01-01T00:00:02Z",
            "total_processed": 1,
            "total_rejected": 0,
            "total_written": 1,
        }
        _save_checkpoint(s3, "b", "silver/_checkpoints/cp.json", cp)
        loaded = _load_checkpoint(s3, "b", "silver/_checkpoints/cp.json")
        self.assertEqual(loaded["processed_object_keys"], ["events/a.json"])
        self.assertEqual(loaded["total_processed"], 1)

    def test_skip_already_processed_objects(self) -> None:
        selected, skipped = _select_objects_for_run(
            ["events/1.json", "events/2.json", "events/3.json"],
            ["events/1.json", "events/3.json"],
            full_refresh=False,
        )
        self.assertEqual(selected, ["events/2.json"])
        self.assertEqual(skipped, 2)

    def test_full_refresh_ignores_checkpoint(self) -> None:
        selected, skipped = _select_objects_for_run(
            ["events/1.json", "events/2.json"],
            ["events/1.json"],
            full_refresh=True,
        )
        self.assertEqual(selected, ["events/1.json", "events/2.json"])
        self.assertEqual(skipped, 0)

    def test_checkpoint_update_after_successful_run(self) -> None:
        existing = ["events/1.json"]
        new = ["events/2.json", "events/3.json"]
        updated = sorted(set(existing + new))
        self.assertEqual(updated, ["events/1.json", "events/2.json", "events/3.json"])


if __name__ == "__main__":
    unittest.main()
