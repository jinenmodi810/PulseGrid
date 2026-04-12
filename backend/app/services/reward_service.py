"""Volunteer credits and rewards (Phase 1: EARNED_REWARD edges)."""


def update_credits(*, volunteer_id: str, delta: int, baseline: int = 100) -> int:
    # TODO(Phase1): MERGE Volunteer credits in Neo4j transactionally.
    _ = volunteer_id
    return max(0, baseline + delta)
