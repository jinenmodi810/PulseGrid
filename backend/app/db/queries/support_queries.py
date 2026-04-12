"""Cypher fragments for support contacts."""

MERGE_SUPPORT_CONTACT = """
MERGE (s:SupportContact {id: $id})
SET s.label = $label,
    s.phone = $phone,
    s.type = $type
"""

LIST_SUPPORT_CONTACTS = """
MATCH (s:SupportContact)
RETURN s.id AS id, s.label AS label, s.phone AS phone, s.type AS type
ORDER BY s.label
"""
