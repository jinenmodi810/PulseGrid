// PulseGrid graph schema (Neo4j AuraDB / Neo4j 5+)
// Run this file once in Neo4j Browser or via cypher-shell against your Aura instance.
//
// Node labels: User, Incident, Volunteer, Responder, Hospital, Shelter,
//             SupportContact, Zone, Reward, Organization
//
// Relationship types (domain):
//   REPORTED          (User)-[:REPORTED]->(Incident)
//   LOCATED_IN        (Incident)-[:LOCATED_IN]->(Zone)
//   CAN_HELP_WITH     (Volunteer)-[:CAN_HELP_WITH]->(Incident)
//   AVAILABLE_FOR     (Volunteer)-[:AVAILABLE_FOR]->(Zone)
//   ASSIGNED_TO       (Volunteer|Responder)-[:ASSIGNED_TO]->(Incident)
//   ROUTE_TO          (Incident)-[:ROUTE_TO]->(Hospital|Shelter)
//   BLOCKED_ROUTE     (Zone)-[:BLOCKED_ROUTE]->(Zone)
//   REFERRED_TO       (Incident)-[:REFERRED_TO]->(Hospital|Shelter)
//   EARNED_REWARD     (User|Volunteer)-[:EARNED_REWARD]->(Reward)
//   VERIFIED_BY       (Incident)-[:VERIFIED_BY]->(Responder)
//   SUPPORTS          (SupportContact)-[:SUPPORTS]->(Zone|Incident)

// --- Unique id constraints (one per label) ---

CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (n:User) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT incident_id_unique IF NOT EXISTS
FOR (n:Incident) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT volunteer_id_unique IF NOT EXISTS
FOR (n:Volunteer) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT responder_id_unique IF NOT EXISTS
FOR (n:Responder) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT hospital_id_unique IF NOT EXISTS
FOR (n:Hospital) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT shelter_id_unique IF NOT EXISTS
FOR (n:Shelter) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT support_contact_id_unique IF NOT EXISTS
FOR (n:SupportContact) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT zone_id_unique IF NOT EXISTS
FOR (n:Zone) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reward_id_unique IF NOT EXISTS
FOR (n:Reward) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT organization_id_unique IF NOT EXISTS
FOR (n:Organization) REQUIRE n.id IS UNIQUE;

// --- Identity uniqueness (registration/login safety) ---

CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (n:User) REQUIRE n.email IS UNIQUE;

CREATE CONSTRAINT volunteer_email_unique IF NOT EXISTS
FOR (n:Volunteer) REQUIRE n.email IS UNIQUE;

CREATE CONSTRAINT organization_contact_email_unique IF NOT EXISTS
FOR (n:Organization) REQUIRE n.contact_email IS UNIQUE;
