import type { Config } from "tailwindcss";

/**
 * Simhastha 2028 — Sprint 1 design tokens.
 * Source of truth: Docs/UX_DESIGN_SYSTEM.md §1. Values below are copied from that
 * spec verbatim; do not substitute a UI kit and do not invent new colors without
 * re-checking contrast (see UX_DESIGN_SYSTEM.md §5.2).
 *
 * Phase 2 dark theme (decision D-05: deferred, NOT built this sprint):
 * `darkMode` is pre-wired to `[data-theme="dark"]` and the semantic surface/ink
 * roles are consumed through CSS custom properties declared in app/globals.css.
 * Adding dark theme later is a token swap inside that one `:root` block plus a
 * `[data-theme="dark"]` sibling block — no component rewrite required.
 */
const config: Config = {
  darkMode: ["class", '[data-theme="dark"]'],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eef2fb",
          100: "#d8e1f5",
          200: "#b3c4ec",
          300: "#8aa5e0",
          400: "#5c7fd0",
          500: "#2f4fb0",
          600: "#254090",
          700: "#1d3374",
          800: "#17285c",
          900: "#101c40",
        },
        secondary: {
          50: "#fff7ed",
          100: "#ffedd2",
          200: "#fed7a3",
          300: "#fdb85f",
          400: "#fb9a2e",
          500: "#e8830f",
          600: "#c1690a",
          700: "#96520c",
        },
        // Crowd-density tokens (PRD §10). NOT wired to live data in Sprint 1 —
        // used only by the static placeholder map layer, which always ships with
        // SafetyBanner variant="crowd-placeholder".
        density: {
          low: "#1a8a4a",
          moderate: "#c99a00",
          high: "#d9720f",
          critical: "#c62828",
        },
        status: {
          success: "#1a8a4a",
          warning: "#c99a00",
          danger: "#c62828",
          info: "#2f4fb0",
        },
        surface: {
          bg: "#ffffff",
          subtle: "#f5f6f8",
          border: "#d8dbe1",
        },
        ink: {
          primary: "#14161a",
          secondary: "#4a4f58",
          muted: "#6b7280",
        },
        // Semantic aliases resolved through the CSS custom properties in
        // globals.css — use these in layout chrome so a Phase 2 theme swap is
        // a variable change rather than a class rewrite.
        app: {
          bg: "var(--bg-primary)",
          subtle: "var(--bg-secondary)",
          border: "var(--border-color)",
          text: "var(--text-primary)",
          "text-muted": "var(--text-secondary)",
        },
      },
      spacing: {
        "section-y": "4rem",
        "section-y-sm": "2.5rem",
      },
      fontFamily: {
        sans: [
          '"Noto Sans"',
          '"Noto Sans Devanagari"',
          "system-ui",
          "sans-serif",
        ],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1.4" }],
        sm: ["0.875rem", { lineHeight: "1.5" }],
        base: ["1rem", { lineHeight: "1.6" }],
        lg: ["1.125rem", { lineHeight: "1.6" }],
        xl: ["1.25rem", { lineHeight: "1.4" }],
        "2xl": ["1.5rem", { lineHeight: "1.3" }],
        "3xl": ["1.875rem", { lineHeight: "1.25" }],
        "4xl": ["2.25rem", { lineHeight: "1.2" }],
      },
      borderRadius: {
        sm: "0.25rem",
        md: "0.5rem",
        lg: "0.75rem",
        full: "9999px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(16,28,64,0.08), 0 1px 2px rgba(16,28,64,0.06)",
        raised: "0 4px 12px rgba(16,28,64,0.12)",
        focus: "0 0 0 3px rgba(47,79,176,0.45)",
      },
      minHeight: {
        touch: "2.75rem",
      },
      minWidth: {
        touch: "2.75rem",
      },
    },
  },
  plugins: [],
};

export default config;
