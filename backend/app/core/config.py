"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    """Runtime configuration: PostgreSQL is the system of record; Neo4j is a projection graph."""

    model_config = ConfigDict(extra="ignore")

    # --- PostgreSQL (system of record) ---
    # e.g. postgresql+psycopg2://jinenmodi@localhost:5432/pulsegrid_db
    DATABASE_URL: str | None = None
    # When true, exposes POST /data/users for local/integration testing (disable in production).
    PG_WRITE_ROUTES_ENABLED: bool = Field(default=False)
    # CSV list of allowed CORS origins. Use "*" only for local throwaway demos.
    CORS_ORIGINS: str = Field(default="http://127.0.0.1:8000,http://127.0.0.1:8002,http://localhost:8000,http://localhost:8002")

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

    # --- Event outbox (PostgreSQL) + Kafka/Redpanda (optional) ---
    # If unset, outbox rows stay pending; API writes still succeed; run the publisher when broker is up.
    KAFKA_BOOTSTRAP_SERVERS: str | None = None
    KAFKA_OUTBOX_TOPIC: str = Field(default="pulsegrid.domain.events")
    KAFKA_TOPIC_ROUTING_ENABLED: bool = Field(default=True)
    KAFKA_TOPIC_INCIDENT_EVENTS: str = Field(default="pulsegrid.incident.events")
    KAFKA_TOPIC_ORGANIZATION_EVENTS: str = Field(default="pulsegrid.organization.events")
    KAFKA_TOPIC_VOLUNTEER_EVENTS: str = Field(default="pulsegrid.volunteer.events")
    KAFKA_TOPIC_AUDIT_EVENTS: str = Field(default="pulsegrid.audit.events")
    OUTBOX_MAX_PUBLISH_ATTEMPTS: int = Field(default=10)
    OUTBOX_PUBLISHER_BATCH_SIZE: int = Field(default=50)
    OUTBOX_PUBLISHER_POLL_SECONDS: float = Field(default=2.0)

    # --- Bronze lake ingestion (MinIO / S3-compatible) ---
    BRONZE_KAFKA_CONSUMER_GROUP: str = Field(default="pulsegrid-bronze-consumer")
    BRONZE_KAFKA_TOPICS: str = Field(
        default="pulsegrid.incident.events,pulsegrid.organization.events,pulsegrid.volunteer.events"
    )
    BRONZE_BUCKET: str = Field(default="pulsegrid-bronze")
    BRONZE_PREFIX: str = Field(default="events")
    BRONZE_S3_ENDPOINT_URL: str = Field(default="http://localhost:9000")
    BRONZE_S3_ACCESS_KEY: str = Field(default="minioadmin")
    BRONZE_S3_SECRET_KEY: str = Field(default="minioadmin")
    BRONZE_S3_REGION: str = Field(default="us-east-1")
    BRONZE_S3_USE_SSL: bool = Field(default=False)
    BRONZE_POLL_TIMEOUT_MS: int = Field(default=1000)
    BRONZE_GZIP_ENABLED: bool = Field(default=False)

    # --- Silver ETL (Bronze -> Silver Parquet) ---
    SILVER_BUCKET: str = Field(default="pulsegrid-bronze")
    SILVER_BRONZE_PREFIX: str = Field(default="events")
    SILVER_PREFIX: str = Field(default="silver")
    SILVER_REJECTED_PREFIX: str = Field(default="silver/_rejected")
    SILVER_CHECKPOINT_KEY: str = Field(default="silver/_checkpoints/bronze_to_silver_checkpoint.json")
    SILVER_FULL_REFRESH: bool = Field(default=False)

    # --- Gold marts (Silver -> business facts/dimensions) ---
    GOLD_BUCKET: str = Field(default="pulsegrid-bronze")
    GOLD_PREFIX: str = Field(default="gold")
    GOLD_REJECTED_PREFIX: str = Field(default="gold/_rejected")
    ANALYTICS_LOCAL_GOLD_ROOT: str = Field(default="backend/data/gold_cache")
    ANALYTICS_AUTO_SYNC: bool = Field(default=True)
    ANALYTICS_SYNC_MIN_SECONDS: int = Field(default=30)

    def cors_origins_list(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return []
        if raw == "*":
            return ["*"]
        return [x.strip() for x in raw.split(",") if x.strip()]

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
