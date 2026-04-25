"""Cypher for volunteer task feed and accept/complete flows."""

LIST_ASSIGNED_TASKS = """
MATCH (v:Volunteer {id: $volunteer_id})-[:ASSIGNED_TO]->(i:Incident)
WHERE NOT coalesce(i.status, '') IN ['resolved', 'cancelled']
OPTIONAL MATCH (i)-[:LOCATED_IN]->(z:Zone)
RETURN i AS incident,
       coalesce(z.id, i.zone_id, '') AS zone_id,
       'assigned' AS task_source
"""

LIST_NEARBY_OPEN_TASKS = """
MATCH (v:Volunteer {id: $volunteer_id})-[:LOCATED_IN]->(z:Zone)
MATCH (i:Incident)-[:LOCATED_IN]->(z)
WHERE coalesce(i.status, 'open') = 'open'
  AND NOT EXISTS { MATCH (:Volunteer)-[:ASSIGNED_TO]->(i) }
  AND coalesce(i.response_tier, '') <> 'organization_only'
RETURN DISTINCT i AS incident,
       z.id AS zone_id,
       'nearby_open' AS task_source
"""

ACCEPT_TASK = """
MATCH (v:Volunteer {id: $volunteer_id}), (i:Incident {id: $incident_id})
WHERE (v)-[:ASSIGNED_TO]->(i)
   OR (
     (v)-[:LOCATED_IN]->(:Zone)<-[:LOCATED_IN]-(i)
     AND coalesce(i.status, 'open') = 'open'
     AND coalesce(i.assigned_volunteer_id, '') = ''
   )
WITH v, i
LIMIT 1
MERGE (v)-[ac:ACCEPTED_TASK]->(i)
ON CREATE SET ac.created_at = datetime()
SET i.status = 'accepted',
    i.assigned_volunteer_id = coalesce(i.assigned_volunteer_id, v.id),
    i.assigned_volunteer_name = CASE
      WHEN coalesce(i.assigned_volunteer_name, '') <> '' THEN i.assigned_volunteer_name
      ELSE coalesce(v.display_name, '')
    END
WITH v, i
WHERE i.assigned_volunteer_id = v.id
MERGE (v)-[:ASSIGNED_TO]->(i)
WITH v, i
OPTIONAL MATCH (other:Volunteer)-[r:ASSIGNED_TO]->(i)
WHERE other.id <> v.id
DELETE r
RETURN i AS incident
"""

COMPLETE_TASK = """
MATCH (v:Volunteer {id: $volunteer_id})-[:ASSIGNED_TO]->(i:Incident {id: $incident_id})
WHERE coalesce(i.status, '') <> 'resolved'
WITH v, i
MERGE (v)-[cp:COMPLETED_TASK]->(i)
ON CREATE SET cp.created_at = datetime()
SET i.status = 'resolved',
    i.route_status = coalesce(i.route_status, 'completed'),
    v.credits = coalesce(v.credits, 0) + 15,
    v.trust_score = CASE
      WHEN coalesce(v.trust_score, 0.5) + 0.02 > 1.0 THEN 1.0
      ELSE coalesce(v.trust_score, 0.5) + 0.02
    END
RETURN i AS incident,
       v.id AS volunteer_id,
       coalesce(v.credits, 0) AS credits,
       coalesce(v.trust_score, 0.5) AS trust_score
"""

GET_VOLUNTEER_PROPS = """
MATCH (v:Volunteer {id: $volunteer_id})
OPTIONAL MATCH (v)-[:LOCATED_IN]->(z:Zone)
RETURN v.id AS id,
       coalesce(v.display_name, '') AS display_name,
       coalesce(v.skill_type, '') AS skill_type,
       coalesce(v.skills, []) AS skills,
       coalesce(v.support_types, []) AS support_types,
       coalesce(v.languages, []) AS languages,
       coalesce(v.transport_access, '') AS transport_access,
       coalesce(v.availability, '') AS availability,
       coalesce(v.credits, 0) AS credits,
       coalesce(v.trust_score, 0.5) AS trust_score,
       coalesce(z.id, '') AS zone_id
"""

LIST_VOLUNTEERS_BRIEF = """
MATCH (v:Volunteer)
RETURN v.id AS id,
       coalesce(v.display_name, '') AS display_name,
       coalesce(v.skill_type, '') AS skill_type,
       coalesce(v.credits, 0) AS credits,
       coalesce(v.trust_score, 0.5) AS trust_score
ORDER BY v.display_name
LIMIT 100
"""
