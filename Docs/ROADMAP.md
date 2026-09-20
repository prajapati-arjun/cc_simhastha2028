# Simhastha 2028 — Forward Roadmap (post-Sprint 1)

Sprint 1 delivered PRD **Phase 1 – Foundation** at MVP depth. This document captures
everything that remains, so the next sprint starts from a known backlog rather than a
re-read of the PRD.

Sources: `Docs/PRD_tables.txt` Table 6 (phased delivery roadmap) and Table 7 (initial
product backlog with priorities), plus the PRD section bodies in
`Docs/PRD_extracted.txt`.

---

## Where Sprint 1 landed

| Table 7 Epic | Priority | Sprint 1 status |
|---|---|---|
| Identity & Access | P0 | **Partial** — admin login, JWT, 3-role RBAC, seeded users. MFA, OAuth2/OIDC, public OTP accounts deferred (PRD §30). |
| Master Data | P0 | **Done (MVP)** — Temple, Ghat, Zone, EmergencyService entities + seed. Parking, Hospital, PoliceStation, Accommodation entities not modelled. |
| CMS | P0 | **Partial** — Events, Announcements, Temples, Ghats with a two-state draft→published stub. Full §28 five-stage workflow deferred. |
| GIS | P0 | **Partial** — MapLibre + OSM tiles, static layer toggles. Routing, search, live layers deferred. |
| Emergency | P0 | **Partial (simulated)** — directory, SOS record creation, lost-found and missing-person case storage with admin verification queue. No dispatch integration, no matching. |
| Pilgrimage Planner | P1 | Not started |
| Events | P1 | **Partial** — calendar + list/detail done. Search and reminders deferred. |
| Parking | P1 | Not started |
| Transport | P1 | Not started |
| PWA / Offline | P1 | Not started |
| AI Assistant | P1 | Not started |
| Crowd Analytics | P1 | Not started |
| Command Center | P1 | Not started |
| Volunteer | P2 | Not started |
| Vendor | P2 | Not started |
| Digital Twin | P3 | Not started |

---

## Phase 2 — Pilgrim Platform

> Table 6 scope: *"Trip planner, live map, parking, transport, PWA, AI assistant"*

### 2.1 Pilgrimage Planner (P1, PRD §7)
Input: arrival/departure dates, party size, age groups, transport mode, accommodation
preference, spiritual/cultural interests, accessibility requirements. Output: a generated
itinerary of temples, events, ghats, rest periods, transport options and routes.
Depends on: Sprint 1 master data; benefits from routing (2.2) and accommodation (2.5).

### 2.2 Live map upgrade (P1, PRD §9, §11)
Route planning (walking + vehicle modes), in-map search, accessible-route option,
alternate-route suggestions, road-closure awareness. Needs a routing engine decision
(self-hosted OSRM/Valhalla vs. a licensed provider) — a procurement question, not just
an engineering one.

### 2.3 Parking (P1, PRD §12)
Parking directory, capacity/availability, entry-exit info, type (bus/two-wheeler/
accessible), shuttle connectivity. Delivers `GET /api/v1/parking/{id}/availability`.
Availability is meaningless without a real counting source — pair with 3.2 or an
operator-entered count screen.

### 2.4 Transport (P1, PRD §18)
Railway info, bus services, shuttle routes, parking-to-event shuttles, walking routes,
advisories, temporary traffic arrangements. PRD asks for dynamic integration "wherever
authoritative APIs or approved data feeds are available" — that availability needs
confirming with the departments before estimating.

### 2.5 Accommodation & essential services (PRD §17)
Hotels, dharamshalas, ashrams, tent/camp, government accommodation, food services,
bhandaras, drinking water, toilets, changing facilities. **Requirement**: listings must
visibly distinguish officially verified entries from third-party/commercial ones — extend
the `verified` flag Sprint 1 stubbed on Temple.

