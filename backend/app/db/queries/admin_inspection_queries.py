"""Cypher for admin inspection — read-only aggregates and listings."""

# --- counts (overview) ---

COUNT_USERS = "MATCH (u:User) RETURN count(u) AS c"
COUNT_VOLUNTEERS = "MATCH (v:Volunteer) RETURN count(v) AS c"
COUNT_INCIDENTS = "MATCH (i:Incident) RETURN count(i) AS c"
COUNT_ACTIVE_INCIDENTS = """
MATCH (i:Incident)
WHERE NOT coalesce(i.status, 'open') IN ['resolved', 'cancelled']
RETURN count(i) AS c
"""
COUNT_PENDING_INCIDENTS = """
MATCH (i:Incident)
WHERE coalesce(i.status, 'open') IN ['open', 'assigned']
RETURN count(i) AS c
"""
COUNT_ACCEPTED_INCIDENTS = """
MATCH (i:Incident)
WHERE coalesce(i.status, '') = 'accepted'
RETURN count(i) AS c
"""
COUNT_RESOLVED_INCIDENTS = """
MATCH (i:Incident)
WHERE coalesce(i.status, '') = 'resolved'
RETURN count(i) AS c
"""
COUNT_HOSPITALS = "MATCH (h:Hospital) RETURN count(h) AS c"
COUNT_SHELTERS = "MATCH (s:Shelter) RETURN count(s) AS c"
COUNT_SUPPORT_CONTACTS = "MATCH (sc:SupportContact) RETURN count(sc) AS c"
COUNT_ZONES = "MATCH (z:Zone) RETURN count(z) AS c"
COUNT_REWARDS = "MATCH (r:Reward) RETURN count(r) AS c"
COUNT_DISTINCT_ASSIGNED_INCIDENTS = """
MATCH ()-[:ASSIGNED_TO]->(i:Incident)
RETURN count(DISTINCT i) AS c
"""
COUNT_COMPLETED_INCIDENTS = """
MATCH (:Volunteer)-[:COMPLETED_TASK]->(i:Incident)
RETURN count(DISTINCT i) AS c
"""
AGG_VOLUNTEER_TRUST_AND_CREDITS = """
MATCH (v:Volunteer)
RETURN coalesce(avg(toFloat(v.trust_score)), 0.0) AS avg_trust,
       coalesce(sum(toInteger(v.credits)), 0) AS sum_credits
"""

# --- lists ---

LIST_USERS = """
MATCH (u:User)
OPTIONAL MATCH (u)-[:LOCATED_IN]->(z:Zone)
RETURN u.id AS user_id,
       coalesce(u.full_name, '') AS name,
       coalesce(u.phone, '') AS phone,
       coalesce(u.preferred_language, '') AS language,
       coalesce(z.id, '') AS zone_id,
       u.family_size AS family_size,
       u.created_at AS created_at
ORDER BY coalesce(u.full_name, u.id)
"""

LIST_VOLUNTEERS = """
MATCH (v:Volunteer)
OPTIONAL MATCH (v)-[:LOCATED_IN]->(z:Zone)
OPTIONAL MATCH (v)-[:ASSIGNED_TO]->(ia:Incident)
OPTIONAL MATCH (v)-[:COMPLETED_TASK]->(ic:Incident)
WITH v, z,
     count(DISTINCT ia) AS assigned_incident_count,
     count(DISTINCT ic) AS completed_incident_count
RETURN v.id AS volunteer_id,
       coalesce(v.display_name, '') AS name,
       coalesce(v.phone, '') AS phone,
       coalesce(v.skill_type, '') AS skill_type,
       v.languages AS languages,
       coalesce(z.id, '') AS zone_id,
       coalesce(v.availability, '') AS availability,
       coalesce(v.verified, false) AS verified,
       toFloat(coalesce(v.trust_score, 0.5)) AS trust_score,
       toInteger(coalesce(v.credits, 0)) AS credits,
       assigned_incident_count,
       completed_incident_count
ORDER BY name, volunteer_id
"""

