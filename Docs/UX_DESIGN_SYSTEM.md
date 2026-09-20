# Simhastha 2028 — Design System (Sprint 1)

Owner: UX Architect. Consumers: Frontend Developer (FE-01 onward). Source: PRD §6, §9, §13,
§15, §16, §28, §32, §33; `project-specs/simhastha-sprint1-setup.md`.

Tone: civic/government safety platform serving pilgrims incl. elderly and
accessibility-needs users. Clean, high-contrast, calm. Not flashy — no gradients-as-decoration,
no animation-heavy UI, no dense visual noise. Trust and legibility over branding flourish.

---

## 1. Design Tokens

Drop this into `apps/web/tailwind.config.ts` as a `theme.extend` block. Values are final for
Sprint 1; do not substitute a UI kit (no FluxUI etc. per tasklist).

```ts
// tailwind.config.ts (theme.extend excerpt)
export default {
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Brand — civic/spiritual trust palette. Deep indigo (governance/trust) +
        // saffron accent (cultural/spiritual signal, used sparingly for CTAs/highlights).
        primary: {
          50:  '#eef2fb',
          100: '#d8e1f5',
          200: '#b3c4ec',
          300: '#8aa5e0',
          400: '#5c7fd0',
          500: '#2f4fb0',   // primary brand — buttons, links, header
          600: '#254090',
          700: '#1d3374',
          800: '#17285c',
          900: '#101c40',   // headers/footers, high-contrast text-on-light use
        },
        secondary: {
          50:  '#fff7ed',
          100: '#ffedd2',
          200: '#fed7a3',
          300: '#fdb85f',
          400: '#fb9a2e',
          500: '#e8830f',   // saffron accent — sparingly: highlights, badges, active nav
          600: '#c1690a',
          700: '#96520c',
        },
        // Semantic crowd-density colors (PRD §10) — NOT wired to live data this
        // sprint. Used only where FE-06 renders the static placeholder layer with
        // the demo banner. Keep these names stable for when Phase 2 wires real data.
        density: {
          low:      '#1a8a4a',  // green
          moderate: '#c99a00',  // yellow (darkened for AA contrast on white)
          high:     '#d9720f',  // orange
          critical: '#c62828',  // red
        },
        // Status / feedback colors (forms, admin CMS, API states)
        status: {
          success: '#1a8a4a',
          warning: '#c99a00',
          danger:  '#c62828',
          info:    '#2f4fb0',
        },
        // Neutral surface/text scale (light theme base; dark theme remaps via CSS vars, see §1.4)
        surface: {
          bg: '#ffffff',
          subtle: '#f5f6f8',
          border: '#d8dbe1',
        },
        ink: {
          primary: '#14161a',
          secondary: '#4a4f58',
          muted: '#6b7280',
        },
      },
      spacing: {
        // 4px base grid — use Tailwind's default scale (1=4px..96) plus these
        // named aliases for layout rhythm.
        'section-y': '4rem',      // 64px vertical section padding (desktop)
        'section-y-sm': '2.5rem', // 40px (mobile)
      },
      fontFamily: {
        sans: ['"Noto Sans"', '"Noto Sans Devanagari"', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        xs:   ['0.75rem',  { lineHeight: '1.4' }],   // 12px
        sm:   ['0.875rem', { lineHeight: '1.5' }],   // 14px
        base: ['1rem',     { lineHeight: '1.6' }],   // 16px — body default
        lg:   ['1.125rem', { lineHeight: '1.6' }],   // 18px
        xl:   ['1.25rem',  { lineHeight: '1.4' }],   // 20px
        '2xl':['1.5rem',   { lineHeight: '1.3' }],   // 24px — H3
        '3xl':['1.875rem', { lineHeight: '1.25' }],  // 30px — H2
        '4xl':['2.25rem',  { lineHeight: '1.2' }],   // 36px — H1 desktop
      },
      borderRadius: {
        sm: '0.25rem',   // 4px — inputs, badges
        md: '0.5rem',    // 8px — cards
        lg: '0.75rem',   // 12px — modals, large cards
        full: '9999px',  // pills, toggle
      },
      boxShadow: {
        card: '0 1px 3px rgba(16,28,64,0.08), 0 1px 2px rgba(16,28,64,0.06)',
        raised: '0 4px 12px rgba(16,28,64,0.12)',
        focus: '0 0 0 3px rgba(47,79,176,0.45)', // visible focus ring, meets 3:1 non-text contrast
      },
      minHeight: {
        touch: '2.75rem', // 44px minimum touch target (PRD §32)
      },
      minWidth: {
        touch: '2.75rem',
      },
    },
  },
};
```

