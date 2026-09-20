# Simhastha 2028 – Sprint 1 (Phase 1 "Foundation") Development Tasks

## Specification Summary
**Source of truth**: `project-specs/simhastha-sprint1-setup.md` (settled decisions — not
re-litigated here) + PRD Phase 1 scope (`Docs/PRD_tables.txt` Table 6: "Architecture, CMS,
GIS, master data, public website, core APIs") + P0 epics (Table 7: Identity & Access,
Master Data, CMS, GIS, Emergency).

**Explicitly OUT of scope this sprint** (do not build): AI assistant/RAG (PRD §19, §27),
Kafka/OpenSearch/real-time streaming (§38), CCTV/computer-vision analytics (§26 — biometrics
skipped entirely per spec), Pilgrimage Planner (§7), Parking availability API, Crowd/Traffic
zone APIs, Volunteer/Vendor platforms (§22/§23), Command Center (§24), Digital Twin (§46).
These belong in `docs/ROADMAP.md` as forward backlog, not in Sprint 1 code.

**Technical Stack** (PRD Table 4, fixed by spec): Frontend — Next.js + React + TypeScript +
Tailwind CSS, MapLibre + free OSM tiles. Backend — Python + FastAPI. DB — PostgreSQL +
PostGIS. Cache — Redis (wired in, lightly used). Deployment — docker-compose only, no cloud
provisioning.

**Target Timeline**: Single sprint; no phased sub-milestones given in spec — treat as one
delivery with the dependency order below governing execution sequence.

**Critical safety-banner rule** (spec decision #1): every SOS/missing-person/lost-found/
emergency-directory/crowd-CCTV-placeholder screen or API response must carry a visible
"Demo prototype — not connected to live emergency dispatch" style banner/flag. This is a
cross-cutting requirement, not a single task — it is called out per-task below wherever it
applies (UX-02, BE-08, BE-11, BE-12, FE-08, FE-09).

---

## Dependency Order (critical path)

1. **DO-01 (repo scaffold) → DO-02 (docker-compose)** — nothing else can run without a
   working local stack.
2. **UX-01/UX-02 (design system, page inventory, safety-banner pattern)** can start in
   parallel with DevOps from day one — no code dependency, only informs FE work.
3. **BE-01 (DB schema/migrations) → BE-02 (seed script) → BE-03…BE-08 (the 6 public APIs)
   → BE-09 (admin auth/RBAC) → BE-10 (admin CRUD+draft/publish) → BE-13 (pytest suite,
   can be written incrementally alongside each API).**
4. **Frontend pages depend on their corresponding API being live**: FE-02 (Homepage) needs
   BE-04+BE-06; FE-03 (Calendar/Events) needs BE-04; FE-04 (Temple directory+detail) needs
   BE-05; FE-05 (Ghats) needs BE-05 (ghat status endpoint); FE-06 (GIS Map) needs BE-05
   (temples/ghats geo data) + BE-06 (emergency); FE-07 (Emergency directory+SOS) needs BE-06;
   FE-08/FE-09 (Lost & Found / Missing Person forms) need BE-07/BE-08; FE-10 (Admin CMS UI)
   needs BE-09+BE-10.
5. **FE-01 (Next.js scaffold + i18n scaffold + Tailwind config)** must land before any page
   task (FE-02 through FE-10).
6. **Documentation tasks (DOC-01, DOC-02)** are independent of code and can be drafted early
   but finalized last, once actual scope/limitations are known.
7. **Parallelizable groups**:
   - DO-01/DO-02 (infra) ‖ UX-01/UX-02 (design) can start simultaneously on day 1.
   - Once BE-01 lands, BE-02 (seed) and the individual API tasks BE-03–BE-08 can be split
     across backend contributors in parallel (each API touches different entities).
   - Once FE-01 lands and its dependent API is live, FE-02–FE-09 (public pages) can be built
     in parallel by different frontend contributors since they are largely independent routes.
   - DOC-01/DOC-02 can be drafted in parallel with everything else, finalized at the end.

---

## 1. DevOps / Infra Tasks

- [ ] DO-01: Scaffold monorepo layout per spec repo layout (`apps/web`, `apps/api`, `infra`,
  `docs`) with placeholder READMEs so each app directory is a valid Next.js / FastAPI project
  root (owner: DevOps Automator). No dependency — can start immediately.
- [ ] DO-02: Write `docker-compose.yml` in `infra/` bringing up Postgres+PostGIS, Redis,
  FastAPI, and Next.js exactly as required by spec deliverable #1 ("Monorepo scaffold,
  working `docker-compose up` (Postgres+PostGIS, Redis, FastAPI, Next.js)") (owner: DevOps
  Automator). Depends on DO-01.
