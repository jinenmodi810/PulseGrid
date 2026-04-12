"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    """Runtime configuration. Neo4j AuraDB is the primary graph store."""

    model_config = ConfigDict(extra="ignore")

    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    # Aura: often "neo4j". If Aura returns "database neo4j does not exist", set AUTO / __DEFAULT__ / empty
    # to use the server home database, or set this to the exact name from the Aura console.
    NEO4J_DATABASE: str = Field(default="neo4j")
    # Bolt: TCP/TLS connect phase (default driver was 30s).
    NEO4J_CONNECTION_TIMEOUT: float = Field(default=15.0)
    # Bolt pool: max seconds to wait for a pooled connection (includes opening new Bolt connections).
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT: float = Field(default=25.0)
    # Managed read transactions (admin inspection): server-side transaction timeout (seconds).
    NEO4J_TRANSACTION_TIMEOUT: float = Field(default=25.0)
    GEMINI_API_KEY: str | None = None
    # Model id for google-generativeai (e.g. gemini-2.0-flash, gemini-1.5-flash). TODO: per-tenant routing.
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash")
    # Hackathon-only admin gate (plain text). TODO(Phase1): remove; use real auth.
    ADMIN_EMAIL: str = Field(default="")
    ADMIN_PASSWORD: str = Field(default="")
    # Plain marker returned on admin-login; client sends as X-Admin-Session. TODO: JWT instead.
    ADMIN_SESSION_MARKER: str = Field(default="admin-hackathon")
    # HS256 signing secret for victim/volunteer/org access tokens (set in production).
    # Default only for local demos; override in production.
    JWT_SECRET: str = Field(default="pulsegrid-dev-jwt-secret-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)  # 7 days default for MVP demos

    def resolved_neo4j_database(self) -> str | None:
        """Database name for Bolt `session(database=...)`, or None for server default / home DB."""
        v = (self.NEO4J_DATABASE or "").strip()
        if not v or v.upper() in ("AUTO", "__DEFAULT__", "__HOME__"):
            return None
        return v

    def neo4j_database_display(self) -> str:
        """For logs and health JSON when no explicit graph name is sent to the driver."""
        r = self.resolved_neo4j_database()
        return r if r is not None else "server-default"


@lru_cache
def get_settings() -> Settings:
    """Load settings from process environment (call load_dotenv() in entrypoints first)."""
    return Settings.model_validate(dict(os.environ))


def clear_settings_cache() -> None:
    get_settings.cache_clear()
