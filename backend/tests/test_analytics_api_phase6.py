from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.analytics_routes import router
from app.services import analytics_service


class _FakeSettings:
    ANALYTICS_AUTO_SYNC = False
    ANALYTICS_LOCAL_GOLD_ROOT = ""
    BRONZE_S3_ENDPOINT_URL = "http://localhost:9000"
    BRONZE_S3_ACCESS_KEY = "minioadmin"
    BRONZE_S3_SECRET_KEY = "minioadmin"
    BRONZE_S3_REGION = "us-east-1"
    BRONZE_S3_USE_SSL = False
    GOLD_BUCKET = "pulsegrid-bronze"
    GOLD_PREFIX = "gold"


def _write_sample_gold(root: Path) -> None:
    (root / "gold" / "fact_incident_lifecycle" / "year=2026").mkdir(parents=True, exist_ok=True)
    (root / "gold" / "fact_volunteer_performance" / "year=2026").mkdir(parents=True, exist_ok=True)
    (root / "gold" / "fact_org_capacity" / "year=2026").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "incident_id": "inc-1",
                "zone_id": "zone-central",
                "created_at": "2026-01-01T00:00:00Z",
                "time_to_assignment_seconds": 60.0,
                "time_to_acceptance_seconds": 120.0,
                "time_to_completion_seconds": 300.0,
            }
        ]
    ).to_parquet(root / "gold" / "fact_incident_lifecycle" / "year=2026" / "batch.parquet", index=False)
    pd.DataFrame(
        [{"volunteer_id": "vol-1", "tasks_assigned": 2, "tasks_accepted": 2, "tasks_completed": 1, "latest_credits": 10, "latest_trust_score": 0.8, "avg_completion_time_seconds": 300.0}]
    ).to_parquet(root / "gold" / "fact_volunteer_performance" / "year=2026" / "batch.parquet", index=False)
    pd.DataFrame(
        [{"organization_id": "org-1", "captured_at": "2026-01-01T00:00:00Z", "beds_available": 5, "oxygen_units": 2, "ambulances_available": 1}]
    ).to_parquet(root / "gold" / "fact_org_capacity" / "year=2026" / "batch.parquet", index=False)


class TestAnalyticsApiPhase6(unittest.TestCase):
    def test_service_queries_with_sample_gold(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_sample_gold(root)
            fs = _FakeSettings()
            fs.ANALYTICS_LOCAL_GOLD_ROOT = str(root)
            with patch("app.services.analytics_service.get_settings", return_value=fs):
                overview = analytics_service.query_overview(analytics_service.AnalyticsFilters())
                self.assertEqual(int(overview["incident_operations"]["incidents_total"]), 1)
                zones = analytics_service.query_incidents_by_zone(analytics_service.AnalyticsFilters())
                self.assertEqual(zones[0]["zone_id"], "zone-central")

    def test_route_returns_503_when_gold_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            fs = _FakeSettings()
            fs.ANALYTICS_LOCAL_GOLD_ROOT = str(Path(td) / "missing_gold")
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            with patch("app.services.analytics_service.get_settings", return_value=fs):
                resp = client.get("/analytics/overview")
                self.assertEqual(resp.status_code, 503)


if __name__ == "__main__":
    unittest.main()
