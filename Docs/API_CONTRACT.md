# Simhastha 2028 — Sprint 1 API Contract (frozen)

Purpose: let Backend and Frontend build in parallel against one interface. This
contract is **binding for Sprint 1**. Backend implements exactly these paths and
response shapes; Frontend codes against them. If Backend must deviate, it must say
so explicitly in its final report so Frontend can be corrected — do not silently
change a field name.

Base URL: `NEXT_PUBLIC_API_URL` (local dev: `http://localhost:8000`).
All paths are prefixed `/api/v1`. All responses are JSON. All timestamps are ISO-8601
UTC strings (e.g. `2028-04-09T04:30:00Z`).

Derived from: PRD §37 (named endpoints), `Docs/SPRINT1_DECISIONS.md` D-01/D-02/D-03,
`Docs/UX_PAGE_ARCHITECTURE.md` §2 (page data needs).

---

## 0. Conventions

**List envelope.** All list endpoints return:
```json
{ "items": [ ... ], "total": 9, "last_updated": "2026-09-20T10:00:00Z" }
```
`last_updated` = max `updated_at` across returned rows (null if empty). It backs the
`DataFreshnessTimestamp` component (PRD §8 "last-updated timestamp", §33 freshness).

**Errors.** FastAPI default shape, HTTP status carries meaning:
```json
{ "detail": "Temple not found" }
```
422 for validation errors (FastAPI default body). 404 not found. 401 unauthenticated.
403 wrong role.

**Publication.** Public endpoints return **only** `status = "published"` rows. Draft
rows are visible solely through `/api/v1/admin/*` with a valid admin token.

**Prototype flag.** Every safety-critical response object (emergency services, SOS,
lost-found, missing-person) carries:
```json
"prototype_notice": "Demo prototype — not connected to live emergency dispatch."
```
SOS additionally carries `"simulated": true` (decision D-02).

**Geo.** Coordinates are returned as plain floats, never GeoJSON blobs:
`"latitude": 23.1828, "longitude": 75.7682`. Nullable if unknown.

**Seed-data honesty.** Any field whose value is invented for the prototype rather than
sourced from an authority must be marked. Objects carrying such data include
`"data_source": "placeholder"` (vs `"cms"` for admin-authored content). Phone numbers
in seeded emergency entries must be obviously non-real placeholders (see §5).

---

## 1. Events — PRD §8

### `GET /api/v1/events`
Query params (all optional): `category` (string), `from_date` (ISO date),
`to_date` (ISO date), `limit` (int, default 50), `offset` (int, default 0).

Item shape:
```json
{
  "id": 1,
  "slug": "first-shahi-snan",
  "title": "First Shahi Snan",
  "summary": "Principal bathing day at Ram Ghat.",
  "description": "Full CMS-authored body text.",
  "category": "snan_parva",
  "starts_at": "2028-04-09T04:30:00Z",
  "ends_at": "2028-04-09T12:00:00Z",
  "venue_name": "Ram Ghat",
  "latitude": 23.1828,
  "longitude": 75.7682,
  "image_url": null,
  "status": "published",
  "data_source": "placeholder",
  "updated_at": "2026-09-20T10:00:00Z"
}
```
`category` enum: `snan_parva | religious | aarti | akhada | cultural | government`.

### `GET /api/v1/events/{slug}`
Single event, same shape. 404 if not found or not published.

---

## 2. Temples — PRD §13

### `GET /api/v1/temples`
Query params: `limit`, `offset`. Returns exactly the 9 seeded temples.

