"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import { Link, usePathname } from "@/i18n/navigation";
import LanguageSelector from "./LanguageSelector";

/**
 * SiteHeader — UX_PAGE_ARCHITECTURE.md §3.
 *
 * Carries three non-negotiables:
 *  1. Skip link to #main-content (design system §5.5).
 *  2. Language selector visible without opening a nested menu (§5 / PRD §6).
 *  3. Persistent emergency CTA in the header bar itself — NOT inside the
 *     hamburger menu — so it is reachable on mobile without scrolling (PRD §6).
 */

const NAV_ITEMS = [
  { href: "/events", key: "events" },
  { href: "/temples", key: "temples" },
  { href: "/ghats", key: "ghats" },
  { href: "/parking", key: "parking" },
  { href: "/accommodation", key: "accommodation" },
  { href: "/map", key: "map" },
  { href: "/planner", key: "planner" },
  { href: "/lost-found/report", key: "lostFound" },
  { href: "/missing-person/report", key: "missingPerson" },
] as const;

export function SiteHeader() {
  const t = useTranslations("nav");
  const tc = useTranslations("common");
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary-700 focus:px-4 focus:py-3 focus:text-white"
      >
        {tc("skipToContent")}
      </a>

      <header className="sticky top-0 z-50 border-b border-surface-border bg-surface-bg">
        <div className="container-app flex h-16 items-center justify-between gap-2">
          <Link
            href="/"
            className="touch-target flex-col items-start rounded-md px-1 leading-tight"
          >
            <span className="text-base font-bold text-primary-700 md:text-lg">
              {tc("appName")}
            </span>
            <span className="hidden text-xs text-ink-secondary sm:block">
              {tc("appTagline")}
            </span>
          </Link>

          <nav
            aria-label={t("mainLabel")}
            className="hidden items-center gap-1 lg:flex"
          >
            {NAV_ITEMS.map((item) => {
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={[
                    "touch-target rounded-md px-3 text-sm font-medium",
                    active
                      ? "bg-primary-50 text-primary-700"
                      : "text-ink-primary hover:bg-surface-subtle",
                  ].join(" ")}
                >
                  {t(item.key)}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-2">
            <LanguageSelector />
            <Link
              href="/emergency"
              aria-label={t("emergencyCtaAria")}
              className="touch-target gap-1.5 rounded-md bg-status-danger px-3 text-sm font-bold text-white hover:bg-red-800"
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5 fill-current">
                <path d="M10 2h4v6h6v4h-6v6h-4v-6H4V8h6V2Z" />
              </svg>
              <span className="hidden sm:inline">{t("emergencyCta")}</span>
            </Link>
            <button
              type="button"
              className="touch-target rounded-md border border-surface-border px-2 lg:hidden"
              aria-expanded={menuOpen}
              aria-controls="mobile-nav"
              aria-label={menuOpen ? tc("closeMenu") : tc("openMenu")}
              onClick={() => setMenuOpen((open) => !open)}
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" className="h-6 w-6 fill-current">
                {menuOpen ? (
                  <path d="m5 6.4 1.4-1.4 5.6 5.6 5.6-5.6L19 6.4 13.4 12 19 17.6 17.6 19 12 13.4 6.4 19 5 17.6 10.6 12 5 6.4Z" />
                ) : (
                  <path d="M3 6h18v2H3V6Zm0 5h18v2H3v-2Zm0 5h18v2H3v-2Z" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {menuOpen ? (
          <nav
            id="mobile-nav"
            aria-label={t("mainLabel")}
            className="border-t border-surface-border bg-surface-bg lg:hidden"
          >
            <ul className="container-app flex flex-col py-2">
              {NAV_ITEMS.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={() => setMenuOpen(false)}
                    className="touch-target w-full justify-start rounded-md px-2 text-base font-medium text-ink-primary hover:bg-surface-subtle"
                  >
                    {t(item.key)}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        ) : null}
      </header>
    </>
  );
}

export default SiteHeader;
