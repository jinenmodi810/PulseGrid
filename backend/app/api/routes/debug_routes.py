"""Development-only diagnostics (no auth). Do not expose in production without protection."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services import graph_counts_service

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/persistence-summary")
def get_persistence_summary() -> dict[str, int]:
    try:
        return graph_counts_service.persistence_summary()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
