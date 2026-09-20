import type { Config } from "tailwindcss";

// Sprint 1 scaffold: base Tailwind config with no custom theme yet.
// UX Architect (UX-03) owns the design-token extension (colors, spacing,
// typography) — Frontend Developer wires it in here under `theme.extend`.
const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