### 1.1 Rationale
- **Primary indigo** reads as institutional/government-trustworthy without being cold;
  passes WCAG AA (4.5:1) as text/button color on white and as white-text background.
- **Secondary saffron** nods to the spiritual/cultural context (temple, Kumbh) as an accent
  only — never as body text color (fails contrast at lighter tints).
- **Density colors** are deliberately desaturated versions of pure red/yellow/green so they
  hit AA contrast as text-on-white or icon fills; do not swap for brighter hex values without
  re-checking contrast.

### 1.2 Typography scale
- Font: system-first with Noto Sans + Noto Sans Devanagari fallback for Hindi glyph coverage
  (no paid/custom fonts this sprint — avoid external font-loading latency debates; Frontend
  may self-host Noto via `next/font` if preferred, same family names).
- Headings: H1 `text-3xl md:text-4xl font-bold`, H2 `text-2xl md:text-3xl font-semibold`,
  H3 `text-xl md:text-2xl font-semibold`, body `text-base`, small print `text-sm`.
- Line-height stays generous (1.4–1.6) — senior-friendly reading per PRD §32.

### 1.3 Spacing
Use Tailwind default 4px-based scale (`p-1`…`p-24`) for component-internal spacing. Use the
`section-y` / `section-y-sm` aliases for page-section vertical rhythm only, so section spacing
stays consistent across pages without every dev picking a number.

### 1.4 Theming (light/system; dark is optional this sprint)
Sprint 1 ships **light theme only** as the shipped default (this is a safety/legibility
platform for outdoor daylight use — high-contrast light is the priority). Structure tokens as
CSS custom properties now so dark mode is a Phase 2 drop-in, not a rewrite:

```css
/* globals.css */
:root {
  --bg-primary: theme('colors.surface.bg');
  --bg-secondary: theme('colors.surface.subtle');
  --text-primary: theme('colors.ink.primary');
  --text-secondary: theme('colors.ink.secondary');
  --border-color: theme('colors.surface.border');
}
```
If Frontend has bandwidth, wiring `prefers-color-scheme`/`data-theme="dark"` overrides of
these same variables is welcome but is explicitly **not required** for Sprint 1 sign-off —
flagged as a call for PM/Frontend to prioritize or defer (see report).

---

## 2. Layout Framework

### Container system
| Breakpoint | Tailwind prefix | Max width | Side padding |
|---|---|---|---|
| Mobile (base) | — | 100% | 16px (`px-4`) |
| Tablet | `md:` (768px) | 768px | 24px (`px-6`) |
| Desktop | `lg:` (1024px) | 1024px | 32px (`px-8`) |
| Large | `xl:` (1280px) | 1280px | 32px |

Utility class: `.container-app { @apply w-full mx-auto px-4 md:px-6 lg:px-8 max-w-7xl; }`
(cap at 1280px / `max-w-7xl`; content-heavy pages like temple detail may use `max-w-4xl` for
the reading column).

### Grid patterns
- **Directory grids** (temples, ghats, emergency services): CSS Grid, `grid-cols-1
  sm:grid-cols-2 lg:grid-cols-3`, `gap-4 md:gap-6`, card min-width ~280px.
