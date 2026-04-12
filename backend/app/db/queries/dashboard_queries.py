"""Cypher for dashboard counters."""

ACTIVE_INCIDENTS = """
MATCH (i:Incident)
WHERE NOT coalesce(i.status, 'open') IN ['resolved', 'cancelled']
RETURN count(i) AS c
"""

AVAILABLE_VOLUNTEERS = """
MATCH (v:Volunteer)
RETURN count(v) AS c
"""

HOSPITALS_AVAILABLE = """
MATCH (h:Hospital)
WHERE coalesce(h.beds_available, 0) > 0
RETURN count(h) AS c
"""

SHELTERS_AVAILABLE = """
MATCH (s:Shelter)
RETURN count(s) AS c
"""

PENDING_REQUESTS = """
MATCH (i:Incident)
WHERE coalesce(i.status, 'open') = 'open'
RETURN count(i) AS c
"""

RESOLVED_REQUESTS = """
MATCH (i:Incident)
WHERE coalesce(i.status, '') = 'resolved'
RETURN count(i) AS c
"""