- [ ] DO-03: Root `README.md` with exact run instructions ("README.md with exact run
  instructions" per spec deliverable #1) — `docker-compose up`, env var setup, how to run
  migrations/seed, how to run pytest and frontend build/lint (owner: DevOps Automator).
  Depends on DO-02 and BE-02/BE-13/FE-11 existing (finalize last, draft early).
- [ ] DO-04: Base Dockerfiles for `apps/api` (Python/FastAPI) and `apps/web` (Next.js) used
  by docker-compose, plus `.env.example` covering DB/Redis connection strings (owner: DevOps
  Automator). Depends on DO-01, feeds DO-02.
- [ ] DO-05: Dev tooling — Alembic config wiring inside the API container, hot-reload for
  both services in docker-compose for local dev loop (owner: DevOps Automator). Depends on
  DO-02, feeds BE-01 (Alembic migrations need a running container to run against).

**Parallel**: DO-01 → DO-04 → DO-02 → DO-05 is mostly sequential (each builds the container
the next needs); DO-03 (README) is written last once other pieces exist but can be drafted
early.

---

## 2. UX / Design System Tasks

- [ ] UX-01: Page inventory for all Sprint 1 public pages exactly matching spec scope list:
  Homepage, Calendar & Events, Temple directory + 9 temple detail pages, Ghats directory,
  Live GIS Map, Emergency Services directory + SOS entry point, Lost & Found form, Missing
  Person form, plus Admin CMS screens (login, events/announcements/temples/ghats
  create-edit-publish) (owner: UX Architect). No dependency — start day 1.
- [ ] UX-02: Define the reusable "Demo prototype — not connected to live emergency dispatch"
  safety-banner component pattern (visual spec, placement rules, which screens/API responses
  require it per spec decision #1: SOS, missing-person, lost-found, emergency directory,
  crowd/CCTV placeholder) (owner: UX Architect). No dependency — start day 1, feeds FE-06,
  FE-07, FE-08, FE-09.
- [ ] UX-03: Define component structure/spacing/color system in Tailwind config terms
  (design tokens: colors, spacing scale, typography) to hand to Frontend Developer as a
  starting Tailwind theme (owner: UX Architect). No dependency — start day 1, feeds FE-01.
- [ ] UX-04: Define multilingual (EN + HI) layout pattern — language selector placement per
  PRD §6 "Multilingual interface selector" and §19/§32 i18n scaffold requirement from spec
  (owner: UX Architect). Feeds FE-11 (i18n scaffold).
- [ ] UX-05: Define GIS Map layer-toggle UI pattern (temples/ghats/emergency layers minimum
  per spec, static placeholder crowd/traffic layer) per PRD §9 "The map should support layer
  controls, search, route planning... real-time status" (scoped down: layer toggles only,
  no routing/search this sprint per settled decision) (owner: UX Architect). Feeds FE-06.

**Parallel**: UX-01 through UX-05 have no dependencies on each other or on backend/DevOps —
all can run in parallel from day 1, ideally UX-01/UX-02 completed first since they gate the
most downstream frontend work.

---

## 3. Backend Tasks

- [ ] BE-01: Alembic migrations for all entities named in spec deliverable #2: User/Role,
  Temple, Ghat, Event, Zone, EmergencyService, Announcement, LostFoundCase,
  MissingPersonCase, AuditLog (owner: Backend Architect). Depends on DO-05 (DB container +
  Alembic wiring). Blocks everything else in this section.
- [ ] BE-02: Seed script per spec deliverable #3: "9 named temples, sample ghats, sample
  events, sample emergency directory entries, at least one admin user" — the 9 temples must
  be exactly: Mahakaleshwar, Kal Bhairav, Harsiddhi, Mangalnath, Gadkalika, Chintaman Ganesh,
  Sandipani Ashram, 84 Mahadev, Panchkroshi Yatra (PRD §13) (owner: Backend Architect).
  Depends on BE-01.
