from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.analytics_duckdb import QUERY_CATALOG, run_queries


class TestAnalyticsDuckdbPhase5(unittest.TestCase):
    def test_query_catalog_contains_required_queries(self) -> None:
        required = {
            "average_time_to_assignment",
            "average_time_to_completion",
            "incidents_by_zone",
            "tasks_completed_by_volunteer",
            "latest_organization_capacity",
        }
        self.assertTrue(required.issubset(set(QUERY_CATALOG.keys())))

    def test_run_queries_returns_expected_dataframe_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Build minimal gold parquet structure
            (root / "gold" / "fact_incident_lifecycle" / "year=2026").mkdir(parents=True, exist_ok=True)
            (root / "gold" / "fact_volunteer_performance" / "year=2026").mkdir(parents=True, exist_ok=True)
            (root / "gold" / "fact_org_capacity" / "year=2026").mkdir(parents=True, exist_ok=True)
            (root / "gold" / "dim_time" / "year=2026").mkdir(parents=True, exist_ok=True)

            pd.DataFrame(
                [
                    {"incident_id": "inc-1", "zone_id": "zone-central", "time_to_assignment_seconds": 60.0, "time_to_completion_seconds": 300.0}
                ]
            ).to_parquet(root / "gold" / "fact_incident_lifecycle" / "year=2026" / "batch.parquet", index=False)
            pd.DataFrame([{"volunteer_id": "vol-1", "tasks_completed": 5}]).to_parquet(
                root / "gold" / "fact_volunteer_performance" / "year=2026" / "batch.parquet", index=False
            )
            pd.DataFrame(
                [
                    {
                        "organization_id": "org-1",
                        "captured_at": "2026-01-01T00:00:00Z",
                        "beds_available": 10,
                        "oxygen_units": 2,
                        "ambulances_available": 1,
                        "shelter_units": 0,
                        "food_capacity_units": 20,
                        "rescue_units": 3,
                    }
                ]
            ).to_parquet(
                root / "gold" / "fact_org_capacity" / "year=2026" / "batch.parquet", index=False
            )
            pd.DataFrame([{"date_key": 20260101, "date": "2026-01-01", "year": 2026, "month": 1, "day": 1, "hour": 0}]).to_parquet(
                root / "gold" / "dim_time" / "year=2026" / "batch.parquet", index=False
            )

            outputs = run_queries(root, ["incidents_by_zone", "tasks_completed_by_volunteer", "latest_organization_capacity"])
            self.assertIn("incidents_by_zone", outputs)
            self.assertEqual(outputs["incidents_by_zone"].iloc[0]["zone_id"], "zone-central")
            self.assertEqual(int(outputs["tasks_completed_by_volunteer"].iloc[0]["tasks_completed"]), 5)
            self.assertEqual(outputs["latest_organization_capacity"].iloc[0]["organization_id"], "org-1")


if __name__ == "__main__":
    unittest.main()