### 2.6 PWA / offline (P1, PRD §33)
Service worker, offline emergency contacts, offline temple info, cached maps/routes
*where licensing permits*, offline FAQs, cached events, sync queue for selected actions.
Every cached surface must display its freshness timestamp — Sprint 1's
`DataFreshnessTimestamp` component is the seed of this.

### 2.7 AI Assistant (P1, PRD §19, §27, §43)
Multilingual (Hindi/English minimum) natural-language Q&A over a RAG knowledge base plus
structured real-time APIs. Stack per Table 4: LangGraph, approved LLMs, hybrid/semantic
search (OpenSearch/Elasticsearch).
**Governance is part of the work, not a follow-up**: model registry and versioning,
evaluation datasets, security testing, bias/quality evaluation, prompt versioning, human
oversight, model monitoring, audit trails (§43). Two hard product rules from the PRD: the
assistant must display source/authority and last-updated information, and it **must not
invent real-time crowd, traffic, emergency or event information** (§19). That constraint
argues for tool-calling against the real APIs rather than free-text generation over a
crowd/traffic corpus.

### 2.8 Multilingual completion (PRD §19, §32)
Sprint 1 shipped an EN/HI i18n scaffold with `[HI-TODO]`-flagged placeholder strings and
**no fabricated Hindi**. Phase 2 needs professional Hindi translation and native-speaker
review of every string, then any additional approved languages. This is a content and
procurement task with an engineering tail, and it blocks any credible public launch.

### 2.9 Notifications (PRD §20)
Emergency, traffic, crowd, parking alerts; event reminders; temple/service updates;
itinerary notifications. User-configurable categories, with critical public-safety alerts
following authorized emergency communication policy. Requires a delivery channel decision
(web push vs. SMS vs. both) and, for emergency alerts, an authority sign-off path.

### 2.10 Family Safety (PRD §21)
Family groups, shared meeting points, emergency contacts, optional location sharing,
QR-based family identification *where approved*. Location sharing must be explicit,
purpose-specific and time-limited. Legal review required before build.

---

## Phase 3 — Operations

> Table 6 scope: *"Command center, crowd analytics, traffic, incidents, emergency"*

### 3.1 Command Center (P1, PRD §24)
Live operational dashboard: zone-wise crowd, traffic, parking, incidents, medical
incidents, missing-person cases, infrastructure issues, active alerts, GIS layers,
reports. PRD requires a clear visual distinction between observed data,
model-generated recommendations, and human decisions — design that in from the start.

### 3.2 Crowd analytics (P1, PRD §10, §26)
Aggregated crowd density from authorized sources (CCTV analytics, sensors, entry/exit
counters, traffic systems, operational reports), surfaced as the green/yellow/orange/red
bands Sprint 1 already reserved tokens for. Every reading carries a timestamp and
data-source status.
**Two PRD constraints carry forward**: individual-level tracking is not required for
basic crowd density (§10), and biometric identification / facial recognition is **not** a
default requirement — any biometric processing needs explicit legal authority, defined
purpose, governance, access controls and retention limits (§26). Sprint 1 skipped
biometrics entirely; that decision should be revisited only with counsel, not by
engineering.

### 3.3 Traffic monitoring (PRD §11, §39)
`GET /api/v1/traffic/status`, traffic-aware routing, closure management, flow analytics.

### 3.4 Incident management (PRD §25)
Full lifecycle: detection/report → classification → priority (P1–P4 per Table 3) →
department/zone assignment → response → SLA-breach escalation → resolution →
post-incident report. Sprint 1's `Incident`-shaped SOS record and AuditLog are the
foundation; the state machine, SLA timers and escalation routing are new.

### 3.5 Real emergency integration (PRD §15)
**The single biggest gap between this prototype and a production system.** Sprint 1's SOS,
missing-person and lost-found flows write to our own database and dispatch nothing.
Production requires: authorized integration with police/medical/fire dispatch, an
escalation path with named accountable operators, 24x7 staffing of the verification queue,
legally reviewed consent and retention handling, and an agreed SLA. This is an
institutional and legal programme, not a sprint of engineering.