- [ ] BE-03: Zone model support (used by Temple/Ghat/EmergencyService geo association per
  PostGIS) — no dedicated public zone API this sprint (crowd/traffic zone APIs are out of
  scope), Zone exists purely as master-data schema per spec deliverable #2 (owner: Backend
  Architect). Depends on BE-01.
- [ ] BE-04: `GET /api/v1/events` — returns CMS-sourced events, matching spec requirement
  "Simhastha Calendar & Events (section 8) — CMS-sourced, not hardcoded" (owner: Backend
  Architect). Depends on BE-01, BE-02.
- [ ] BE-05: `GET /api/v1/temples` and `GET /api/v1/ghats/{id}/status` — temple directory
  data for all 9 named temples per PRD §13, and ghat status endpoint per spec scope "Ghats
  directory (basic)" (owner: Backend Architect). Depends on BE-01, BE-02.
- [ ] BE-06: `GET /api/v1/emergency/services` — seeded emergency directory per spec "Emergency
  Services directory + SOS entry point (section 15) — seeded directory"; response must
  include the demo-prototype banner flag per spec decision #1 (owner: Backend Architect).
  Depends on BE-01, BE-02.
- [ ] BE-07: `POST /api/v1/lost-found` — persists lost/found item reports via real API per
  spec "public report forms persisting via real API"; fields per PRD §16 "category,
  description, image, location and time" (owner: Backend Architect). Depends on BE-01.
- [ ] BE-08: `POST /api/v1/missing-person` — persists missing-person reports via real API;
  response/flow must carry the demo-prototype safety banner per spec decision #1 since this
  is a safety-critical feature simulated against our own DB (owner: Backend Architect).
  Depends on BE-01.
- [ ] BE-09: Admin authentication + RBAC per spec "Admin CMS (section 28, P0) — login + RBAC
  (Super Admin, Content Manager, Public User minimum, table structured to extend to full
  section 29 role list)" — implement the 3 minimum roles with a roles table designed to
  extend to the full PRD §29 list (Super Admin, Department Admin, Zone Admin,
  Police/Security Admin, Medical Admin, Content Manager, Volunteer, Vendor, Public User)
  (owner: Backend Architect). Depends on BE-01.
- [ ] BE-10: Admin CRUD + draft/publish workflow stub for Events, Announcements, Temples,
  Ghats per spec "create/edit/publish for Events, Announcements, Temples, Ghats, draft →
  published stub workflow" (owner: Backend Architect). Depends on BE-01, BE-09.
- [ ] BE-11: SOS incident creation flow — "SOS creates a simulated incident record" per spec
  decision #1; must carry the demo-prototype banner in the response (owner: Backend
  Architect). Depends on BE-01, BE-06.
- [ ] BE-12: Input validation on all 6 public APIs (spec deliverable #4: "Public APIs listed
  above working with curl/pytest evidence + input validation") — request schema validation
  via Pydantic on lost-found and missing-person POST bodies especially (owner: Backend
  Architect). Depends on BE-04 through BE-08.
- [ ] BE-13: Pytest API tests for all 6 public APIs with pass/fail counts as evidence per
  spec deliverable #7 "backend pytest API tests... with pass/fail counts as evidence" (owner:
  Backend Architect). Depends on BE-04 through BE-12 (write incrementally alongside each API,
  finalize once all APIs exist).
- [ ] BE-14: AuditLog wiring for sensitive case actions per PRD §16 "Audit trail for
  sensitive cases" and spec deliverable #2 AuditLog table — log admin publish actions and
  missing-person/lost-found case state changes (owner: Backend Architect). Depends on BE-08,
  BE-10.

**Parallel**: BE-03 through BE-08 (each a distinct entity/endpoint) can be split across
backend contributors once BE-01+BE-02 land. BE-09 (auth/RBAC) can start in parallel with
BE-03–BE-08 since it only depends on BE-01. BE-10 depends on BE-09. BE-11 depends on BE-06.
BE-12/BE-13 are cross-cutting and trail the individual endpoint tasks.

---

## 4. Frontend Tasks

