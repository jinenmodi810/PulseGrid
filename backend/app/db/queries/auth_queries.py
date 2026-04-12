"""Cypher for registration flows.

TODO: optional unified :Identity node + unique composite constraints for email across roles
if product later requires one email / multiple roles.
"""

MERGE_USER_AND_ZONE = """
MERGE (u:User {id: $user_id})
SET u.full_name = $full_name,
    u.phone = $phone,
    u.preferred_language = $preferred_language,
    u.household_size = coalesce($household_size, $family_size, u.household_size, 1),
    u.family_size = coalesce($household_size, $family_size, u.family_size, 1),
    u.elderly_count = $elderly_count,
    u.mobility_concern = $mobility_concern,
    u.oxygen_dependency = $oxygen_dependency,
    u.emergency_contact_name = $emergency_contact_name,
    u.emergency_contact_phone = $emergency_contact_phone,
    u.emergency_contact_relationship = $emergency_contact_relationship,
    u.created_at = coalesce(u.created_at, datetime())
WITH u
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (u)-[:LOCATED_IN]->(z)
RETURN u.id AS user_id, z.id AS zone_id
"""

MERGE_VOLUNTEER_AND_ZONE = """
MERGE (v:Volunteer {id: $volunteer_id})
SET v.display_name = $full_name,
    v.phone = $phone,
    v.skill_type = $skill_type,
    v.skills = $skills,
    v.support_types = $support_types,
    v.languages = $languages,
    v.transport_access = $transport_access,
    v.availability = $availability,
    v.verified = $verified,
    v.created_at = coalesce(v.created_at, datetime()),
    v.credits = coalesce(v.credits, 0),
    v.trust_score = coalesce(v.trust_score, 0.5)
WITH v
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (v)-[:LOCATED_IN]->(z)
RETURN v.id AS volunteer_id, z.id AS zone_id
"""

MERGE_ORGANIZATION_AND_ZONE = """
MERGE (o:Organization {id: $organization_id})
SET o.name = $name,
    o.org_type = $org_type,
    o.phone = $phone,
    o.active = true,
    o.beds_available = coalesce($beds_available, o.beds_available, 0),
    o.oxygen_units = coalesce($oxygen_units, o.oxygen_units, 0),
    o.ambulances_available = coalesce($ambulances_available, o.ambulances_available, 0),
    o.shelter_units = coalesce($shelter_units, o.shelter_units, 0),
    o.food_capacity_units = coalesce($food_capacity_units, o.food_capacity_units, 0),
    o.rescue_units = coalesce($rescue_units, o.rescue_units, 0),
    o.zone_id = $zone_id,
    o.created_at = coalesce(o.created_at, datetime())
WITH o
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (o)-[:OPERATES_IN]->(z)
RETURN o.id AS organization_id, z.id AS zone_id
"""

GET_USER_BY_ID = """
MATCH (u:User {id: $user_id})
OPTIONAL MATCH (u)-[:LOCATED_IN]->(z:Zone)
RETURN u.id AS user_id,
       coalesce(u.email, '') AS email,
       coalesce(u.full_name, '') AS full_name,
       coalesce(u.phone, '') AS phone,
       coalesce(u.preferred_language, 'en') AS preferred_language,
       coalesce(z.id, '') AS zone_id,
       toInteger(coalesce(u.household_size, u.family_size, 1)) AS household_size,
       toInteger(coalesce(u.elderly_count, 0)) AS elderly_count,
       coalesce(u.mobility_concern, false) AS mobility_concern,
       coalesce(u.oxygen_dependency, false) AS oxygen_dependency,
       coalesce(u.emergency_contact_name, '') AS emergency_contact_name,
       coalesce(u.emergency_contact_phone, '') AS emergency_contact_phone,
       coalesce(u.emergency_contact_relationship, '') AS emergency_contact_relationship
"""

# --- Email/password MVP (User = victim) ---

FIND_USER_BY_EMAIL = """
MATCH (u:User) WHERE toLower(trim(u.email)) = toLower(trim($email))
RETURN u.id AS id,
       coalesce(u.password_hash, '') AS password_hash,
       coalesce(u.email, '') AS email
LIMIT 1
"""

CREATE_USER_WITH_PASSWORD = """
CREATE (u:User {
  id: $user_id,
  email: $email,
  password_hash: $password_hash,
  full_name: $full_name,
  phone: $phone,
  preferred_language: $preferred_language,
  household_size: coalesce($household_size, 1),
  family_size: coalesce($household_size, 1),
  elderly_count: $elderly_count,
  mobility_concern: $mobility_concern,
  oxygen_dependency: $oxygen_dependency,
  emergency_contact_name: $emergency_contact_name,
  emergency_contact_phone: $emergency_contact_phone,
  emergency_contact_relationship: $emergency_contact_relationship,
  created_at: datetime()
})
WITH u
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (u)-[:LOCATED_IN]->(z)
RETURN u.id AS user_id, z.id AS zone_id
"""

# --- Volunteer ---