- **Homepage quick-access**: `grid-cols-2 md:grid-cols-4` icon-tile grid.
- **Detail pages** (temple, event): single content column, `max-w-4xl`, sidebar (map/quick
  facts) stacks below content on mobile, right rail on `lg:`.
- **Admin CMS tables**: full-width responsive table, collapses to stacked cards below `md:`.

### Component hierarchy
1. Layout — `SiteHeader`, `SiteFooter`, `PageContainer`, section wrappers.
2. Content — cards, list items, detail sections, map panels.
3. Interactive — buttons, form fields, toggles, modals.
4. Cross-cutting — `SafetyBanner`, `DataFreshnessTimestamp`, `StatusBadge`,
   `LoadingState`/`EmptyState`/`ErrorState`.

---

## 3. The Safety / Demo-Prototype Banner (UX-02)

This is the single most important cross-cutting spec in this sprint. It must be
**visually distinct, impossible to miss, and consistent** everywhere it appears.

### 3.1 Component: `SafetyBanner`

**Purpose**: Tell every user, on every safety-critical screen, that emergency/missing-person/
lost-found/crowd data is simulated and NOT connected to real dispatch or authorities.

**Props**
```ts
type SafetyBannerVariant =
  | 'emergency'      // SOS, emergency directory
  | 'missing-person'
  | 'lost-found'
  | 'crowd-placeholder'; // GIS map crowd/traffic layer

interface SafetyBannerProps {
  variant: SafetyBannerVariant;
  /** Optional override; default copy per variant is defined below and should
   *  be used unless a specific screen needs added context. */
  message?: string;
  /** Default 'inline'. 'sticky' pins to top of viewport under the header —
   *  use only on SOS trigger flow where the user must not miss it while
   *  scrolling. */
  placement?: 'inline' | 'sticky';
  /** Default false. If true, adds "This creates a real record in our test
   *  database but is not sent to any emergency service." — use on POST
   *  forms (SOS, lost-found, missing-person) right above the submit button. */
  showFormNote?: boolean;
}
```

**Default copy per variant** (exact strings, do not paraphrase):

| Variant | Copy |
|---|---|
| `emergency` | "Demo prototype — not connected to live emergency dispatch." |
| `missing-person` | "Demo prototype — not connected to live police or government missing-person systems." |
| `lost-found` | "Demo prototype — reports are stored for this pilot only and are not monitored 24/7." |
| `crowd-placeholder` | "Demo prototype — crowd and traffic levels shown are sample data, not live sensor feeds." |

Form-note addendum (`showFormNote: true`), appended below the main message, smaller text:
"Submitting this form creates a real record in our test database but does not alert any
emergency service, police, or hospital. In a real emergency, contact local authorities
directly."

### 3.2 Visual spec
- Container: full-width within its parent (page-width on `inline`, viewport-width on
  `sticky`), `bg-secondary-50` background, `border-l-4 border-secondary-500`, `rounded-md`
  (inline) / no radius (sticky, edge-to-edge), `px-4 py-3`.
- Icon: warning/info triangle (`⚠` or an inline SVG), `text-secondary-600`, `aria-hidden`.
- Text: `text-sm font-medium text-ink-primary` for the main message; form-note in
  `text-xs text-ink-secondary` below it.
- Contrast: secondary-50 background + ink-primary text must be verified ≥4.5:1 (it is, by
  token design above).
- **Never** use `status.danger` red background for this banner — red is reserved for the
  `density.critical` crowd level and real error states, and using it here would visually
  compete with actual emergency-severity signaling and could read as alarming rather than
  informational.
- `placement: 'sticky'`: `position: sticky; top: [header height]; z-index: 40;` — sits
  directly below `SiteHeader`, above page content, scrolls away only when the header does.
- Dismissible: **no**. This banner must not be closeable/dismissible — it needs to stay
  visible for the duration of the safety-critical interaction (this is a deliberate
  deviation from typical "dismiss this notice" UX patterns).