Item shape:
```json
{
  "id": 1,
  "slug": "mahakaleshwar",
  "name": "Mahakaleshwar Jyotirlinga",
  "short_description": "One of the twelve Jyotirlingas.",
  "significance": "Full CMS-authored significance text.",
  "timings": "Placeholder — darshan timings to be confirmed by temple authority.",
  "aarti_schedule": null,
  "address": "Jaisinghpura, Ujjain, Madhya Pradesh",
  "latitude": 23.1828,
  "longitude": 75.7682,
  "transport_info": "Placeholder transport guidance.",
  "accessibility_info": "Placeholder — accessibility details not yet verified.",
  "image_url": null,
  "status": "published",
  "verified": false,
  "data_source": "placeholder",
  "updated_at": "2026-09-20T10:00:00Z"
}
```
Required slugs (decision D-04): `mahakaleshwar`, `kal-bhairav`, `harsiddhi`,
`mangalnath`, `gadkalika`, `chintaman-ganesh`, `sandipani-ashram`, `84-mahadev`,
`panchkroshi-yatra`.

`verified` is false for all seeded rows — nothing in this prototype is authority-verified.
Frontend renders the verified badge only when `verified === true`.

### `GET /api/v1/temples/{slug}`
Single temple, same shape. 404 if not found.

---

## 3. Ghats — PRD §9/§13, decision D-03

### `GET /api/v1/ghats`
**Added to the PRD's named list** because the directory page cannot enumerate ghats
otherwise (UX flagged this; confirmed here). Item shape:
```json
{
  "id": 1,
  "slug": "ram-ghat",
  "name": "Ram Ghat",
  "description": "Principal bathing ghat on the Shipra.",
  "bathing_info": "Placeholder bathing guidance.",
  "facilities": ["changing_rooms", "drinking_water", "toilets"],
  "accessibility_info": "Placeholder — accessibility details not yet verified.",
  "latitude": 23.1852,
  "longitude": 75.7684,
  "image_url": null,
  "status": "published",
  "data_source": "placeholder",
  "updated_at": "2026-09-20T10:00:00Z"
}
```

### `GET /api/v1/ghats/{id}/status` — PRD §37 (named endpoint, keep this exact path)
`{id}` accepts **either** the numeric id or the slug (implement slug-or-id resolution).
```json
{
  "ghat_id": 1,
  "slug": "ram-ghat",
  "name": "Ram Ghat",
  "status": "open",
  "crowd_level": null,
  "advisory": null,
  "data_source": "placeholder",
  "prototype_notice": "Status is seeded placeholder data — no live sensor or CCTV feed is connected.",
  "updated_at": "2026-09-20T10:00:00Z"
}
```
`status` enum: `open | restricted | closed`. `crowd_level` is **always null** this
sprint (no crowd data source exists — do not fabricate green/yellow/orange/red values).
Frontend must render "Crowd level: not available" rather than a fake badge.

---

## 4. Emergency — PRD §15, decision D-02

### `GET /api/v1/emergency/services`
Query param: `category` (optional). Item shape:
```json
{
  "id": 1,
  "name": "Ujjain Central Police Help Point (demo)",
  "category": "police",
  "phone": "+91-00000-00001",
  "address": "Near Ram Ghat, Ujjain",
  "latitude": 23.1830,
  "longitude": 75.7690,
  "hours": "24x7",
  "notes": "Seeded demo entry — not a real police contact.",
  "data_source": "placeholder",
  "prototype_notice": "Demo prototype — not connected to live emergency dispatch.",
  "updated_at": "2026-09-20T10:00:00Z"
}
```
`category` enum: `police | ambulance | fire | medical | women_child | disaster_mgmt |
help_center`.