LIST_INCIDENTS_ADMIN = """
MATCH (i:Incident)
OPTIONAL MATCH (u:User)-[:REPORTED]->(i)
OPTIONAL MATCH (v:Volunteer)-[:ASSIGNED_TO]->(i)
RETURN i.id AS incident_id,
       coalesce(i.incident_type, i.title, '') AS incident_type,
       coalesce(i.severity, 'medium') AS severity,
       toFloat(coalesce(i.priority_score, 0)) AS priority_score,
       coalesce(i.priority_label, 'MEDIUM') AS priority_label,
       coalesce(i.status, 'open') AS status,
       coalesce(i.zone_id, '') AS zone_id,
       toInteger(coalesce(i.people_count, 1)) AS people_count,
       i.created_at AS created_at,
       u.id AS reported_by_user_id,
       v.id AS assigned_volunteer_id,
       coalesce(i.elderly, false) AS elderly,
       coalesce(i.child_present, false) AS child_present,
       coalesce(i.injury, false) AS injury,
       coalesce(i.oxygen_required, false) AS oxygen_required,
       coalesce(i.shelter_needed, false) AS shelter_needed,
       coalesce(i.food_needed, false) AS food_needed,
       coalesce(i.transport_needed, false) AS transport_needed,
       coalesce(i.note, '') AS note
ORDER BY i.created_at DESC NULLS LAST, incident_id DESC
"""

GET_INCIDENT_ADMIN = """
MATCH (i:Incident {id: $incident_id})
OPTIONAL MATCH (u:User)-[:REPORTED]->(i)
OPTIONAL MATCH (u)-[:LOCATED_IN]->(uz:Zone)
OPTIONAL MATCH (v:Volunteer)-[:ASSIGNED_TO]->(i)
OPTIONAL MATCH (i)-[:LOCATED_IN]->(z:Zone)
RETURN i AS incident,
       u AS reporter,
       coalesce(uz.id, '') AS reporter_zone_id,
       v AS assignee,
       z AS zone
"""

INCIDENT_GRAPH_LINES = """
MATCH (i:Incident {id: $incident_id})
OPTIONAL MATCH (a)-[rin]->(i)
OPTIONAL MATCH (i)-[rout]->(b)
RETURN collect(DISTINCT CASE WHEN a IS NOT NULL
  THEN coalesce(head(labels(a)), '?') + ':' + coalesce(a.id, '') + ' -[' + type(rin) + ']-> Incident' END) AS incoming,
       collect(DISTINCT CASE WHEN b IS NOT NULL
         THEN 'Incident -[' + type(rout) + ']-> ' + coalesce(head(labels(b)), '?') + ':' + coalesce(b.id, '') END) AS outgoing
"""

INCIDENT_TASK_EVENTS = """
MATCH (i:Incident {id: $incident_id})
OPTIONAL MATCH (v1)-[ac:ACCEPTED_TASK]->(i)
OPTIONAL MATCH (v2)-[cp:COMPLETED_TASK]->(i)
RETURN collect(DISTINCT {event: 'accepted', volunteer_id: v1.id, at: ac.created_at}) +
       collect(DISTINCT {event: 'completed', volunteer_id: v2.id, at: cp.created_at}) AS events
"""

LIST_ASSIGNMENTS = """
MATCH (v:Volunteer)-[:ASSIGNED_TO]->(i:Incident)
OPTIONAL MATCH (v)-[ac:ACCEPTED_TASK]->(i)
RETURN i.id AS incident_id,
       v.id AS volunteer_id,
       coalesce(v.display_name, v.id) AS volunteer_name,
       coalesce(i.status, '') AS status,
       coalesce(i.zone_id, '') AS zone_id,
       coalesce(i.priority_label, '') AS priority_label,
       ac.created_at AS assigned_at
ORDER BY assigned_at DESC, incident_id
"""

LIST_REWARDS_SUMMARY = """
MATCH (v:Volunteer)
OPTIONAL MATCH (v)-[:EARNED_REWARD]->(er:Reward)
OPTIONAL MATCH (v)-[:COMPLETED_TASK]->(ic:Incident)
WITH v, count(DISTINCT er) AS earned_reward_count, count(DISTINCT ic) AS completed_incident_count
RETURN v.id AS volunteer_id,
       coalesce(v.display_name, '') AS volunteer_name,
       toInteger(coalesce(v.credits, 0)) AS credits,
       toFloat(coalesce(v.trust_score, 0.5)) AS trust_score,
       earned_reward_count,
       completed_incident_count
ORDER BY volunteer_name, volunteer_id
"""

LIST_HOSPITALS_PROPS = """
MATCH (h:Hospital)
RETURN properties(h) AS props
ORDER BY coalesce(h.id, h.name, '')
LIMIT 500
"""

LIST_SHELTERS_PROPS = """
MATCH (s:Shelter)
RETURN properties(s) AS props
ORDER BY coalesce(s.id, s.name, '')
LIMIT 500
"""

LIST_SUPPORT_CONTACTS_PROPS = """
MATCH (sc:SupportContact)
RETURN properties(sc) AS props
ORDER BY coalesce(sc.id, sc.name, '')
LIMIT 500
"""

LIST_ZONES_ADMIN = """
MATCH (z:Zone)
RETURN z.id AS zone_id, coalesce(z.name, z.id) AS name
ORDER BY zone_id
"""
