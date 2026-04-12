"""Support directory endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from app.models.support_contact import SupportContactRead
from app.services import support_neo4j_service

router = APIRouter(prefix="/support", tags=["support"])
_log = logging.getLogger("pulsegrid.support")


@router.get("/contacts", response_model=list[SupportContactRead])
def list_support_contacts() -> list[SupportContactRead]:
    try:
        rows = support_neo4j_service.list_support_contacts()
    except Exception as exc:  # noqa: BLE001
        _log.warning("support contacts Neo4j read failed: %s", exc)
        return []
    out: list[SupportContactRead] = []
    for r in rows:
        tid = str(r.get("id") or "").strip() or "unknown"
        label = str(r.get("label") or "Support").strip() or "Support"
        phone = str(r.get("phone") or "").strip()
        t = str(r.get("type") or "other").strip().lower() or "other"
        try:
            out.append(SupportContactRead(id=tid, label=label, phone=phone, type=t))
        except Exception:  # noqa: BLE001
            continue
    return out
