"""Cypher fragments for volunteers."""

MERGE_VOLUNTEER = """
MERGE (v:Volunteer {id: $id})
SET v.display_name = $display_name,
    v.skills = $skills,
    v.credits = $credits
"""

LIST_VOLUNTEERS = """
MATCH (v:Volunteer)
RETURN v.id AS id, v.display_name AS display_name, v.skills AS skills, v.credits AS credits
ORDER BY v.display_name
"""
