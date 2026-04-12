"""Cypher fragments for rewards."""

MERGE_REWARD = """
MERGE (r:Reward {id: $id})
SET r.title = $title,
    r.description = $description,
    r.badge_type = $badge_type,
    r.credits_value = $credits_value
"""

LIST_REWARDS = """
MATCH (r:Reward)
RETURN r.id AS id, r.title AS title, r.description AS description,
       r.badge_type AS badge_type, r.credits_value AS credits_value
ORDER BY r.title
"""