### 3.6 Lost & found matching (PRD §16)
Controlled matching between lost and found reports, case resolution workflow, and the
audit trail extended to cover match decisions. Any automated matching needs a human
confirmation step.

### 3.7 Real-time data architecture (PRD §38)
Kafka/managed event bus, stream processing, operational stores, WebSocket push to public
clients through controlled APIs. Deferred wholesale from Sprint 1.

---

## Phase 4 — Event Operations

> Table 6 scope: *"Real-time monitoring, alerts, operational AI and analytics"*

- Live event-time monitoring and alerting at full scale
- Operational AI and predictive analytics with human oversight (§43)
- Analytics suite (§39): visitor estimates, zone crowd trends, traffic flow, parking
  utilisation, medical and emergency incidents, lost/found statistics, infrastructure
  reports, service utilisation
- Volunteer platform (P2, §22): registration, zone assignment, shifts, tasks, incident
  reporting, attendance
- Vendor management (P2, §23): registration, licence/compliance documents, location,
  hours, public listing, QR verification, complaint workflow
- Digital Twin (P3, §46): GIS + crowd + traffic + parking + infrastructure simulation.
  PRD is explicit that simulation outputs support, never replace, authorized human
  operational decisions.

---

## Cross-cutting work that has no phase and cannot be skipped

These are not features, and none of them were in Sprint 1's scope. They gate any real
public launch regardless of which phase the feature backlog has reached.

### Security (PRD §30)
OAuth2/OIDC, MFA for privileged users, secure OTP auth for public accounts, API gateway,
WAF and DDoS protection, rate limiting, secret management, encryption in transit and at
rest, session management, vulnerability and dependency scanning, and an independent
penetration test. Sprint 1 has JWT + bcrypt + input validation and nothing else.

### Privacy and legal (PRD §31)
Data minimisation, purpose limitation, explicit consent for optional location sharing,
encryption of sensitive data, retention periods, secure deletion, privacy notices,
auditability — aligned with applicable Indian data-protection, cybersecurity and
government information-security requirements. **A qualified legal review of the
missing-person and location-sharing flows is required before any public exposure.**

### Accessibility (PRD §32)
Sprint 1 built to WCAG-oriented patterns but had no audit. Needs a formal accessibility
audit with assistive-technology testing, given the PRD's explicit senior-citizen and
differently-abled user types (Table 2).

### Non-functional targets (PRD Table 5)
Availability ≥ 99.95%, critical API latency < 500 ms under designed load, page load < 3 s,
search < 1 s, emergency alert delivery < 10 s, AI response < 5 s, horizontal scaling and
traffic-spike readiness. **None of these have been measured.** Load testing against
realistic Simhastha traffic spikes is a prerequisite, not a nice-to-have.

### Infrastructure and operations (PRD §35, §41, §42)
Real cloud deployment (Docker + Kubernetes or managed containers per Table 4), CDN,
multi-zone deployment, automated backups, database replication, DR environment with
tested restores, incident-response runbooks, failover procedures, and observability
(OpenTelemetry/Prometheus/Grafana) covering API latency, error rate, resource usage,
database and Redis health, and notification delivery.

### Governance
A single authoritative Simhastha data layer consumed consistently by website, PWA, mobile
app, command center and AI assistant (§48), plus the departmental data-sharing agreements
that make the real feeds in Phases 2–3 possible.

---

## Recommended sequencing note

The PRD's phase numbering is a scope grouping, not a strict build order. Two items argue
for being pulled earlier than their phase:

1. **Hindi translation (2.8)** — the platform is unlaunchable in Ujjain without real
   Hindi. It has a long procurement/review lead time and should start immediately, in
   parallel with engineering.
2. **Security and privacy review (cross-cutting)** — the missing-person and SOS flows
   already exist in prototype form. Legal and security review of those flows should
   happen before they are extended, not after.
