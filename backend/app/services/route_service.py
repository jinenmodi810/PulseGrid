"""Routing between graph nodes (Phase 1: external map + graph weights)."""

from __future__ import annotations

from typing import Any


def compute_route(*, from_id: str, to_id: str) -> dict[str, Any]:
    # TODO(Phase1): read ROUTE_TO / BLOCKED_ROUTE from Neo4j and merge external ETA.
    return {
        "from_id": from_id,
        "to_id": to_id,
        "edges": [],
        "eta_minutes": None,
        "note": "placeholder route",
    }
