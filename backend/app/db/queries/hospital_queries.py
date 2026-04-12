"""Cypher fragments for hospitals."""

MERGE_HOSPITAL = """
MERGE (h:Hospital {id: $id})
SET h.name = $name,
    h.beds_available = $beds_available,
    h.latitude = $latitude,
    h.longitude = $longitude
"""

LIST_HOSPITALS = """
MATCH (h:Hospital)
RETURN h.id AS id, h.name AS name, h.beds_available AS beds_available,
       h.latitude AS latitude, h.longitude AS longitude
ORDER BY h.name
"""
