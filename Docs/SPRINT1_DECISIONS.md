# Sprint 1 — Open Decision Resolutions

Decisions resolved for the five items the UX Architect flagged in
`UX_DESIGN_SYSTEM.md` and `UX_PAGE_ARCHITECTURE.md`. Backend and Frontend
should treat these as settled for Sprint 1.

---

## D-01. Lost & Found / Missing Person status lookup

**Question:** Only `POST` endpoints were in the fixed API list, so the two
`/status` pages had no data source. Add an endpoint, or cut the pages?

**Decision: add read endpoints, keyed by an opaque case reference.**

```
GET /api/v1/lost-found/{case_reference}
GET /api/v1/missing-person/{case_reference}
```

Rules:

- The `POST` response returns a `case_reference`: a random, non-sequential,
  non-guessable token. It is the only way to read a case back.
- Do **not** expose lookup by name, phone, or sequential id, and do **not**
  provide a public list endpoint for either resource.
- The missing-person read response returns only case status and timestamps.
  It must not echo back personal detail or the uploaded photo.

**Rationale:** A person who reports a lost child or a lost bag needs to check
progress, so cutting the pages would break the core flow. But PRD §31 requires
data minimisation and purpose limitation, and §16 asks for an audit trail on
sensitive cases. An enumerable endpoint over missing-person records would be a
serious privacy failure at an event of this scale. The opaque reference keeps
the flow working without creating a scraping surface.

---

## D-02. Admin CRUD and SOS endpoint paths

**Decision: follow PRD §37 conventions exactly where it names them, and use
these for the rest.**

Already fixed by the PRD:

```
POST   /api/v1/admin/events
PATCH  /api/v1/admin/events/{id}
POST   /api/v1/admin/alerts
POST   /api/v1/admin/incidents
GET    /api/v1/admin/dashboard
```

Filling the gaps, same shape:

```
GET    /api/v1/admin/events
DELETE /api/v1/admin/events/{id}
CRUD   /api/v1/admin/temples[/{id}]
CRUD   /api/v1/admin/ghats[/{id}]
CRUD   /api/v1/admin/announcements[/{id}]
GET    /api/v1/admin/lost-found          # verification queue
PATCH  /api/v1/admin/lost-found/{id}
GET    /api/v1/admin/missing-person
PATCH  /api/v1/admin/missing-person/{id}
```

Simulated SOS:

```
POST   /api/v1/emergency/sos
```

`POST /api/v1/emergency/sos` creates an incident record in our own database
and returns a reference. It dispatches nothing and notifies nobody. The
response body must carry an explicit `"simulated": true` field, and the
endpoint's OpenAPI description must state that it is a prototype.

---

## D-03. Ghat detail pages

**Decision: build them, minimally.**

The PRD already specifies `GET /api/v1/ghats/{id}/status`, which only makes
sense if there is a per-ghat view to render it. Ship
`/ghats/[slug]` with location, bathing information, facilities, accessibility,
and the status strip fed by that endpoint. Keep it lighter than the temple
detail page. No separate ghat-detail endpoint is needed: the directory payload
plus `/status` is enough.

---

## D-04. Slug format

**Decision: lowercase kebab-case, numerals preserved, transliterated Latin.**

| Name | Slug |
|---|---|
| Mahakaleshwar | `mahakaleshwar` |
| Kal Bhairav | `kal-bhairav` |
| 84 Mahadev | `84-mahadev` |
| Chintaman Ganesh | `chintaman-ganesh` |
| Sandipani Ashram | `sandipani-ashram` |
| Panchkroshi Yatra | `panchkroshi-yatra` |

Slugs stay stable and locale-independent. The Hindi route is `/hi/temples/84-mahadev`,
never a Devanagari slug, so links survive translation and copy-paste. Store the
slug as a unique indexed column, not as a value derived at render time.

---

## D-05. Dark theme

**Decision: deferred, as proposed. Not required for Sprint 1 sign-off.**

Keep the CSS custom properties structured so a Phase 2 dark theme is a token
swap rather than a refactor.

---

## Standing constraint, restated

No screen, endpoint, seed row, or document may imply a live connection to
police, medical, CCTV, or any government dispatch system. The `SafetyBanner`
is non-dismissible on every safety-critical surface, and simulated endpoints
say so in their own responses.
