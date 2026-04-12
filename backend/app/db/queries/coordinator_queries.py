"""Cypher for coordinator override actions on incidents."""

REASSIGN_INCIDENT = """
MATCH (i:Incident {id: $incident_id})
OPTIONAL MATCH ()-[rel:ASSIGNED_TO]->(i)
DELETE rel
WITH i
MATCH (nv:Volunteer {id: $new_volunteer_id})
MERGE (nv)-[:ASSIGNED_TO]->(i)
SET i.status = 'assigned',
    i.assigned_volunteer_id = nv.id,
    i.assigned_volunteer_name = coalesce(nv.display_name, nv.id),
    i.route_status = coalesce(i.route_status, 'pending')
RETURN i AS incident
"""

ESCALATE_INCIDENT = """
MATCH (i:Incident {id: $incident_id})
SET i.status = 'escalated',
    i.escalation_note = $note
RETURN i AS incident
"""

BLOCK_ROUTE = """
MATCH (i:Incident {id: $incident_id})
SET i.route_status = 'blocked',
    i.route_block_reason = $reason
RETURN i AS incident
"""
