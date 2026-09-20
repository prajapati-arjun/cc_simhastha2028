# Simhastha 2028 – Ujjain Digital Experience Platform — Sprint 1 (Phase 1: Foundation)

Source of truth: `Docs/PRD_extracted.txt` (full 49-section PRD body) and `Docs/PRD_tables.txt`
(target users, tech stack, NFRs, phased roadmap Table 6, backlog epics Table 7).
Original docx (correct UTF-8 Hindi if needed): `Docs/Simhastha_2028_Web_App_PRD.docx`.

## Mission
Idea to a locally-runnable, real full-stack product covering PRD Phase 1 "Foundation"
scope — without skipping QA. "Real users" this sprint = a real person can run the stack
locally end-to-end, not a public cloud deployment.

## Settled decisions (do not re-litigate)
1. Safety-critical features (SOS, missing-person, lost-found, emergency directory,
   crowd/CCTV analytics placeholders) are built full-depth against OUR OWN database with
   seeded/simulated data — NOT integrated with any live police/medical/CCTV/government
   system. Every such screen/API response must carry a visible
   "Demo prototype — not connected to live emergency dispatch" style banner/flag. No real
   facial recognition, biometrics, or live CCTV ingestion (PRD section 26: biometrics is
   not a default requirement — skip it entirely).
2. Deployment: docker-compose full stack (Postgres+PostGIS, Redis, FastAPI, Next.js).
   No real cloud provisioning, no live claims.
3. Scope = PRD Phase 1 (PRD_tables.txt Table 6) at MVP depth, P0 epics from Table 7
   (Identity & Access, Master Data, CMS, GIS, Emergency):
   - Homepage (PRD section 6)
   - Simhastha Calendar & Events (section 8) — CMS-sourced, not hardcoded
   - Temple & Spiritual Guide (section 13) — all 9 named temples, directory + detail
   - Ghats directory (basic)
   - Live GIS Map (section 9) — MapLibre + free OSM tiles, layer toggles
     (temples/ghats/emergency at minimum), static placeholder crowd/traffic layer
   - Emergency Services directory + SOS entry point (section 15) — seeded directory,
     SOS creates a simulated incident record
   - Lost & Found / Missing Persons (section 16) — public report forms persisting via
     real API + admin verification workflow stub
   - Multilingual scaffold (section 19/32) — i18n structure EN + HI minimum, placeholder
     translations flagged for review. AI assistant itself is OUT of scope (Phase 2).
   - Admin CMS (section 28, P0) — login + RBAC (Super Admin, Content Manager, Public
     User minimum, table structured to extend to full section 29 role list), create/
     edit/publish for Events, Announcements, Temples, Ghats, draft → published stub
     workflow.
   - Core public read/write APIs (section 37): GET /api/v1/events, GET /api/v1/temples,
     GET /api/v1/ghats/{id}/status, GET /api/v1/emergency/services,
     POST /api/v1/lost-found, POST /api/v1/missing-person

## Tech stack (PRD Table 4 — decided)
Frontend: Next.js + React + TypeScript + Tailwind CSS. Maps: MapLibre + free OSM tiles.
Backend: Python + FastAPI. DB: PostgreSQL + PostGIS (docker-compose postgis image).
Cache: Redis (wired in even if lightly used). OUT of scope this sprint: Kafka,
OpenSearch, computer vision, AI/RAG stack (Phase 2/3 per Table 6).

## Repo layout
`D:\Claude_Community` — git repo. `apps/web` (Next.js), `apps/api` (FastAPI), `infra`
(docker-compose etc.), `Docs` (PRD source material), `docs` (this sprint's prototype-
limitations/roadmap docs), `project-specs`, `project-tasks` (PM output).

## Required deliverables (verify each with evidence)
1. Monorepo scaffold, working `docker-compose up` (Postgres+PostGIS, Redis, FastAPI,
   Next.js). README.md with exact run instructions.
2. DB schema/migrations (Alembic) for: User/Role, Temple, Ghat, Event, Zone,
   EmergencyService, Announcement, LostFoundCase, MissingPersonCase, AuditLog.
3. Seed script: 9 named temples, sample ghats, sample events, sample emergency
   directory entries, at least one admin user.
4. Public APIs listed above working with curl/pytest evidence + input validation.
5. Frontend pages listed above rendering real API data (not hardcoded), with the
   demo/prototype safety banner where required.
6. Minimal admin CMS flow: log in, create event/announcement, publish, see it on the
   public site.
7. Automated tests: backend pytest API tests + frontend build/lint pass, with pass/fail
   counts as evidence.
8. `docs/PROTOTYPE_LIMITATIONS.md` — explicit list of simulated/out-of-scope items.
9. `docs/ROADMAP.md` — PRD Phases 2-4 (Table 6) + remaining P1-P3 epics (Table 7) as
   forward backlog.

## Team for this sprint
Core (always): Senior Project Manager, UX Architect, Frontend Developer,
Backend Architect (Backend Developer role), DevOps Automator.
Support (only if concretely needed): AI Engineer, Performance Benchmarker,
Infrastructure Maintainer — NOT expected to be needed this sprint (AI assistant and
load/infra work are Phase 2+ per PRD's own roadmap).
