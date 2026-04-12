"""Rewards endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from app.models.reward import RewardRead
from app.services import rewards_neo4j_service
from app.services.reward_service import update_credits

router = APIRouter(prefix="/rewards", tags=["rewards"])
_log = logging.getLogger("pulsegrid.rewards")


@router.get("/", response_model=list[RewardRead])
def list_rewards() -> list[RewardRead]:
    try:
        rows = rewards_neo4j_service.list_rewards()
    except Exception as exc:  # noqa: BLE001
        _log.warning("rewards Neo4j read failed: %s", exc)
        return []
    out: list[RewardRead] = []
    for r in rows:
        rid = str(r.get("id") or "").strip() or "unknown"
        title = str(r.get("title") or "Reward").strip() or "Reward"
        desc = str(r.get("description") or "").strip()
        badge = str(r.get("badge_type") or "bronze").strip().lower() or "bronze"
        cv = r.get("credits_value")
        credits = int(cv) if cv is not None else 0
        try:
            out.append(
                RewardRead(
                    id=rid,
                    title=title,
                    description=desc,
                    badge_type=badge,
                    credits_value=credits,
                )
            )
        except Exception:  # noqa: BLE001
            continue
    return out


@router.post("/credits/demo", response_model=dict)
def demo_credit_update(volunteer_id: str = "vol-001", delta: int = 10) -> dict:
    # TODO(Phase1): authenticated mutation + Neo4j transaction.
    new_balance = update_credits(volunteer_id=volunteer_id, delta=delta)
    return {"volunteer_id": volunteer_id, "applied_delta": delta, "new_balance_mock": new_balance}
