"use client";

import { useLocale, useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useTransition } from "react";
import { usePathname, useRouter } from "@/i18n/navigation";
import { routing, type AppLocale } from "@/i18n/routing";

/**
 * EN | HI switch (UX_PAGE_ARCHITECTURE.md §5).
 * Short labels to save header space; full language names live in aria-label.
 * Switching preserves the current route rather than redirecting to the homepage.
 */

const LABELS: Record<AppLocale, { short: string; full: string }> = {
  en: { short: "EN", full: "English" },
  hi: { short: "हिं", full: "हिन्दी (Hindi)" },
};

export function LanguageSelector() {
  const locale = useLocale() as AppLocale;
  const pathname = usePathname();
  const router = useRouter();
  const params = useParams();
  const [isPending, startTransition] = useTransition();
  const t = useTranslations("common");

  function switchTo(next: AppLocale) {
    if (next === locale) return;
    startTransition(() => {
      router.replace(
        // @ts-expect-error -- pathname is a runtime string; params carry dynamic segments
        { pathname, params },
        { locale: next },
      );
    });
  }

  return (
    <div
      className="flex items-center rounded-full border border-surface-border bg-surface-bg p-0.5"
      role="group"
      aria-label={t("appName") + " language"}
    >
      {routing.locales.map((code) => {
        const active = code === locale;
        return (
          <button
            key={code}
            type="button"
            lang={code}
            onClick={() => switchTo(code)}
            aria-current={active ? "true" : undefined}
            aria-label={LABELS[code].full}
            disabled={isPending}
            className={[
              "touch-target rounded-full px-3 text-sm font-semibold transition-colors",
              active
                ? "bg-primary-500 text-white"
                : "text-primary-700 hover:bg-primary-50",
            ].join(" ")}
          >
            {LABELS[code].short}
          </button>
        );
      })}
    </div>
  );
}

export default LanguageSelector;
