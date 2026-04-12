# PulseGrid response engine — internal audit (not user-facing)

Deterministic rule-based routing only; no Bayesian / Hungarian / min-cost flow / Dijkstra unless explicitly added later.

## Implemented

- **Neo4j**: `User`, `Volunteer`, `Organization`, `Zone`, `Incident`; relationships `REPORTED`, `LOCATED_IN`, `ASSIGNED_TO`, `OPERATES_IN` (org–zone), `MERGE` incident–zone.
- **Victim profile** (`GET_USER_PROFILE_FOR_INCIDENT`): household, elderly count, mobility, oxygen dependency, preferred language, emergency contact — used for enrichment and tier input.
- **Volunteer profile** (matching): zone via `LOCATED_IN`, availability, support_types/skills, languages, transport_access, trust_score, credits.
- **Organization** (matching): org_type, zone_id, active, verified, beds/oxygen/ambulance/shelter/food/rescue units; zone query prefers `OPERATES_IN` + `COVERS` on same zone.
- **Incident**: full SOS flags, priority, AI guidance placeholder, response_tier, escalation, decision_summary, tier_reasons_json, rejected volunteers/orgs, assigned org as properties, intake_source (when set).
- **Response tier** (`response_tier_service`): deterministic plan + `finalize_response_after_matching` for post-match tier text and escalation.
- **Volunteer matching** (`graph_matching_service`): zone-first, then other zones; hard rejects (unavailable, no transport); soft scoring (support, language, trust).
- **Organization matching** (`organization_matching_service`): in-zone + fallback; capacity and disaster-type rules; explicit rejection strings.
- **WebSockets**: dashboard, `incident:{id}`, `volunteer:{id}`; org channel `organization:{id}` added in this phase.
- **SOS path**: `POST /incidents` → profile merge → priority → tier → match → persist → background broadcast.
- **Location / zone**: same-zone preference in scoring; TODO hooks for Maps/ETA in tier input and AI placeholder.

## Partially implemented

- **AI guidance**: static placeholder text; no Gemini/stream.
- **ETA**: fixed minutes from zone sameness, not traffic.
- **Coordinator overrides**: reassign/escalate exist; org channel may not fire on every coordinator path (focus was create flow).

## Missing / future

- **ElevenLabs / STT**: `VoiceSosIntakeStub` + `/incidents/voice-intake/preview` stub; client placeholder only.
- **Google Maps**: lat/lng on incidents, ETA, blockage, airlift — TODO on `ResponseEngineInput` / tier input.
- **Multi-worker WebSockets**: in-memory `ConnectionManager` only.
- **Hungarian / global assignment**: not used; parallel incidents can compete for same volunteer (last write wins on assign).

## Risky / inconsistent (mitigated where noted)

- **Org graph edge**: incidents historically property-linked to org; `ROUTED_FOR` edge added on assign for graph traversals — list queries still use `assigned_organization_id`.
- **Verified org**: Cypher defaults `verified` true when missing — unverified orgs must set `verified: false` in graph to reject.
- **Volunteer nearby feed**: previously only assigned volunteers got WS refresh; zone fan-out on create added for open-queue UX.
