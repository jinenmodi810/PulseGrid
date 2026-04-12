"""Cypher fragments for incidents (Phase 1: expand with filters and graph traversals)."""

MERGE_INCIDENT = """
MERGE (i:Incident {id: $id})
SET i.title = $title,
    i.status = $status,
    i.severity = $severity,
    i.created_at = $created_at
"""

LIST_INCIDENTS = """
MATCH (i:Incident)
RETURN i.id AS id, i.title AS title, i.status AS status, i.severity AS severity, i.created_at AS created_at
ORDER BY i.created_at DESC
"""

LINK_INCIDENT_TO_ZONE = """
MATCH (i:Incident {id: $incident_id})
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (i)-[:LOCATED_IN]->(z)
"""

LINK_USER_REPORTED_OPTIONAL = """
MATCH (i:Incident {id: $incident_id})
OPTIONAL MATCH (u:User {id: $user_id})
WITH i, u
WHERE u IS NOT NULL
MERGE (u)-[:REPORTED]->(i)
"""

GET_USER_PROFILE_FOR_INCIDENT = """
MATCH (u:User {id: $user_id})
RETURN coalesce(u.household_size, u.family_size, 1) AS household_size,
       coalesce(u.elderly_count, 0) AS elderly_count,
       coalesce(u.mobility_concern, false) AS mobility_concern,
       coalesce(u.oxygen_dependency, false) AS oxygen_dependency,
       coalesce(u.preferred_language, 'en') AS preferred_language,
       coalesce(u.emergency_contact_name, '') AS emergency_contact_name,
       coalesce(u.emergency_contact_phone, '') AS emergency_contact_phone,
       coalesce(u.emergency_contact_relationship, '') AS emergency_contact_relationship
"""

ASSIGN_VOLUNTEER_TO_INCIDENT = """
MATCH (v:Volunteer {id: $volunteer_id}), (i:Incident {id: $incident_id})
MERGE (v)-[:ASSIGNED_TO]->(i)
"""

ASSIGN_ORGANIZATION_TO_INCIDENT = """
MATCH (o:Organization {id: $org_id}), (i:Incident {id: $incident_id})
MERGE (o)-[:ROUTED_FOR]->(i)
"""

GET_INCIDENT_DETAIL = """
MATCH (i:Incident {id: $incident_id})
OPTIONAL MATCH (v:Volunteer)-[:ASSIGNED_TO]->(i)
RETURN i AS incident,
       v.id AS assigned_id,
       coalesce(v.display_name, '') AS assigned_name,
       i.assigned_organization_id AS assigned_organization_id,
       i.assigned_organization_name AS assigned_organization_name,
       i.assigned_organization_type AS assigned_organization_type,
       i.response_tier AS response_tier,
       coalesce(i.volunteer_candidate_allowed, true) AS volunteer_candidate_allowed,
       coalesce(i.organization_candidate_allowed, false) AS organization_candidate_allowed,
       coalesce(i.escalation_required, false) AS escalation_required,
       coalesce(i.decision_summary, '') AS decision_summary,
       coalesce(i.tier_reasons_json, '[]') AS tier_reasons_json,
       coalesce(i.rejected_org_json, '[]') AS rejected_org_json
"""

GET_INCIDENT_AI_CONTEXT = """
MATCH (i:Incident {id: $incident_id})
OPTIONAL MATCH (u:User)-[:REPORTED]->(i)
OPTIONAL MATCH (v:Volunteer)-[:ASSIGNED_TO]->(i)
RETURN i AS incident,
       u AS reporter,
       v AS volunteer
"""

LIST_INCIDENTS_FULL = """
MATCH (i:Incident)
RETURN i.id AS id,
       coalesce(i.incident_type, i.title, 'Incident') AS title,
       coalesce(i.status, 'open') AS status,
       coalesce(i.severity, 'medium') AS severity,
       coalesce(i.created_at, '') AS created_at
ORDER BY i.created_at DESC
LIMIT 100
"""
