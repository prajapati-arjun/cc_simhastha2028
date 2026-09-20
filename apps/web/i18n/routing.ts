import { defineRouting } from "next-intl/routing";

/**
 * EN + HI only (UX_PAGE_ARCHITECTURE.md §5).
 * `as-needed` keeps English on un-prefixed paths (/temples) and serves Hindi at
 * /hi/temples, so the route table in the UX doc stays literally accurate.
 */
export const routing = defineRouting({
  locales: ["en", "hi"],
  defaultLocale: "en",
  localePrefix: "as-needed",
});

export type AppLocale = (typeof routing.locales)[number];
