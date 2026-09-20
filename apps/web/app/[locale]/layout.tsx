import type { Metadata } from "next";
import { NextIntlClientProvider, hasLocale } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import ServiceWorkerRegister from "@/components/ServiceWorkerRegister";
import SiteFooter from "@/components/SiteFooter";
import SiteHeader from "@/components/SiteHeader";
import { routing } from "@/i18n/routing";
import "../globals.css";

export const metadata: Metadata = {
  title: {
    default: "Simhastha 2028 — Ujjain Digital Experience Platform",
    template: "%s | Simhastha 2028",
  },
  description:
    "Sprint 1 prototype of the Simhastha 2028 Ujjain Digital Experience Platform. Demo data only — not connected to live emergency dispatch.",
  manifest: "/manifest.json",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

/**
 * Locale params are intentionally NOT pre-generated.
 * Every content page reads live API data and the safety/status surfaces must
 * never be baked into a build artifact, so routes stay dynamic. Phase 2 can
 * reintroduce generateStaticParams for the genuinely static pages.
 */

export default function LocaleLayout({
  children,
  params: { locale },
}: {
  children: React.ReactNode;
  // Next.js 14 passes route params synchronously (the Promise form arrives in 15).
  params: { locale: string };
}) {
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }
  // Keeps <html lang> in sync with the active locale so screen readers switch
  // pronunciation correctly (design system §5.9).
  setRequestLocale(locale);

  return (
    <html lang={locale}>
      <body className="flex min-h-screen flex-col">
        <NextIntlClientProvider>
          <ServiceWorkerRegister />
          <SiteHeader />
          <main id="main-content" className="flex-1">
            {children}
          </main>
          <SiteFooter />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