FIND_VOLUNTEER_BY_EMAIL = """
MATCH (v:Volunteer) WHERE toLower(trim(v.email)) = toLower(trim($email))
RETURN v.id AS id,
       coalesce(v.password_hash, '') AS password_hash,
       coalesce(v.email, '') AS email
LIMIT 1
"""

CREATE_VOLUNTEER_WITH_PASSWORD = """
CREATE (v:Volunteer {
  id: $volunteer_id,
  email: $email,
  password_hash: $password_hash,
  display_name: $full_name,
  phone: $phone,
  skill_type: $skill_type,
  skills: $skills,
  support_types: $support_types,
  languages: $languages,
  transport_access: $transport_access,
  availability: $availability,
  verified: $verified,
  credits: 0,
  trust_score: 0.5,
  created_at: datetime()
})
WITH v
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (v)-[:LOCATED_IN]->(z)
RETURN v.id AS volunteer_id, z.id AS zone_id
"""

# --- Organization (contact email login) ---

FIND_ORGANIZATION_BY_CONTACT_EMAIL = """
MATCH (o:Organization) WHERE toLower(trim(o.contact_email)) = toLower(trim($email))
RETURN o.id AS id,
       coalesce(o.password_hash, '') AS password_hash,
       coalesce(o.contact_email, '') AS email
LIMIT 1
"""

CREATE_ORGANIZATION_WITH_PASSWORD = """
CREATE (o:Organization {
  id: $organization_id,
  name: $name,
  org_type: $org_type,
  phone: $contact_phone,
  contact_name: $contact_name,
  contact_email: $contact_email,
  password_hash: $password_hash,
  active: true,
  beds_available: coalesce($beds_available, 0),
  oxygen_units: coalesce($oxygen_units, 0),
  ambulances_available: coalesce($ambulances_available, 0),
  shelter_units: coalesce($shelter_units, 0),
  food_capacity_units: coalesce($food_capacity_units, 0),
  rescue_units: coalesce($rescue_units, 0),
  zone_id: $zone_id,
  created_at: datetime()
})
WITH o
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (o)-[:OPERATES_IN]->(z)
RETURN o.id AS organization_id, z.id AS zone_id
"""

MERGE_ORGANIZATION_COVERS_ZONES = """
MATCH (o:Organization {id: $organization_id})
UNWIND $zone_ids AS zid
MERGE (cz:Zone {id: zid})
ON CREATE SET cz.name = zid
MERGE (o)-[:COVERS]->(cz)
RETURN count(*) AS linked
"""

GET_USER_ME = """
MATCH (u:User {id: $user_id})
OPTIONAL MATCH (u)-[:LOCATED_IN]->(z:Zone)
RETURN u.id AS id,
       coalesce(u.email, '') AS email,
       coalesce(u.full_name, '') AS full_name,
       coalesce(u.phone, '') AS phone,
       coalesce(u.preferred_language, 'en') AS preferred_language,
       coalesce(z.id, '') AS zone_id,
       toInteger(coalesce(u.household_size, u.family_size, 1)) AS household_size,
       toInteger(coalesce(u.elderly_count, 0)) AS elderly_count,
       coalesce(u.mobility_concern, false) AS mobility_concern,
       coalesce(u.oxygen_dependency, false) AS oxygen_dependency,
       coalesce(u.emergency_contact_name, '') AS emergency_contact_name,
       coalesce(u.emergency_contact_phone, '') AS emergency_contact_phone,
       coalesce(u.emergency_contact_relationship, '') AS emergency_contact_relationship
"""

GET_VOLUNTEER_ME = """
MATCH (v:Volunteer {id: $volunteer_id})
OPTIONAL MATCH (v)-[:LOCATED_IN]->(z:Zone)
RETURN v.id AS id,
       coalesce(v.email, '') AS email,
       coalesce(v.display_name, '') AS display_name,
       coalesce(v.phone, '') AS phone,
       coalesce(v.skills, []) AS skills,
       coalesce(v.support_types, []) AS support_types,
       coalesce(v.languages, []) AS languages,
       coalesce(v.transport_access, '') AS transport_access,
       coalesce(v.availability, '') AS availability,
       coalesce(v.credits, 0) AS credits,
       coalesce(v.trust_score, 0.5) AS trust_score,
       coalesce(z.id, '') AS zone_id
"""

GET_ORGANIZATION_ME = """
MATCH (o:Organization {id: $organization_id})
RETURN o.id AS id,
       coalesce(o.contact_email, '') AS email,
       coalesce(o.name, '') AS organization_name,
       coalesce(o.org_type, '') AS org_type,
       coalesce(o.phone, '') AS contact_phone,
       coalesce(o.contact_name, '') AS contact_name,
       coalesce(o.zone_id, '') AS zone_id,
       coalesce(o.beds_available, 0) AS beds_available,
       coalesce(o.oxygen_units, 0) AS oxygen_units,
       coalesce(o.ambulances_available, 0) AS ambulances_available,
       coalesce(o.shelter_units, 0) AS shelter_units,
       coalesce(o.food_capacity_units, 0) AS food_capacity_units,
       coalesce(o.rescue_units, 0) AS rescue_units,
       coalesce(o.active, true) AS active
"""
