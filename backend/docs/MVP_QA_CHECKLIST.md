# PulseGrid MVP QA checklist (internal)

Run backend locally; set Flutter `.env` `API_BASE_URL` if not using defaults (`http://127.0.0.1:8000` on iOS simulator, `http://10.0.2.2:8000` on Android emulator).

## Health / persistence probes

- [ ] `GET /health` → `{"ok": true}`
- [ ] `GET /debug/neo4j-health` → `connected: true` (fix `backend/.env` if false)
- [ ] `GET /debug/persistence-summary` → counts increase after registrations/incidents (dev-only)

## A. Victim

- [ ] Register (victim) → lands victim home; no success if API error
- [ ] Sign in → lands victim home
- [ ] Force-close app → reopen → victim home (token + `/auth/me` path)
- [ ] Request help → `POST /incidents/` success → tracking/detail loads real `GET /incidents/{id}`
- [ ] With open incident: volunteer accept/complete (separate device or role) → victim home card or tracking updates without manual refresh (WS + invalidation)

## B. Volunteer

- [ ] Register / sign in → volunteer home
- [ ] Reopen app → volunteer home
- [ ] Task feed shows API tasks; accept + complete persist; profile credits refresh (WS invalidation)
- [ ] Rewards screen: credits from profile API; catalog from `GET /rewards/`

## C. Organization

- [ ] Register / sign in → org dashboard
- [ ] Reopen app → org dashboard
- [ ] Incidents list matches API; capacity / accept / status mutations persist in Neo4j

## D. Real-time

- [ ] Create incident → volunteer in zone receives WS event and feed refreshes
- [ ] Accept / complete → incident channel + victim tracking providers refresh

## E. Routing

- [ ] `/login/victim`, `/login/volunteer`, `/login/organization` render (no GoRouter not-found)
- [ ] Legacy aliases redirect: `/victim/login` → victim login, etc.
- [ ] Unknown path → not-found screen with link to landing

## F. False success

- [ ] Stop API → registration/login/help request show user-visible errors, not silent success