- [ ] FE-01: Next.js + TypeScript + Tailwind scaffold using UX-03 design tokens, base layout
  with header/footer shell (owner: Frontend Developer). Depends on DO-01, UX-03. Blocks all
  page tasks below.
- [ ] FE-02: Homepage per PRD §6 requirements: "Prominent Simhastha 2028 identity...
  Primary calls to action: Plan Your Journey, Explore Map, Events, Emergency... Today's
  events and important announcements. Quick access to temples, ghats, transport and
  essential services. Multilingual interface selector. Persistent emergency access on mobile
  devices." — note: "Live status indicators for crowd, traffic, parking" is scoped OUT this
  sprint (no crowd/traffic/parking APIs exist) — use static placeholder only if included at
  all (owner: Frontend Developer). Depends on FE-01, BE-04, BE-06.
- [ ] FE-03: Calendar & Events page per spec "Simhastha Calendar & Events (section 8) —
  CMS-sourced, not hardcoded" — render `GET /api/v1/events` data, display last-updated
  timestamp per PRD §8 (owner: Frontend Developer). Depends on FE-01, BE-04.
- [ ] FE-04: Temple directory + 9 individual temple detail pages (Mahakaleshwar, Kal Bhairav,
  Harsiddhi, Mangalnath, Gadkalika, Chintaman Ganesh, Sandipani Ashram, 84 Mahadev,
  Panchkroshi Yatra) per PRD §13 "Each destination page should contain location,
  significance, timings, crowd status where available, transport, accessibility, route,
  instructions and verified information" — scope down "crowd status" to static/none since no
  crowd API exists this sprint (owner: Frontend Developer). Depends on FE-01, BE-05.
- [ ] FE-05: Ghats directory (basic) per spec scope, consuming `GET
  /api/v1/ghats/{id}/status` (owner: Frontend Developer). Depends on FE-01, BE-05.
- [ ] FE-06: Live GIS Map using MapLibre + free OSM tiles per spec "Live GIS Map (section 9)
  — MapLibre + free OSM tiles, layer toggles (temples/ghats/emergency at minimum), static
  placeholder crowd/traffic layer" — apply UX-05 layer-toggle pattern and UX-02 banner where
  the placeholder crowd/traffic layer is shown (owner: Frontend Developer). Depends on FE-01,
  BE-05, BE-06, UX-05.
- [ ] FE-07: Emergency Services directory + SOS entry point per spec — consumes
  `GET /api/v1/emergency/services` and triggers BE-11 SOS flow; must display the
  "Demo prototype — not connected to live emergency dispatch" banner per spec decision #1 and
  UX-02 pattern (owner: Frontend Developer). Depends on FE-01, BE-06, BE-11, UX-02.
- [ ] FE-08: Lost & Found public report form (category, description, image, location, time
  per PRD §16) posting to `POST /api/v1/lost-found`, with demo-prototype banner per UX-02
  (owner: Frontend Developer). Depends on FE-01, BE-07, UX-02.
- [ ] FE-09: Missing Person public report form posting to `POST /api/v1/missing-person`, with
  demo-prototype safety banner per spec decision #1 and UX-02 pattern (owner: Frontend
  Developer). Depends on FE-01, BE-08, UX-02.
- [ ] FE-10: Admin CMS UI — login screen + RBAC-gated create/edit/publish views for Events,
  Announcements, Temples, Ghats per spec "Admin CMS... login + RBAC... create/edit/publish
  for Events, Announcements, Temples, Ghats, draft → published stub workflow" (owner:
  Frontend Developer). Depends on FE-01, BE-09, BE-10.
