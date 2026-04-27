"""Local end-to-end demo orchestrator for PulseGrid."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import requests


@dataclass
class StepResult:
    name: str
    ok: bool
    detail: str


class DemoError(RuntimeError):
    pass


class DemoRunner:
    def __init__(self, base_url: str = "http://127.0.0.1:8002") -> None:
        self.base_url = base_url.rstrip("/")
        self.repo_root = Path(__file__).resolve().parents[2]
        self.backend_dir = self.repo_root / "backend"
        self.backend_started_by_script = False
        self.backend_proc: subprocess.Popen[str] | None = None
        self.results: list[StepResult] = []

    def _print_step(self, msg: str) -> None:
        print(f"\n>>> {msg}")

    def _record(self, name: str, ok: bool, detail: str) -> None:
        self.results.append(StepResult(name=name, ok=ok, detail=detail))
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name} - {detail}")

    def _run_cmd(
        self,
        name: str,
        cmd: list[str],
        cwd: Path | None = None,
        check: bool = True,
        env_overrides: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)
        try:
            cp = subprocess.run(
                cmd,
                cwd=str(cwd or self.repo_root),
                text=True,
                capture_output=True,
                check=check,
                env=env,
            )
            self._record(name, True, (cp.stdout.strip() or "ok")[:200])
            return cp
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr.strip() or exc.stdout.strip() or str(exc))[:500]
            self._record(name, False, detail)
            raise DemoError(f"{name} failed: {detail}") from exc

    def _wait_backend(self, timeout_s: int = 45) -> bool:
        end = time.time() + timeout_s
        while time.time() < end:
            try:
                r = requests.get(f"{self.base_url}/health", timeout=2)
                if r.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(1)
        return False

    def _ensure_backend(self) -> None:
        self._print_step("Backend health check")
        if self._wait_backend(timeout_s=3):
            self._record("backend_ready", True, "Backend already running")
            return
        self._print_step("Starting backend")
        self.backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8002"],
            cwd=str(self.backend_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            env=os.environ.copy(),
        )
        self.backend_started_by_script = True
        if not self._wait_backend(timeout_s=45):
            self._record("backend_start", False, "Timed out waiting for /health")
            raise DemoError("Backend failed to start")
        self._record("backend_start", True, "Backend reachable at /health")

    def _api(self, method: str, path: str, token: str | None = None, **kwargs: Any) -> requests.Response:
        headers = kwargs.pop("headers", {}) or {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return requests.request(method, f"{self.base_url}{path}", headers=headers, timeout=20, **kwargs)

    def _register_or_login_victim(self) -> str:
        email = "demo.victim@pulsegrid.com"
        password = "Demo@123"
        login = self._api("POST", "/auth/login-victim", json={"email": email, "password": password})
        if login.status_code == 200:
            return login.json().get("access_token", "")
        reg_body = {
            "email": email,
            "password": password,
            "full_name": "Demo Victim",
            "phone": "5550001001",
            "preferred_language": "en",
            "home_zone_id": "zone-central",
            "household_size": 3,
            "elderly_count": 1,
            "mobility_concern": False,
            "oxygen_dependency": False,
            "emergency_contact_name": "Demo Contact",
            "emergency_contact_phone": "5550001002",
            "emergency_contact_relationship": "family",
        }
        reg = self._api("POST", "/auth/register-victim", json=reg_body)
        if reg.status_code in (200, 201):
            return reg.json().get("access_token", "")
        # Retry login for idempotent reruns
        login2 = self._api("POST", "/auth/login-victim", json={"email": email, "password": password})
        if login2.status_code == 200:
            return login2.json().get("access_token", "")
        raise DemoError(f"Victim auth failed: {login2.status_code} {login2.text[:300]}")

    def _register_or_login_volunteer(self) -> str:
        email = "demo.volunteer@pulsegrid.com"
        password = "Demo@123"
        login = self._api("POST", "/auth/login-volunteer", json={"email": email, "password": password})
        if login.status_code == 200:
            return login.json().get("access_token", "")
        reg_body = {
            "email": email,
            "password": password,
            "full_name": "Demo Volunteer",
            "phone": "5550002001",
            "languages": ["en"],
            "zone_id": "zone-central",
            "availability": "24x7",
            "transport_access": "car",
            "skills": ["first_aid"],
            "support_types": ["medical_support"],
            "verified": True,
            "skill_type": "first_aid",
        }
        reg = self._api("POST", "/auth/register-volunteer", json=reg_body)
        if reg.status_code in (200, 201):
            return reg.json().get("access_token", "")
        login2 = self._api("POST", "/auth/login-volunteer", json={"email": email, "password": password})
        if login2.status_code == 200:
            return login2.json().get("access_token", "")
        raise DemoError(f"Volunteer auth failed: {login2.status_code} {login2.text[:300]}")

    def _register_or_login_org(self) -> str:
        email = "demo.org@pulsegrid.com"
        password = "Demo@123"
        login = self._api("POST", "/auth/login-organization", json={"email": email, "password": password})
        if login.status_code == 200:
            return login.json().get("access_token", "")
        reg_body = {
            "organization_name": "Demo Care Org",
            "organization_type": "hospital",
            "contact_name": "Demo Admin",
            "contact_phone": "5550003001",
            "contact_email": email,
            "password": password,
            "zone_id": "zone-central",
            "coverage_zone_ids": ["zone-central"],
            "beds_available": 20,
            "oxygen_units": 10,
            "ambulances_available": 3,
            "shelter_units": 5,
            "food_capacity_units": 100,
            "rescue_units": 2,
        }
        reg = self._api("POST", "/auth/register-organization", json=reg_body)
        if reg.status_code in (200, 201):
            return reg.json().get("access_token", "")
        login2 = self._api("POST", "/auth/login-organization", json={"email": email, "password": password})
        if login2.status_code == 200:
            return login2.json().get("access_token", "")
        raise DemoError(f"Organization auth failed: {login2.status_code} {login2.text[:300]}")

    def _run_step(self, name: str, fn: Callable[[], str | None]) -> str | None:
        try:
            detail = fn() or "ok"
            self._record(name, True, detail)
            return detail
        except Exception as exc:  # noqa: BLE001
            self._record(name, False, str(exc)[:400])
            raise

    def run(self) -> int:
        try:
            self._print_step("Start local infrastructure")
            self._run_cmd("docker_compose_up", ["docker", "compose", "up", "-d"], cwd=self.repo_root)

            self._print_step("Run DB migrations")
            self._run_cmd("alembic_upgrade", ["alembic", "upgrade", "head"], cwd=self.backend_dir)

            self._ensure_backend()

            self._print_step("Auth seed users (idempotent)")
            victim_token = self._run_step("seed_victim", self._register_or_login_victim) or ""
            _ = self._run_step("seed_volunteer", self._register_or_login_volunteer)
            org_token = self._run_step("seed_organization", self._register_or_login_org) or ""

            self._print_step("Create sample incidents")
            me = self._api("GET", "/auth/me", token=victim_token)
            if me.status_code != 200:
                raise DemoError(f"/auth/me victim failed: {me.status_code} {me.text[:200]}")
            victim_id = str(me.json().get("id") or "")
            for i in range(2):
                body = {
                    "user_id": victim_id,
                    "incident_type": "medical_emergency",
                    "severity": "high",
                    "people_count": 2 + i,
                    "zone_id": "zone-central",
                    "elderly": True,
                    "child_present": False,
                    "injury": True,
                    "oxygen_required": i % 2 == 0,
                    "shelter_needed": False,
                    "food_needed": False,
                    "transport_needed": True,
                    "note": f"Demo incident {i+1}",
                    "use_profile_for_people_count": True,
                    "use_profile_for_elderly": True,
                    "use_profile_for_oxygen_required": True,
                    "intake_source": "form",
                }
                r = self._api("POST", "/incidents/", token=victim_token, json=body)
                if r.status_code not in (200, 201):
                    raise DemoError(f"incident create failed: {r.status_code} {r.text[:220]}")
            self._record("create_incidents", True, "2 incidents created")

            self._print_step("Trigger organization capacity event")
            org_me = self._api("GET", "/auth/me", token=org_token)
            if org_me.status_code != 200:
                raise DemoError(f"org /auth/me failed: {org_me.status_code} {org_me.text[:200]}")
            org_id = str(org_me.json().get("id") or "")
            cap = self._api(
                "POST",
                f"/organizations/{org_id}/capacity-update",
                token=org_token,
                json={"beds_available": 18, "oxygen_units": 9, "ambulances_available": 3, "active": True},
            )
            if cap.status_code not in (200, 201):
                raise DemoError(f"capacity update failed: {cap.status_code} {cap.text[:220]}")
            self._record("capacity_update", True, "organization capacity updated")

            self._print_step("Run outbox publisher once")
            job_env = {
                # Local demo defaults (safe overrides) so pipeline steps work even if backend/.env omits them.
                "KAFKA_BOOTSTRAP_SERVERS": os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092"),
                "KAFKA_TOPIC_ROUTING_ENABLED": os.environ.get("KAFKA_TOPIC_ROUTING_ENABLED", "true"),
                "KAFKA_TOPIC_INCIDENT_EVENTS": os.environ.get("KAFKA_TOPIC_INCIDENT_EVENTS", "pulsegrid.incident.events"),
                "KAFKA_TOPIC_ORGANIZATION_EVENTS": os.environ.get("KAFKA_TOPIC_ORGANIZATION_EVENTS", "pulsegrid.organization.events"),
                "KAFKA_TOPIC_VOLUNTEER_EVENTS": os.environ.get("KAFKA_TOPIC_VOLUNTEER_EVENTS", "pulsegrid.volunteer.events"),
                "BRONZE_KAFKA_TOPICS": os.environ.get(
                    "BRONZE_KAFKA_TOPICS",
                    "pulsegrid.incident.events,pulsegrid.organization.events,pulsegrid.volunteer.events",
                ),
                "BRONZE_BUCKET": os.environ.get("BRONZE_BUCKET", "pulsegrid-bronze"),
                "BRONZE_PREFIX": os.environ.get("BRONZE_PREFIX", "events"),
                "BRONZE_S3_ENDPOINT_URL": os.environ.get("BRONZE_S3_ENDPOINT_URL", "http://localhost:9000"),
                "BRONZE_S3_ACCESS_KEY": os.environ.get("BRONZE_S3_ACCESS_KEY", "minioadmin"),
                "BRONZE_S3_SECRET_KEY": os.environ.get("BRONZE_S3_SECRET_KEY", "minioadmin"),
                "BRONZE_S3_REGION": os.environ.get("BRONZE_S3_REGION", "us-east-1"),
                "BRONZE_S3_USE_SSL": os.environ.get("BRONZE_S3_USE_SSL", "false"),
                "SILVER_BUCKET": os.environ.get("SILVER_BUCKET", "pulsegrid-bronze"),
                "SILVER_BRONZE_PREFIX": os.environ.get("SILVER_BRONZE_PREFIX", "events"),
                "SILVER_PREFIX": os.environ.get("SILVER_PREFIX", "silver"),
                "SILVER_REJECTED_PREFIX": os.environ.get("SILVER_REJECTED_PREFIX", "silver/_rejected"),
                "GOLD_BUCKET": os.environ.get("GOLD_BUCKET", "pulsegrid-bronze"),
                "GOLD_PREFIX": os.environ.get("GOLD_PREFIX", "gold"),
                "GOLD_REJECTED_PREFIX": os.environ.get("GOLD_REJECTED_PREFIX", "gold/_rejected"),
            }
            self._run_cmd(
                "outbox_publish_once",
                [sys.executable, "-c", "from app.jobs.outbox_publisher import run_once; print(run_once())"],
                cwd=self.backend_dir,
                env_overrides=job_env,
            )

            self._print_step("Run bronze ingestion once")
            self._run_cmd(
                "bronze_once",
                [
                    sys.executable,
                    "-c",
                    "import json; from app.jobs.bronze_ingestor import run_once; print(json.dumps(run_once(), sort_keys=True))",
                ],
                cwd=self.backend_dir,
                env_overrides=job_env,
            )

            self._print_step("Run silver and gold ETL")
            self._run_cmd("silver_etl", [sys.executable, "-m", "app.jobs.silver_etl"], cwd=self.backend_dir, env_overrides=job_env)
            self._run_cmd("gold_etl", [sys.executable, "-m", "app.jobs.gold_etl"], cwd=self.backend_dir, env_overrides=job_env)

            self._print_step("Verify analytics API")
            for p in [
                "/analytics/overview",
                "/analytics/incidents-by-zone",
                "/analytics/time-to-response",
                "/analytics/organization-capacity",
            ]:
                r = self._api("GET", p)
                if r.status_code != 200:
                    raise DemoError(f"{p} failed: {r.status_code} {r.text[:240]}")
            self._record("analytics_api", True, "Core analytics endpoints returned 200")

            self._print_step("Verify /metrics")
            m = self._api("GET", "/metrics")
            if m.status_code != 200:
                raise DemoError(f"/metrics failed: {m.status_code}")
            txt = m.text
            required_markers = [
                "pulsegrid_api_requests_total",
                "pulsegrid_outbox_pending_events",
                "pulsegrid_silver_runtime_processed",
                "pulsegrid_gold_runtime_processed",
            ]
            miss = [x for x in required_markers if x not in txt]
            if miss:
                raise DemoError(f"/metrics missing markers: {miss}")
            self._record("metrics_endpoint", True, "/metrics includes core markers")

            ok_count = sum(1 for r in self.results if r.ok)
            print(f"\nDemo complete: {ok_count}/{len(self.results)} steps passed.")
            return 0
        except Exception as exc:  # noqa: BLE001
            print(f"\nDemo failed: {exc}")
            return 1
        finally:
            if self.backend_started_by_script and self.backend_proc is not None:
                self.backend_proc.terminate()
                try:
                    self.backend_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.backend_proc.kill()


def main() -> None:
    base_url = os.environ.get("PULSEGRID_DEMO_BASE_URL", "http://127.0.0.1:8002")
    rc = DemoRunner(base_url=base_url).run()
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
