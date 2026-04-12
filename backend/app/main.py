"""PulseGrid FastAPI entrypoint."""

from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    admin_routes,
    ai,
    auth_routes,
    dashboard_routes,
    debug_routes,
    incident_routes,
    organizations,
    rewards,
    support,
    users,
    volunteers,
    websocket_routes,
)
from app.core.neo4j_client import close_driver, managed_neo4j_session

# Load environment before any service reads os.environ / Settings.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_log = logging.getLogger("pulsegrid")


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.core.config import get_settings

    db = (get_settings().NEO4J_DATABASE or "").strip()
    # Aura connection strings use a hex instance id; that is NOT the graph database name.
    if re.fullmatch(r"[0-9a-f]{6,16}", db, re.IGNORECASE):
        _log.warning(
            "NEO4J_DATABASE=%r looks like an Aura instance id. On Aura the graph is usually named "
            "'neo4j', or use NEO4J_DATABASE=AUTO for the server home database. Using the instance id "
            "here often yields empty data or very slow /admin/* — fix backend/.env and restart.",
            db,
        )
    yield
    close_driver()


app = FastAPI(title="PulseGrid API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, bool]:
    """Liveness for clients and load balancers (no Neo4j)."""
    return {"ok": True}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "PulseGrid backend running",
        "health_neo4j": "/health/neo4j",
        "debug_neo4j_health": "/debug/neo4j-health",
        "debug_persistence_summary": "/debug/persistence-summary",
    }


@app.get("/health/neo4j")
def neo4j_health() -> dict:
    """Verify AuraDB credentials and driver connectivity."""
    from app.core.config import get_settings
    from app.core.neo4j_client import get_driver

    try:
        driver = get_driver()
        settings = get_settings()
        with managed_neo4j_session(driver, settings) as session:
            session.run("RETURN 1 AS ok")
        return {"neo4j": "ok", "database": settings.neo4j_database_display()}
    except Exception as exc:
        return {"neo4j": "error", "detail": str(exc)}


@app.get("/debug/neo4j-health")
def debug_neo4j_health() -> dict[str, str | bool | None]:
    """Temporary Neo4j connectivity probe (structured)."""
    from app.core.config import get_settings
    from app.core.neo4j_client import get_driver

    settings = get_settings()
    db_label = settings.neo4j_database_display()
    try:
        driver = get_driver()
        with managed_neo4j_session(driver, settings) as session:
            session.run("RETURN 1 AS ok")
        return {"connected": True, "database": db_label, "error": None}
    except Exception as exc:
        return {"connected": False, "database": db_label, "error": str(exc)}


app.include_router(auth_routes.router)
app.include_router(debug_routes.router)
app.include_router(users.router)
# Neo4j-backed admin inspection: GET /admin/* (single mount). Client sends X-Admin-Session
# matching settings.ADMIN_SESSION_MARKER after POST /auth/admin-login.
app.include_router(admin_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(incident_routes.router)
app.include_router(volunteers.router)
app.include_router(support.router)
app.include_router(rewards.router)
app.include_router(organizations.router)
app.include_router(ai.router)
app.include_router(websocket_routes.router)
