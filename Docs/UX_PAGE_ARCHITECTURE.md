# Simhastha 2028 — Page & Component Architecture (Sprint 1)

Owner: UX Architect. Consumers: Frontend Developer. Stack: Next.js App Router + React +
TypeScript + Tailwind. Pairs with `UX_DESIGN_SYSTEM.md` (tokens, safety banner spec,
accessibility notes). Every route below is scoped to Sprint 1 (PRD Phase 1) only — no
planner, parking, transport, crowd/traffic APIs, or AI assistant (see spec's out-of-scope
list).

Route paths shown are **default-locale (English) paths**. See §5 for how the Hindi locale
maps onto the same paths (`/hi/...`).

---

## 1. Route Map (App Router)

```
app/
├── (public)/
│   ├── page.tsx                          # /  — Homepage
│   ├── events/
│   │   ├── page.tsx                      # /events — list
│   │   └── [slug]/page.tsx               # /events/[slug] — detail
│   ├── temples/
│   │   ├── page.tsx                      # /temples — directory
│   │   └── [slug]/page.tsx               # /temples/[slug] — detail (9 temples)
│   ├── ghats/
│   │   ├── page.tsx                      # /ghats — directory (basic)
│   │   └── [slug]/page.tsx               # /ghats/[slug] — detail (optional, see note)
│   ├── map/
│   │   └── page.tsx                      # /map — Live GIS Map
│   ├── emergency/
│   │   ├── page.tsx                      # /emergency — directory
│   │   └── sos/page.tsx                  # /emergency/sos — SOS trigger flow
│   ├── lost-found/
│   │   ├── report/page.tsx               # /lost-found/report
│   │   └── status/page.tsx               # /lost-found/status — lookup (see §1 note)
│   └── missing-person/
│       ├── report/page.tsx               # /missing-person/report
│       └── status/page.tsx               # /missing-person/status — lookup (see §1 note)
├── admin/
│   ├── login/page.tsx                    # /admin/login
│   ├── page.tsx                          # /admin — dashboard
│   ├── events/
│   │   ├── page.tsx                      # /admin/events — list
│   │   ├── new/page.tsx                  # /admin/events/new
│   │   └── [id]/edit/page.tsx            # /admin/events/[id]/edit
│   ├── announcements/  (same list/new/[id]/edit pattern)
│   ├── temples/        (same pattern)
│   └── ghats/          (same pattern)
└── layout.tsx                            # root layout: SiteHeader + SiteFooter + providers
```

**Note on slugs**: temple/event/ghat slugs are lowercase-kebab of the entity name (e.g.
`mahakaleshwar`, `kal-bhairav`, `84-mahadev` → `84-mahadev` or `chaurasi-mahadev`, Backend's
call on the exact slug for numeric-leading names — flag for Backend Architect).

**Note on `/ghats/[slug]` detail**: spec scope says "Ghats directory (basic)" and only
defines `GET /api/v1/ghats/{id}/status`, not a full ghat-detail API. Recommend the directory
page (`/ghats`) show each ghat as a card with name, status badge, and key facts inline —
**no separate detail page required this sprint**. Keep `/ghats/[slug]` as a stub route only
if Backend already returns enough fields to justify one; otherwise cut it. Flagged as a call
for Frontend/Backend, not a hard requirement.

**Note on `/lost-found/status` and `/missing-person/status`**: the spec's fixed public API
list (`project-specs` §"Core public read/write APIs") only names `POST /api/v1/lost-found`
and `POST /api/v1/missing-person` — **no GET-by-reference-number endpoint exists in Sprint 1
backend scope**. These two status-lookup pages are included here because they were named in
this task's deliverable list, but they currently have no API to call. Recommend one of:
(a) cut both pages from Sprint 1 and show "reference number saved, check back in a future
version" on the report confirmation screen instead, or (b) Backend adds a minimal
`GET /api/v1/lost-found/{reference}` / `GET /api/v1/missing-person/{reference}` lookup.
**Flagged for PM/Backend Architect decision** — UI is specified below either way (§3) so
Frontend isn't blocked, but do not build a page that silently fails against a non-existent
endpoint.

