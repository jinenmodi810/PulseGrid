# PulseGrid MVP data sources (internal)

Concise audit of what reads Neo4j / FastAPI vs local mock JSON as of this pass.

## Fully backend-backed (primary flows)

- **Auth:** registration + login + `/auth/me` (JWT, Neo4j writes/reads).
- **Victim:** help request submit (`POST /incidents/`), incident detail (`GET /incidents/{id}`), home profile (`victimProfileBySessionProvider`), active incident card (same detail API + last incident id in session).
- **Volunteer:** task list, profile, accept/complete (`VolunteerTasksRepository` → `/volunteers/...`, `/incidents/...`).
- **Organization:** overview, incidents list, capacity/actions (`OrganizationRepository` + coordinator where wired).
- **Incident tracking / task detail:** `HelpRequestRepository` + guidance providers hitting API where implemented.
- **Support directory:** `GET /support/contacts` → Neo4j `SupportContact` list (empty if none or read error).
- **Rewards catalog:** `GET /rewards/` → Neo4j `Reward` list (empty if none or read error); volunteer **credits** line comes from volunteer profile API, not the catalog JSON file.

## Partially real / hybrid

- **Rewards screen:** credits from live volunteer profile; catalog from API/Neo4j; static **badge** card is decorative until tied to earned rewards.
- **Admin inspection:** intended as Neo4j-backed dev console; verify separately from role MVP.
- **Routing / AI copy:** some strings describe future voice/Gemini behavior; backend may still use placeholders for parts of AI text.

## Still mock / local-only (intentional or legacy)

- **Global `IncidentRepository` / `VolunteerRepository` / hospitals / shelters / responders / routing** in `lib/app/providers.dart` still use `MockDataService` + `assets/json/mock_*.json`. **No feature screens in the main role loop were found consuming `incidentsProvider`**, but the providers remain for legacy/admin experiments—do not assume role UIs use them.
- **`RoutingRepository`:** mock routes JSON (not used in the core victim→volunteer→org loop unless a screen imports it explicitly).

## Real-time

- **WebSocket base URL** follows the same rules as `resolveApiBaseUrl()` (including Android emulator `10.0.2.2`).
- **Volunteer / org / incident channels** invalidate Riverpod providers on server events; **victim home** subscribes to `incidentRealtimeProvider` when a last incident id exists so the home card can refresh without opening tracking.

## Location

- **Primary:** zone id from registration, session, and help request form. **No live GPS** in this MVP; UI copy states zone-only routing on the help request form.
