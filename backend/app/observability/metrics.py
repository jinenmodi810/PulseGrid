"""Prometheus-compatible metrics for API and data pipeline jobs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from app.db.sql.models.event_outbox import EventOutbox
from app.db.sql.session import get_session_factory
from app.domain import outbox_event_types as T

# --- API metrics ---
api_requests_total = Counter(
    "pulsegrid_api_requests_total",
    "Total API requests by route/method/status.",
    ["method", "route", "status_code"],
)
api_request_latency_seconds = Histogram(
    "pulsegrid_api_request_latency_seconds",
    "API request latency in seconds by route/method.",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)
api_errors_total = Counter(
    "pulsegrid_api_errors_total",
    "API 5xx responses by route/method.",
    ["method", "route"],
)

# --- Outbox metrics ---
outbox_pending_events = Gauge("pulsegrid_outbox_pending_events", "Current pending outbox rows.")
outbox_published_events = Gauge("pulsegrid_outbox_published_events", "Current published outbox rows.")
outbox_failed_events = Gauge("pulsegrid_outbox_failed_events", "Current failed outbox rows.")
outbox_publish_attempts_total = Counter(
    "pulsegrid_outbox_publish_attempts_total",
    "Outbox publish attempts performed by worker.",
)

# --- Data jobs metrics (runtime counters) ---
bronze_ingestor_written_total = Counter(
    "pulsegrid_bronze_ingestor_written_total",
    "Total bronze records written.",
)
bronze_ingestor_dead_letter_total = Counter(
    "pulsegrid_bronze_ingestor_dead_letter_total",
    "Total bronze records written to dead-letter.",
)
silver_processed_total = Counter(
    "pulsegrid_silver_processed_total",
    "Total silver processed records.",
)
silver_rejected_total = Counter(
    "pulsegrid_silver_rejected_total",
    "Total silver rejected records.",
)
gold_processed_total = Counter(
    "pulsegrid_gold_processed_total",
    "Total gold processed records.",
)
gold_rejected_total = Counter(
    "pulsegrid_gold_rejected_total",
    "Total gold rejected records.",
)

# Snapshot gauges for job runs (read from shared runtime file)
bronze_runtime_written = Gauge("pulsegrid_bronze_runtime_written", "Latest bronze runtime written count.")
bronze_runtime_dead_letter = Gauge("pulsegrid_bronze_runtime_dead_letter", "Latest bronze runtime dead-letter count.")
silver_runtime_processed = Gauge("pulsegrid_silver_runtime_processed", "Latest silver runtime processed count.")
silver_runtime_rejected = Gauge("pulsegrid_silver_runtime_rejected", "Latest silver runtime rejected count.")
gold_runtime_processed = Gauge("pulsegrid_gold_runtime_processed", "Latest gold runtime processed count.")
gold_runtime_rejected = Gauge("pulsegrid_gold_runtime_rejected", "Latest gold runtime rejected count.")
outbox_runtime_publish_attempts = Gauge(
    "pulsegrid_outbox_runtime_publish_attempts",
    "Latest outbox publisher attempts observed across worker runs.",
)

# --- Analytics API metrics ---
analytics_data_not_ready_total = Counter(
    "pulsegrid_analytics_data_not_ready_total",
    "Analytics requests that failed because Gold data is not ready.",
    ["endpoint"],
)
analytics_query_failure_total = Counter(
    "pulsegrid_analytics_query_failure_total",
    "Analytics requests that failed due to query/runtime errors.",
    ["endpoint"],
)


_RUNTIME_METRICS_FILE = Path(__file__).resolve().parents[2] / "data" / "metrics_runtime.json"


def _read_runtime_metrics() -> dict[str, Any]:
    try:
        if not _RUNTIME_METRICS_FILE.exists():
            return {}
        return json.loads(_RUNTIME_METRICS_FILE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def update_runtime_metric(metric_name: str, value: int | float) -> None:
    """Persist runtime job counters to a shared local file for /metrics scrape."""
    try:
        _RUNTIME_METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = _read_runtime_metrics()
        payload[str(metric_name)] = float(value)
        _RUNTIME_METRICS_FILE.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
    except Exception:  # noqa: BLE001
        # Keep jobs resilient even if metrics persistence fails.
        return


def increment_runtime_metric(metric_name: str, delta: int | float = 1.0) -> None:
    """Increment a shared runtime metric in local snapshot storage."""
    try:
        _RUNTIME_METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = _read_runtime_metrics()
        current = float(payload.get(str(metric_name), 0.0))
        payload[str(metric_name)] = current + float(delta)
        _RUNTIME_METRICS_FILE.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
    except Exception:  # noqa: BLE001
        return


def refresh_outbox_gauges() -> None:
    """Refresh outbox gauges from PostgreSQL (best effort)."""
    factory = get_session_factory()
    if factory is None:
        return
    try:
        with factory() as session:
            pending = (
                session.query(EventOutbox).filter(EventOutbox.status == T.STATUS_PENDING).count()
            )
            published = (
                session.query(EventOutbox).filter(EventOutbox.status == T.STATUS_PUBLISHED).count()
            )
            failed = session.query(EventOutbox).filter(EventOutbox.status == T.STATUS_FAILED).count()
        outbox_pending_events.set(float(pending))
        outbox_published_events.set(float(published))
        outbox_failed_events.set(float(failed))
    except Exception:  # noqa: BLE001
        return


def refresh_runtime_gauges() -> None:
    payload = _read_runtime_metrics()
    bronze_runtime_written.set(float(payload.get("bronze_written", 0.0)))
    bronze_runtime_dead_letter.set(float(payload.get("bronze_dead_letter", 0.0)))
    silver_runtime_processed.set(float(payload.get("silver_processed", 0.0)))
    silver_runtime_rejected.set(float(payload.get("silver_rejected", 0.0)))
    gold_runtime_processed.set(float(payload.get("gold_processed", 0.0)))
    gold_runtime_rejected.set(float(payload.get("gold_rejected", 0.0)))
    outbox_runtime_publish_attempts.set(float(payload.get("outbox_publish_attempts", 0.0)))


def render_prometheus_metrics() -> tuple[bytes, str]:
    refresh_outbox_gauges()
    refresh_runtime_gauges()
    return generate_latest(), CONTENT_TYPE_LATEST
