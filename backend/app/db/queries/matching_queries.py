"""Volunteer discovery for graph-based matching."""

_VOLUNTEER_PROPS = """
       coalesce(v.skill_type, '') AS skill_type,
       coalesce(v.skills, []) AS skills,
       coalesce(v.support_types, []) AS support_types,
       coalesce(v.languages, []) AS languages,
       coalesce(v.transport_access, '') AS transport_access,
       coalesce(v.availability, '') AS availability,
       toFloat(coalesce(v.trust_score, 0.5)) AS trust_score,
       coalesce(v.credits, 0) AS credits
"""

VOLUNTEERS_IN_ZONE = f"""
MATCH (v:Volunteer)-[:LOCATED_IN]->(z:Zone {{id: $zone_id}})
RETURN v.id AS id,
       coalesce(v.display_name, '') AS name,
       {_VOLUNTEER_PROPS.strip()}
"""

VOLUNTEERS_OTHER_ZONES = f"""
MATCH (v:Volunteer)-[:LOCATED_IN]->(z:Zone)
WHERE z.id <> $zone_id
RETURN v.id AS id,
       coalesce(v.display_name, '') AS name,
       {_VOLUNTEER_PROPS.strip()},
       z.id AS zone_id
""".strip()

_ORG_PROPS = """
       coalesce(o.name, '') AS name,
       coalesce(o.org_type, '') AS org_type,
       coalesce(o.zone_id, '') AS zone_id,
       coalesce(o.active, true) AS active,
       coalesce(o.verified, true) AS verified,
       toInteger(coalesce(o.beds_available, 0)) AS beds_available,
       toInteger(coalesce(o.oxygen_units, 0)) AS oxygen_units,
       toInteger(coalesce(o.ambulances_available, 0)) AS ambulances_available,
       toInteger(coalesce(o.shelter_units, 0)) AS shelter_units,
       toInteger(coalesce(o.food_capacity_units, 0)) AS food_capacity_units,
       toInteger(coalesce(o.rescue_units, 0)) AS rescue_units
"""

ORGANIZATIONS_IN_ZONE = f"""
MATCH (o:Organization)
WHERE coalesce(o.active, true) = true
  AND (
    EXISTS {{ (o)-[:OPERATES_IN]->(:Zone {{id: $zone_id}}) }}
    OR EXISTS {{ (o)-[:COVERS]->(:Zone {{id: $zone_id}}) }}
  )
RETURN o.id AS id,
       {_ORG_PROPS.strip()}
""".strip()

ORGANIZATIONS_FALLBACK = f"""
MATCH (o:Organization)
WHERE coalesce(o.active, true) = true
RETURN o.id AS id,
       {_ORG_PROPS.strip()}
LIMIT 80
""".strip()
