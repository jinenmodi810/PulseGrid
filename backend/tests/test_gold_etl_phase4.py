from __future__ import annotations

import unittest

import pandas as pd

from app.jobs.gold_etl import (
    build_fact_incident_lifecycle,
    build_fact_org_capacity,
    build_fact_volunteer_performance,
)


class TestGoldEtlPhase4(unittest.TestCase):
    def test_lifecycle_duration_calculation(self) -> None:
        df = pd.DataFrame(
            [
                {"event_id": "1", "event_type": "incident.created", "incident_id": "inc-1", "occurred_at": "2026-01-01T00:00:00Z", "zone_id": "zone-central", "priority_label": "HIGH", "status": "open"},
                {"event_id": "2", "event_type": "incident.assigned", "incident_id": "inc-1", "occurred_at": "2026-01-01T00:01:00Z", "volunteer_id": "vol-1"},
                {"event_id": "3", "event_type": "incident.accepted", "incident_id": "inc-1", "occurred_at": "2026-01-01T00:02:00Z", "volunteer_id": "vol-1"},
                {"event_id": "4", "event_type": "incident.completed", "incident_id": "inc-1", "occurred_at": "2026-01-01T00:05:00Z", "volunteer_id": "vol-1", "status": "completed"},
            ]
        )
        out, rejected = build_fact_incident_lifecycle(df)
        self.assertEqual(len(rejected), 0)
        self.assertEqual(len(out), 1)
        self.assertEqual(float(out.iloc[0]["time_to_assignment_seconds"]), 60.0)
        self.assertEqual(float(out.iloc[0]["time_to_completion_seconds"]), 300.0)

    def test_missing_event_handling(self) -> None:
        df = pd.DataFrame(
            [
                {"event_id": "1", "event_type": "incident.created", "incident_id": "inc-2", "occurred_at": "2026-01-01T00:00:00Z"},
            ]
        )
        out, rejected = build_fact_incident_lifecycle(df)
        self.assertEqual(len(rejected), 0)
        self.assertEqual(len(out), 1)
        self.assertTrue(pd.isna(out.iloc[0]["accepted_at"]))
        self.assertTrue(pd.isna(out.iloc[0]["completed_at"]))

    def test_volunteer_performance_aggregation(self) -> None:
        incident_df = pd.DataFrame(
            [
                {"event_type": "incident.assigned", "volunteer_id": "vol-1"},
                {"event_type": "incident.accepted", "volunteer_id": "vol-1"},
                {"event_type": "incident.completed", "volunteer_id": "vol-1"},
            ]
        )
        volunteer_df = pd.DataFrame(
            [
                {"volunteer_id": "vol-1", "occurred_at": "2026-01-01T00:00:00Z", "credits": 5, "trust_score": 0.7},
                {"volunteer_id": "vol-1", "occurred_at": "2026-01-01T01:00:00Z", "credits": 8, "trust_score": 0.9},
            ]
        )
        lifecycle_df = pd.DataFrame([{"assigned_volunteer_id": "vol-1", "time_to_completion_seconds": 120.0}])
        out, rejected = build_fact_volunteer_performance(incident_df, volunteer_df, lifecycle_df)
        self.assertEqual(len(rejected), 0)
        self.assertEqual(len(out), 1)
        self.assertEqual(int(out.iloc[0]["tasks_completed"]), 1)
        self.assertEqual(int(out.iloc[0]["latest_credits"]), 8)

    def test_org_capacity_extraction(self) -> None:
        org_df = pd.DataFrame(
            [
                {"organization_id": "org-1", "occurred_at": "2026-01-01T00:00:00Z", "updated_fields_json": "{\"beds_available\":10,\"oxygen_units\":2}"},
            ]
        )
        out, rejected = build_fact_org_capacity(org_df)
        self.assertEqual(len(rejected), 0)
        self.assertEqual(len(out), 1)
        self.assertEqual(int(out.iloc[0]["beds_available"]), 10)
        self.assertEqual(int(out.iloc[0]["oxygen_units"]), 2)

    def test_negative_duration_rejection(self) -> None:
        df = pd.DataFrame(
            [
                {"event_id": "1", "event_type": "incident.created", "incident_id": "inc-3", "occurred_at": "2026-01-01T00:10:00Z"},
                {"event_id": "2", "event_type": "incident.assigned", "incident_id": "inc-3", "occurred_at": "2026-01-01T00:01:00Z"},
            ]
        )
        out, rejected = build_fact_incident_lifecycle(df)
        self.assertEqual(len(out), 0)
        self.assertGreaterEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["reason"], "negative_duration")


if __name__ == "__main__":
    unittest.main()
