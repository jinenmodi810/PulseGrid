"""Cypher for organization operations dashboard (Neo4j)."""

GET_ORGANIZATION = """
MATCH (o:Organization {id: $org_id})
RETURN o
"""

LIST_ORGAN_INCIDENTS = """
MATCH (i:Incident)
WHERE coalesce(i.assigned_organization_id, '') = $org_id
RETURN i.id AS incident_id,
       coalesce(i.incident_type, i.title, '') AS incident_type,
       coalesce(i.severity, 'medium') AS severity,
       coalesce(i.status, 'open') AS status,
       coalesce(i.priority_label, 'MEDIUM') AS priority_label,
       toFloat(coalesce(i.priority_score, 0)) AS priority_score,
       coalesce(i.zone_id, '') AS zone_id,
       coalesce(i.assigned_volunteer_name, '') AS assigned_volunteer_name,
       coalesce(i.response_tier, '') AS response_tier,
       coalesce(i.escalation_required, false) AS escalation_required,
       coalesce(i.decision_summary, '') AS decision_summary,
       coalesce(i.assigned_volunteer_name, '') <> '' AS volunteer_support_active,
       i.created_at AS created_at
ORDER BY i.created_at IS NULL ASC, i.created_at DESC
"""

COUNT_ORG_INCIDENTS = """
MATCH (i:Incident)
WHERE coalesce(i.assigned_organization_id, '') = $org_id
  AND NOT coalesce(i.status, 'open') IN ['resolved', 'cancelled']
RETURN count(i) AS c
"""

SET_ORGAN_CAPACITY = """
MATCH (o:Organization {id: $org_id})
SET o += $props
RETURN o.id AS id
"""

ACCEPT_ORG_INCIDENT = """
MATCH (i:Incident {id: $incident_id})
WHERE coalesce(i.assigned_organization_id, '') = $org_id
SET i.organization_accepted = true,
    i.organization_response_status = coalesce(i.organization_response_status, 'accepted')
RETURN i.id AS incident_id, i.status AS status
"""

UPDATE_ORG_RESPONSE_STATUS = """
MATCH (i:Incident {id: $incident_id})
WHERE coalesce(i.assigned_organization_id, '') = $org_id
SET i.organization_response_status = $status
RETURN i.id AS incident_id, i.organization_response_status AS organization_response_status
"""