- [ ] FE-11: i18n scaffold EN + HI per spec "Multilingual scaffold (section 19/32) — i18n
  structure EN + HI minimum, placeholder translations flagged for review" — wire into FE-01
  base layout using UX-04 pattern; explicitly do NOT build the AI assistant (spec: "AI
  assistant itself is OUT of scope (Phase 2)") (owner: Frontend Developer). Depends on FE-01,
  UX-04.
- [ ] FE-12: Build/lint pass across `apps/web` with evidence per spec deliverable #7
  "frontend build/lint pass, with pass/fail counts as evidence" (owner: Frontend Developer).
  Depends on FE-02 through FE-11 (run once all pages exist, then fix as needed).

**Parallel**: Once FE-01 + relevant backend API are ready, FE-02 through FE-09 can be built
in parallel by different frontend contributors (independent routes/components). FE-10 and
FE-11 are also independent of FE-02–FE-09 once their own dependencies (BE-09/BE-10, UX-04)
are met. FE-12 is the final integration/verification step.

---

## 5. Documentation Tasks

- [ ] DOC-01: `docs/PROTOTYPE_LIMITATIONS.md` per spec deliverable #8 — explicit list of
  simulated/out-of-scope items: no live police/medical/CCTV/government system integration
  (spec decision #1), no real facial recognition/biometrics (PRD §26, explicitly skipped),
  no cloud deployment (spec decision #2, docker-compose only), Kafka/OpenSearch/AI-RAG/
  computer vision out of scope (tech stack note), Pilgrimage Planner/Parking/Crowd-Traffic
  APIs/Volunteer/Vendor/Command Center/Digital Twin not built this sprint (owner: Senior
  Project Manager or UX Architect, writer TBD). No code dependency — draft early, finalize
  once BE-11/FE-06/FE-07 land so the list matches actual shipped simulated features.
- [ ] DOC-02: `docs/ROADMAP.md` per spec deliverable #9 — PRD Phases 2-4 (Table 6: Phase 2
  Pilgrim Platform — trip planner, live map enhancements, parking, transport, PWA, AI
  assistant; Phase 3 Operations — command center, crowd analytics, traffic, incidents,
  emergency; Phase 4 Event Operations — real-time monitoring, alerts, operational AI and
  analytics) plus remaining P1-P3 epics from Table 7 (Pilgrimage Planner, Events P1, Parking,
  Transport, PWA/Offline, AI Assistant, Crowd Analytics, Command Center — all P1; Volunteer,
  Vendor — P2; Digital Twin — P3) as forward backlog (owner: Senior Project Manager). No code
  dependency — can be drafted at any time, purely derived from PRD tables already read.

**Parallel**: DOC-01 and DOC-02 have no code dependencies and can be drafted in parallel with
all other workstreams from day 1; DOC-01 should be finalized last (after safety-critical
features ship) to ensure accuracy.

---

## Quality Requirements
- [ ] All FluxUI/component usage (if any UI kit is introduced) uses supported props only —
  N/A this sprint per fixed stack (Next.js/Tailwind, no FluxUI in spec's tech stack).
- [ ] No background processes in any commands — never append `&`.
- [ ] No server startup commands assumed by tasks — docker-compose is the only startup path,
  per spec deliverable #1.
- [ ] Mobile responsive design required (PRD §6 "Persistent emergency access on mobile
  devices", §32 accessibility).
- [ ] Form functionality must work: Lost & Found (FE-08) and Missing Person (FE-09) forms
  must actually persist via BE-07/BE-08.
- [ ] Every safety-critical screen/API response (SOS, missing-person, lost-found, emergency
  directory, crowd/CCTV placeholder) carries the demo-prototype banner per spec decision #1 —
  verify on BE-06, BE-08, BE-11, FE-06, FE-07, FE-08, FE-09 before calling them done.
- [ ] Backend pytest evidence (BE-13) and frontend build/lint evidence (FE-12) both required
  per spec deliverable #7, with pass/fail counts reported, not just "tests exist."

## Technical Notes
**Development Stack**: Next.js + React + TypeScript + Tailwind CSS (frontend); MapLibre +
free OSM tiles (maps); Python + FastAPI (backend); PostgreSQL + PostGIS (DB); Redis (cache,
lightly used); docker-compose (deployment) — all fixed by spec, do not substitute.
**Special Instructions**: Do not re-litigate the settled decisions in the spec (safety-banner
requirement, docker-compose-only deployment, Phase 1 scope boundary). Do not add
Kafka/OpenSearch/computer-vision/AI-RAG even though they appear in PRD Table 4 — spec
explicitly marks them out of scope this sprint.
**Timeline Expectations**: This is a foundation sprint covering 9 public-facing feature areas
plus a minimal admin CMS — realistic scope is a working MVP-depth slice of each, not
polished/luxury implementations. Expect 2-3 revision cycles on GIS map layer toggles and the
admin draft/publish workflow, which are the most novel pieces for a first pass.
