"""Reward catalog reads from Neo4j."""

from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import rewards_queries as rq


def list_rewards() -> list[dict[str, Any]]:
    driver = get_driver()
    settings = get_settings()

    def work(tx: Any) -> list[dict[str, Any]]:
        result = tx.run(rq.LIST_REWARDS)
        return [dict(r) for r in result]

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(work)