**Note on admin CRUD API paths**: BE-10 covers "Admin CRUD + draft/publish" but the spec's
fixed API list doesn't name exact admin endpoint paths. This doc assumes a convention of
`GET/POST/PUT /api/v1/admin/{entity}` and `PATCH /api/v1/admin/{entity}/{id}/publish` for the
draft→published toggle. **Confirm exact paths with Backend Architect** before Frontend wires
FE-10 — placeholder convention only.

---

## 2. Page Inventory

### 2.1 Homepage — `/`
PRD §6. Consumes: `GET /api/v1/events` (today's events subset), `GET
/api/v1/emergency/services` (for the persistent emergency CTA/count, not full listing).
No crowd/traffic/parking data this sprint — PRD's "live status indicators" bullet is
**out of scope**; if a placeholder tile is added anyway it must carry `SafetyBanner
variant="crowd-placeholder"` per the design system.

Sections top to bottom:
1. `SiteHeader` (persistent, includes emergency CTA + language selector)
2. Hero — Simhastha 2028 identity, short tagline, primary CTA row: **Explore Map / Events /
   Temples / Emergency** (4 CTAs, "Plan Your Journey" CTA omitted — planner is out of scope
   this sprint; replace with "Temples" or "Emergency" per PM call)
3. `AnnouncementStrip` — today's announcements/events, horizontally scrollable on mobile,
   pulls top N by date from `/api/v1/events`
4. `QuickAccessGrid` — icon tiles: Temples, Ghats, Emergency, Lost & Found (2×4 grid, see
   design system §2)
5. `SiteFooter`

Mobile requirement: emergency CTA in `SiteHeader` must remain visible/reachable without
scrolling (persistent emergency access, PRD §6) — implement as a sticky icon button in the
header bar, not buried in a hamburger menu.

### 2.2 Calendar & Events — `/events` (list), `/events/[slug]` (detail)
PRD §8. Consumes `GET /api/v1/events`.

List page: filter/tab by category (Snan/Parva, Religious, Cultural, Government — per PRD §8
categories) if the API returns a `category` field; otherwise flat chronological list.
`DataFreshnessTimestamp` shown at top ("Last updated: ..."). Each item: `EventCard` (title,
date/time, venue, category badge) linking to detail.

Detail page: full description, date/time, venue name + link to map location (if the event
has geo coords, deep-link into `/map`), `DataFreshnessTimestamp`. No hardcoded content — 404
gracefully (`ErrorState`) if slug not found.

### 2.3 Temple Directory + Detail — `/temples`, `/temples/[slug]`
PRD §13. Consumes `GET /api/v1/temples`. Exactly 9 temples: Mahakaleshwar, Kal Bhairav,
Harsiddhi, Mangalnath, Gadkalika, Chintaman Ganesh, Sandipani Ashram, 84 Mahadev,
Panchkroshi Yatra.

Directory: grid of `TempleCard` (name, thumbnail, one-line significance, link).

Detail page sections (per PRD §13 field list, scoped per tasklist FE-04 — crowd status
static/omitted):
1. Header — name, hero image, breadcrumb
2. Significance — descriptive text (CMS-authored)
3. Timings — darshan hours, aarti schedule if available
4. Location & Transport — address, nearest access points, link to `/map` centered on this
   temple (deep-link via query param, e.g. `/map?focus=temple:mahakaleshwar`)
5. Accessibility — wheelchair access, ramp/step info, accessible route note (PRD §32) — even
   if data is sparse this sprint, render the section with "Accessibility information: [text
   or 'Not yet available']" rather than omitting it silently
6. Crowd status — **omit entirely this sprint** (no crowd API); do not show a fake number
7. Verified-info note — small badge/text: "Information verified by [Content Manager /
   Admin]" sourced from CMS `verified` flag if the schema has one; otherwise omit, do not
   fabricate

### 2.4 Ghats Directory — `/ghats`
Spec: "Ghats directory (basic)". Consumes `GET /api/v1/ghats/{id}/status` (per-ghat) — list
page likely needs a ghat list first; if no `GET /api/v1/ghats` list endpoint exists,
**flag for Backend**: directory needs a way to enumerate ghats before it can call the
per-id status endpoint. Render as `GhatCard` grid: name, `StatusBadge` (open/closed/status
text — whatever `{id}/status` returns), basic facts.

### 2.5 Live GIS Map — `/map`
PRD §9, scoped per tasklist FE-06: MapLibre + free OSM tiles, layer toggles for
temples/ghats/emergency minimum, static placeholder crowd/traffic layer. No search, no route
planning this sprint (explicitly descoped). Consumes `GET /api/v1/temples`, `GET
/api/v1/ghats/{id}/status` (or list equivalent), `GET /api/v1/emergency/services` — each as
a toggleable marker layer.

Structure:
1. `SiteHeader`
2. `MapCanvas` (full-bleed below header, MapLibre instance, OSM raster/vector free tiles)
3. `LayerTogglePanel` — floating panel, top-left or bottom-sheet on mobile (see UX-05 spec
   in §4 below)
4. `SafetyBanner variant="crowd-placeholder"` — appears above/over the map only when the
   crowd/traffic placeholder layer toggle is ON
5. Marker click → `MapInfoCard` popover (name, category, link to detail page)

Query param `?focus=temple:{slug}` (or `ghat:{slug}`, `emergency:{id}`) centers/zooms the
map and opens that marker's popover on load — used by deep-links from detail pages.

### 2.6 Emergency Services Directory + SOS — `/emergency`, `/emergency/sos`
PRD §15. Consumes `GET /api/v1/emergency/services`; SOS posts to an incident-creation
endpoint (BE-11 — exact path e.g. `POST /api/v1/emergency/sos`, **confirm with Backend**).

`/emergency`: `SafetyBanner variant="emergency"` inline at top. Directory grouped by category
(Police, Ambulance, Fire, Medical, Women & Child, Disaster Mgmt, Help Centers per PRD §15),
each entry: name, phone (tap-to-call `tel:` link), location, distance if geo available. Large
"SOS" CTA button (prominent, `secondary` accent color, min 56px tall) linking to
`/emergency/sos`.

`/emergency/sos`: `SafetyBanner variant="emergency" placement="sticky" showFormNote`.
Flow: (1) consent step — explicit checkbox "I consent to sharing my location for this test
SOS record" per PRD §15 "clear user consent"; (2) minimal form — name/phone (optional if
anonymous allowed, Backend's call), situation category, free-text note; (3) submit → creates
simulated incident record; (4) confirmation screen showing a reference number and repeating
the demo-prototype notice plus real-world guidance ("If this is a real emergency, call
[local emergency number] directly").

### 2.7 Lost & Found — `/lost-found/report`, `/lost-found/status`
PRD §16 fields: category, description, image, location, time. Posts to `POST
/api/v1/lost-found`. `SafetyBanner variant="lost-found" showFormNote` at top of report form.

Report form fields: report type (Lost item / Found item — radio), category (dropdown, seed
options e.g. Bag, Documents, Phone, Jewelry, Child's item, Other), description (textarea),
image upload (optional, single image), location (text field + optional "pick on map" linking
to `/map` in picker mode), date/time (defaults to now, editable), reporter contact (phone,
required for follow-up). On submit: confirmation screen with reference number.

Status page: reference-number lookup form + result panel. **Backed by no API this sprint**
(see §1 note) — build the UI, but gate the actual fetch behind a clearly-commented TODO / or
per PM decision, cut the page.

### 2.8 Missing Person — `/missing-person/report`, `/missing-person/status`
PRD §16. Posts to `POST /api/v1/missing-person`. `SafetyBanner variant="missing-person"
showFormNote` at top — this is the most sensitive form on the site; consent language must be
explicit ("This report will be visible to platform administrators for this pilot. It is not
automatically sent to police.").

Report form fields: missing person's name, age, gender, physical description, last-seen
location (text + map picker), last-seen date/time, photo upload (optional), reporter name +
contact (required), relationship to missing person. Submit → confirmation + reference number
+ repeat guidance to also contact police directly for real emergencies.

Status page: same caveat as §2.7 — reference-lookup UI spec provided, backing API to be
confirmed.

### 2.9 Admin CMS — `/admin/login`, `/admin`, entity CRUD
PRD §28. Consumes admin auth (BE-09) + CRUD (BE-10).

`/admin/login`: centered card, email/username + password, error state on failure. No public
self-registration (admin accounts are seeded, per spec deliverable #3).

`/admin` (dashboard): post-login landing. Summary tiles (counts: draft events, published
events, pending announcements, etc. — nice-to-have, not blocking) + nav to the four entity
sections (Events, Announcements, Temples, Ghats).

Per-entity screens (`/admin/{entity}`, `/admin/{entity}/new`, `/admin/{entity}/[id]/edit`):
- List view: table (desktop) / stacked cards (mobile) with columns Name/Title, Status
  (`StatusBadge`: Draft / Published), Last Updated, Actions (Edit, Publish/Unpublish toggle).
- Create/Edit form: fields per entity (Event: title, description, date/time, venue,
  category, image; Announcement: title, body, priority, expiry; Temple/Ghat: name,
  description, timings, location fields, image, accessibility notes).
- `PublishToggle` component: explicit two-state control (Draft ⇄ Published), not a silent
  auto-publish-on-save — matches spec's "draft → published stub workflow." Full PRD §28
  multi-stage workflow (Draft → Department review → Verification → Approval → Publication)
  is **descoped to a single Draft/Published toggle** this sprint per tasklist BE-10 wording
  ("draft → published stub workflow") — do not build the 5-stage workflow.
- RBAC: Super Admin and Content Manager can both reach these screens this sprint (minimum 3
  roles: Super Admin, Content Manager, Public User — Public User has no admin access at all).
  Role-gating enforced by backend; frontend hides admin nav entirely for non-admin sessions
  and redirects `/admin/*` to `/admin/login` if unauthenticated.

---

## 3. Shared Component List

| Component | Purpose | Notes |
|---|---|---|
| `SiteHeader` | Global nav, logo/identity, language selector (EN/HI), persistent emergency icon-button | Sticky on mobile; skip-link target; see §4/§5 |
| `SiteFooter` | Secondary nav, credits, prototype disclaimer link | Include a permanent small-print line: "Simhastha 2028 prototype — Sprint 1" |
| `SafetyBanner` | Demo-prototype safety notice | Full spec in `UX_DESIGN_SYSTEM.md` §3 |
| `Card` (variants: `TempleCard`, `GhatCard`, `EventCard`, `EmergencyServiceCard`) | List-item summary tile | Shared base: image/icon, title, 1-2 line meta, link wrapper; variant-specific meta row |
| `StatusBadge` | Small colored+labeled pill: ghat status, event category, admin Draft/Published, density level | Always pairs color with a text label — never color-only (accessibility) |
| `DataFreshnessTimestamp` | "Last updated: {date}" / "Showing cached data from {date}" | Per PRD §33 offline-freshness pattern; reusable on Events, Announcements, Temple/Ghat detail, and any offline-cached view; props: `{ updatedAt: string; isCached?: boolean }` |
| `LayerToggle` / `LayerTogglePanel` | GIS map layer show/hide controls | Full spec §4 below |
| `LoadingState` | Skeleton or spinner for async data | Use skeleton cards matching the target layout, not a generic spinner, for list pages |
| `EmptyState` | "No events scheduled" / "No results" | Icon + short message + optional CTA (e.g. "Back to Temples") |
| `ErrorState` | API failure / 404 | Message + retry button where retry is meaningful (GET failures), not on POST confirmation pages |
| `ConsentCheckbox` | Explicit consent control for SOS/location sharing | Required-checked state before submit enabled, per PRD §15/§31 |
| `FormField` (text/textarea/select/date/file/phone) | Shared form input wrapper | Label + input + error message, `aria-describedby` wired per accessibility notes |
| `ImageUpload` | Single-image picker with preview | Used by Lost & Found, Missing Person, Admin entity forms |
| `MapLocationPicker` | Modal/inline mini-map to pick a lat/lng, backed by `/map`'s MapLibre instance | Used by Lost & Found / Missing Person forms |
| `PublishToggle` | Draft ⇄ Published control | Admin CMS only |
| `LanguageSelector` | EN/HI switch | Part of `SiteHeader`; see §5 |
| `Breadcrumb` | Directory > Detail trail | Temple/Ghat/Event detail pages |
| `ReferenceNumberDisplay` | Post-submit confirmation code block, copyable | Lost & Found / Missing Person / SOS confirmation screens |

---

## 4. GIS Map Layer-Toggle Pattern (UX-05)

Scope: temples, ghats, emergency layers minimum (per spec), plus a static placeholder
crowd/traffic layer. No search, no routing this sprint.

**Component**: `LayerTogglePanel`
- Desktop: floating card, top-left corner of the map, `shadow-raised`, `rounded-lg`,
  `bg-surface-bg`, max-width ~220px, always visible (not collapsed behind a button) since
  there are only 4 layers.
- Mobile: collapses into a bottom-sheet triggered by a floating "Layers" pill button
  (bottom-right, above safe-area), min 44px touch target, expands upward.
- Each row: `LayerToggle` = icon + label + switch control (not a checkbox — use a toggle
  switch visually, `role="switch" aria-checked`), min 44px row height.

**Layers (fixed order, Sprint 1)**:
1. Temples (icon: temple/dome silhouette, color: `primary.500`) — default ON
2. Ghats (icon: water/steps, color: `primary.400`) — default ON
3. Emergency Services (icon: cross/shield, color: `status.danger`) — default ON
4. Crowd & Traffic (placeholder) (icon: people/warning, color: `density.moderate`) —
   **default OFF**. Turning it on reveals static sample markers/zones using the `density.*`
   color tokens AND triggers the `SafetyBanner variant="crowd-placeholder"` above the map
   (see §2.5). Turning it off removes both the layer and the banner.

**Behavior**:
- Toggles are independent (any combination on/off), state persists only for the session
  (component state, not localStorage — avoid confusing users on return visits with a
  different-than-default map).
- Marker clustering: not required this sprint given small seeded dataset (9 temples + a
  handful of ghats/emergency entries) — skip clustering complexity.
- Each layer's markers use visually distinct shapes AND colors (not color alone) so the map
  remains legible for color-vision-deficient users.

---

## 5. i18n Structure (EN + HI)

**Library choice: `next-intl`.** Rationale: first-class Next.js App Router support (server
components, `generateStaticParams` for locale segments, typed message catalogs), active
maintenance, and simpler middleware than rolling a custom solution — appropriate for a
2-locale Sprint 1 scaffold that Phase 2 will extend. (Alternative `react-i18next` was
considered but has weaker App Router/server-component ergonomics.)

### Folder structure
```
apps/web/
├── messages/
│   ├── en.json
│   └── hi.json
├── i18n/
│   ├── request.ts        # next-intl server config (locale detection, message loading)
│   └── routing.ts        # locale list, default locale, localePrefix: 'as-needed'
├── middleware.ts          # next-intl middleware for locale routing
└── app/
    └── [locale]/
        ├── layout.tsx
        ├── page.tsx        # homepage
        └── ...             # all routes from §1 nest under [locale]
```

`localePrefix: 'as-needed'` — English (default) serves at un-prefixed paths (`/temples`),
Hindi serves at `/hi/temples`. This keeps the route table in §1 accurate for the default
locale while giving Hindi a clean, shareable prefix. `defaultLocale: 'en'`, `locales: ['en',
'hi']`.

### `LanguageSelector` placement (UX-04)
Lives in `SiteHeader`, top-right on desktop, inside the mobile menu header row on small
screens — always visible without opening a nested menu (PRD §6 "Multilingual interface
selector" is a top-level requirement, not buried). Two-option toggle: **EN | हिं** (short
labels, not full "English"/"हिन्दी" spelled out, to save header space — full names in
`aria-label`). Switching locale preserves the current route (`/temples/mahakaleshwar` ↔
`/hi/temples/mahakaleshwar`), not a redirect to homepage.

### Message key structure
Namespaced by feature area, flat within each namespace (2 levels max — avoid deep nesting
that's painful to maintain by hand):

```json
{
  "common": {
    "appName": "Simhastha 2028",
    "skipToContent": "Skip to main content",
    "loading": "Loading...",
    "retry": "Try again",
    "lastUpdated": "Last updated: {date}",
    "submit": "Submit",
    "cancel": "Cancel"
  },
  "nav": {
    "home": "Home",
    "events": "Events",
    "temples": "Temples",
    "ghats": "Ghats",
    "map": "Map",
    "emergency": "Emergency",
    "lostFound": "Lost & Found",
    "missingPerson": "Missing Person"
  },
  "safetyBanner": {
    "emergency": "Demo prototype — not connected to live emergency dispatch.",
    "missingPerson": "Demo prototype — not connected to live police or government missing-person systems.",
    "lostFound": "Demo prototype — reports are stored for this pilot only and are not monitored 24/7.",
    "crowdPlaceholder": "Demo prototype — crowd and traffic levels shown are sample data, not live sensor feeds.",
    "formNote": "Submitting this form creates a real record in our test database but does not alert any emergency service, police, or hospital. In a real emergency, contact local authorities directly."
  },
  "homepage": {
    "heroTitle": "Simhastha 2028 — Ujjain",
    "heroSubtitle": "[HI-TODO] Your guide to temples, events, and essential services",
    "ctaMap": "Explore Map",
    "ctaEvents": "Events",
    "ctaTemples": "Temples",
    "ctaEmergency": "Emergency"
  },
  "events": {
    "pageTitle": "Calendar & Events",
    "emptyState": "No events scheduled right now.",
    "category": {
      "snanParva": "Snan / Parva",
      "religious": "Religious Programs",
      "cultural": "Cultural Programs",
      "government": "Government Programs"
    }
  },
  "temples": {
    "pageTitle": "Temples",
    "significance": "Significance",
    "timings": "Timings",
    "accessibility": "Accessibility",
    "accessibilityUnavailable": "Accessibility information not yet available.",
    "viewOnMap": "View on map"
  },
  "ghats": {
    "pageTitle": "Ghats",
    "statusLabel": "Status"
  },
  "map": {
    "pageTitle": "Live Map",
    "layers": "Layers",
    "layerTemples": "Temples",
    "layerGhats": "Ghats",
    "layerEmergency": "Emergency Services",
    "layerCrowd": "Crowd & Traffic (sample)"
  },
  "emergency": {
    "pageTitle": "Emergency Services",
    "sosButton": "SOS",
    "sosConsent": "I consent to sharing my location for this test SOS record.",
    "sosConfirmTitle": "Your test SOS report was recorded",
    "callDirect": "If this is a real emergency, call your local emergency number directly."
  },
  "lostFound": {
    "pageTitle": "Lost & Found",
    "reportTypeLost": "Lost item",
    "reportTypeFound": "Found item",
    "category": "Category",
    "description": "Description",
    "location": "Location",
    "dateTime": "Date & time",
    "confirmTitle": "Report submitted",
    "referenceNumber": "Reference number"
  },
  "missingPerson": {
    "pageTitle": "Report a Missing Person",
    "personName": "Name",
    "age": "Age",
    "gender": "Gender",
    "lastSeenLocation": "Last seen location",
    "lastSeenDateTime": "Last seen date & time",
    "reporterName": "Your name",
    "reporterContact": "Your contact number",
    "confirmTitle": "Report submitted",
    "policeNote": "This report is visible to platform administrators for this pilot. It is not automatically sent to police — please also contact police directly."
  },
  "admin": {
    "loginTitle": "Admin Login",
    "dashboard": "Dashboard",
    "statusDraft": "Draft",
    "statusPublished": "Published",
    "publish": "Publish",
    "unpublish": "Unpublish",
    "createNew": "Create new",
    "edit": "Edit"
  }
}
```

`hi.json` mirrors this exact key structure. Every value not provided by a verified Hindi
translation is written as English text prefixed `[HI-TODO]` so it is greppable and cannot be
mistaken for a real translation:

```json
{
  "common": {
    "appName": "Simhastha 2028",
    "skipToContent": "[HI-TODO] Skip to main content",
    "loading": "[HI-TODO] Loading...",
    "retry": "[HI-TODO] Try again",
    "lastUpdated": "[HI-TODO] Last updated: {date}",
    "submit": "[HI-TODO] Submit",
    "cancel": "[HI-TODO] Cancel"
  }
}
```
(Full `hi.json` mirrors every key from `en.json` above with `[HI-TODO]` prefixes — Frontend
should generate it 1:1 from `en.json`, not hand-author, to avoid missed keys. Do not fabricate
Hindi text; a native reviewer should replace `[HI-TODO]` entries before this leaves prototype
status, per spec: "placeholder translations flagged for review.")

**Exception**: `appName` ("Simhastha 2028") is a proper noun and stays identical in both
locale files, no `[HI-TODO]` needed.

---

## 6. Cross-reference

- Design tokens, safety banner full spec, accessibility notes → `UX_DESIGN_SYSTEM.md`
- Open items needing a PM/Backend/Frontend decision are marked **flagged** throughout this
  doc (see: ghat detail page, lost-found/missing-person status lookup API, admin CRUD API
  paths, SOS endpoint path, temple/event slug format for numeric names).