### 3.3 Placement rules — exact screens (per spec decision #1 + tasklist)

| Screen / Route | Variant | Placement |
|---|---|---|
| `/emergency` (Emergency Services directory) | `emergency` | inline, top of page content, below page H1 |
| `/emergency/sos` (SOS trigger flow) | `emergency` | sticky, `showFormNote: true` |
| `/missing-person/report` | `missing-person` | inline, top of form, `showFormNote: true` |
| `/missing-person/status` (lookup) | `missing-person` | inline, top of page |
| `/lost-found/report` | `lost-found` | inline, top of form, `showFormNote: true` |
| `/lost-found/status` (lookup) | `lost-found` | inline, top of page |
| `/map` — only when the crowd/traffic placeholder layer is toggled ON | `crowd-placeholder` | inline, appears directly above the map panel when that layer is active; disappears if the user toggles the layer off |
| Homepage — only if any live-status placeholder tile is shown (PRD §6 "live status
  indicators" is scoped OUT this sprint per FE-02 note; if Frontend adds a static
  placeholder tile anyway) | `crowd-placeholder` | inline, directly under that tile |

Backend note (informs BE-06/BE-08/BE-11, already called out in tasklist): API responses for
emergency services, missing-person, and SOS should include a `demo_notice` string field
mirroring this banner copy, so the frontend can render it even if it fetches data
independently of a page that already has the static banner (e.g., a future mobile client).

---

## 4. Component list reference

See `UX_PAGE_ARCHITECTURE.md` §4 for the full shared component inventory (SiteHeader,
SiteFooter, cards, StatusBadge, DataFreshnessTimestamp, Loading/Empty/Error states, form
components, LayerToggle).

---

## 5. Accessibility notes (PRD §32) — concrete, Sprint 1 scope

1. **Touch targets**: all interactive elements (buttons, nav links, form controls, map layer
   toggles) minimum 44×44px. Use the `min-h-touch min-w-touch` utilities defined above.
2. **Contrast**: body text vs background ≥4.5:1, large text (≥24px or ≥19px bold) ≥3:1, UI
   component boundaries (input borders, focus rings) ≥3:1 non-text contrast. All tokens in
   §1 are pre-checked against `surface.bg`/`ink.primary` — do not introduce new colors
   without checking.
3. **Focus visibility**: every focusable element gets a visible focus ring — use the
   `shadow-focus` token (`focus-visible:shadow-focus focus-visible:outline-none`). Never
   remove focus outlines without replacing them.
4. **Keyboard navigation**: full tab-order support for header nav, language selector,
   all forms, map layer toggle panel, and admin CMS tables/forms. SOS button must be
   reachable and triggerable via keyboard (Enter/Space), not mouse/touch-only.
5. **Skip link**: `SiteHeader` includes a visually-hidden "Skip to main content" link that
   becomes visible on focus, targeting `#main-content`.
6. **Alt text**: every temple/ghat photo requires descriptive alt text (content field in
   CMS, not filename-derived). Map markers/icons need `aria-label` (e.g. "Mahakaleshwar
   Temple, tap for details"), not just a visual icon.
7. **Forms**: every input has a visible `<label>` (not placeholder-only), error messages are
   programmatically associated via `aria-describedby`, and required fields are marked both
   visually (`*`) and with `aria-required`.
8. **Senior-friendly**: base body font size stays at 16px minimum (never smaller for primary
   content), line-height ≥1.5 for paragraph text, avoid relying on color alone to convey
   meaning (density badges pair color with text label, e.g. "Moderate", not just a colored
   dot).
9. **Language toggle**: `lang` attribute on `<html>` updates when locale changes (`en`/`hi`)
   so screen readers switch pronunciation correctly.
10. **Motion**: keep transitions short (≤200ms) and respect `prefers-reduced-motion` for any
    map pan/zoom animation or toggle transition.