**Seeded phone numbers must be obviously fake placeholders** in the `+91-00000-000NN`
pattern. Do NOT seed real Indian emergency numbers (100/102/108/112) or real station
numbers — a user must never tap-to-call a number this prototype implies is live. The
frontend `/emergency` page separately shows static real-world guidance text ("In a real
emergency, dial your local emergency number directly") authored in the UI, not seeded
as a callable directory row.

### `POST /api/v1/emergency/sos` — simulated, decision D-02
Request:
```json
{
  "reporter_name": "optional string",
  "reporter_phone": "optional string",
  "situation_category": "medical",
  "note": "optional free text",
  "latitude": 23.1828,
  "longitude": 75.7682,
  "consent_given": true
}
```
`situation_category` enum: `medical | security | fire | lost_person | other`.
`consent_given` must be `true` — reject with 422 if false/absent (PRD §15 explicit
consent). Location is optional but only stored if `consent_given` is true.

Response `201`:
```json
{
  "case_reference": "SOS-7K2M9QX4",
  "status": "recorded",
  "simulated": true,
  "created_at": "2026-09-20T10:00:00Z",
  "prototype_notice": "Demo prototype — this SOS was recorded in a test database only. Nothing was dispatched and no responder was notified. In a real emergency contact local emergency services directly."
}
```
The OpenAPI `description=` for this route must state it is a prototype that dispatches
nothing.

---

## 5. Lost & Found — PRD §16, decision D-01

### `POST /api/v1/lost-found`
Request:
```json
{
  "report_type": "lost",
  "category": "bag",
  "description": "Brown backpack with blue zip.",
  "location_text": "Near Ram Ghat gate 3",
  "latitude": null,
  "longitude": null,
  "occurred_at": "2026-09-20T09:00:00Z",
  "reporter_name": "string",
  "reporter_phone": "string",
  "image_url": null
}
```
`report_type` enum: `lost | found`. `category` enum: `bag | documents | phone |
jewellery | child_item | other`. Validation: `description` 10–2000 chars,
`reporter_phone` required and non-empty, `occurred_at` must not be in the future.

Response `201`:
```json
{
  "case_reference": "LF-3N8P2VQ7",
  "status": "submitted",
  "created_at": "2026-09-20T10:00:00Z",
  "prototype_notice": "Demo prototype — this report is stored in a test database and is not shared with police or any lost-property authority."
}
```

### `GET /api/v1/lost-found/{case_reference}`
The **only** public read path. Returns:
```json
{
  "case_reference": "LF-3N8P2VQ7",
  "report_type": "lost",
  "category": "bag",
  "status": "submitted",
  "created_at": "2026-09-20T10:00:00Z",
  "updated_at": "2026-09-20T10:00:00Z",
  "prototype_notice": "Demo prototype — ..."
}
```
`status` enum: `submitted | under_review | verified | matched | closed | rejected`.
404 on unknown reference. **No list endpoint, no lookup by name or phone.**

---

## 6. Missing Person — PRD §16, decision D-01 (strictest privacy rules)

### `POST /api/v1/missing-person`
Request:
```json
{
  "person_name": "string",
  "person_age": 8,
  "person_gender": "male",
  "physical_description": "string",
  "last_seen_location_text": "Near Mahakaleshwar gate 2",
  "latitude": null,
  "longitude": null,
  "last_seen_at": "2026-09-20T08:30:00Z",
  "photo_url": null,
  "reporter_name": "string",
  "reporter_phone": "string",
  "reporter_relationship": "parent",
  "consent_given": true
}
```
Validation: `person_name` required, `person_age` 0–120 if given, `reporter_phone`
required, `last_seen_at` not in the future, `consent_given` must be true (422 otherwise).

Response `201`:
```json
{
  "case_reference": "MP-9Q4X7KT2",
  "status": "submitted",
  "created_at": "2026-09-20T10:00:00Z",
  "prototype_notice": "Demo prototype — this report is stored in a test database for this pilot and is NOT automatically sent to police. If a person is genuinely missing, contact local police directly."
}
```

### `GET /api/v1/missing-person/{case_reference}`
**Status and timestamps only.** Must NOT echo `person_name`, age, description, photo,
reporter details, or location.
```json
{
  "case_reference": "MP-9Q4X7KT2",
  "status": "submitted",
  "created_at": "2026-09-20T10:00:00Z",
  "updated_at": "2026-09-20T10:00:00Z",
  "prototype_notice": "Demo prototype — ..."
}
```
`status` enum: `submitted | under_review | verified | resolved | closed`.
404 on unknown reference. **No list endpoint. No search by name or phone. Ever.**

### Case reference format (both resources + SOS)
`{PREFIX}-{8 chars}` where the 8 chars come from a cryptographically secure random
source (`secrets.choice`) over an unambiguous alphabet (no `0/O`, `1/I/L`). Prefixes:
`LF`, `MP`, `SOS`. Stored unique-indexed. Never sequential, never derived from the row id.

---

## 7. Announcements — PRD §28 (CMS-managed)

### `GET /api/v1/announcements`
Query param: `limit`. Returns published, non-expired announcements, newest first.
```json
{
  "id": 1,
  "slug": "shuttle-route-change",
  "title": "Shuttle route change for Ram Ghat",
  "body": "CMS-authored body text.",
  "priority": "normal",
  "published_at": "2026-09-20T09:00:00Z",
  "expires_at": null,
  "status": "published",
  "data_source": "cms",
  "updated_at": "2026-09-20T10:00:00Z"
}
```
`priority` enum: `normal | important | critical`.

---

## 8. Auth & Admin — PRD §29, §37, decision D-02

### `POST /api/v1/auth/login`
Request `{ "username": "admin", "password": "..." }` (JSON body, not form-encoded).
Response `200`:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": { "id": 1, "username": "admin", "full_name": "Sprint 1 Admin", "role": "super_admin" }
}
```
401 on bad credentials. JWT (HS256, `SECRET_KEY` from settings), claims include `sub`
(user id), `role`, `exp`. Passwords hashed with bcrypt/passlib — never stored plaintext,
never returned.

### `GET /api/v1/auth/me`
Bearer-token protected. Returns the `user` object above. 401 if missing/invalid token.

### Roles
Seed the role table with at least `super_admin`, `content_manager`, `public_user`, and
structure it (a `roles` table + FK, not a hardcoded enum column) so the full PRD §29 list
(department_admin, zone_admin, police_admin, medical_admin, volunteer, vendor) can be
added later without a schema change. `public_user` has **no** admin access.

### Admin endpoints (all Bearer-protected, `super_admin` or `content_manager`)
```
GET    /api/v1/admin/events            list incl. drafts
POST   /api/v1/admin/events            create (defaults status=draft)
PATCH  /api/v1/admin/events/{id}       partial update incl. status transition
DELETE /api/v1/admin/events/{id}
GET|POST|PATCH|DELETE  /api/v1/admin/announcements[/{id}]
GET|POST|PATCH|DELETE  /api/v1/admin/temples[/{id}]
GET|POST|PATCH|DELETE  /api/v1/admin/ghats[/{id}]
GET    /api/v1/admin/lost-found                 verification queue
PATCH  /api/v1/admin/lost-found/{id}            status transition only
GET    /api/v1/admin/missing-person             verification queue
PATCH  /api/v1/admin/missing-person/{id}        status transition only
GET    /api/v1/admin/dashboard                  counts by entity + status
```
Admin list endpoints return the same item shapes as public ones plus drafts.

### Draft → Published workflow (stub state machine, per spec)
`status` on Event/Announcement/Temple/Ghat is `draft | published | archived`.
Transitions allowed: `draft → published`, `published → draft`, `published → archived`,
`draft → archived`. Implement as an explicit guarded transition function, not a free-form
column write, so the full PRD §28 five-stage workflow can replace it later. Reject invalid
transitions with 409.

### Audit log — PRD §16 ("audit trail for sensitive cases"), §30
Every admin write (create/update/delete/status transition) and every
lost-found / missing-person / SOS submission writes an `AuditLog` row:
`actor_user_id` (nullable for public submissions), `action`, `entity_type`, `entity_id`,
`timestamp`, `detail` (JSON). No public endpoint exposes audit rows this sprint.

---

## 9. Explicitly NOT in this sprint
`/api/v1/parking/*`, `/api/v1/crowd/zones`, `/api/v1/traffic/status`, `/api/v1/ai/chat`,
`/api/v1/admin/analytics`, WebSockets. Do not stub them as fake-data endpoints — omit
them entirely so nothing downstream mistakes a placeholder for a feed. They are recorded
in `docs/ROADMAP.md` instead.
