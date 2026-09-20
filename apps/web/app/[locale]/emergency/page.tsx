import { getTranslations } from "next-intl/server";
import { EmergencyServiceCard } from "@/components/Card";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { PageHeading } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import SafetyBanner from "@/components/SafetyBanner";
import { EmptyState, ErrorState } from "@/components/States";
import { Link } from "@/i18n/navigation";
import { getEmergencyServices } from "@/lib/api";
import type { EmergencyCategory, EmergencyService } from "@/lib/types";

export const dynamic = "force-dynamic";

const CATEGORY_ORDER: EmergencyCategory[] = [
  "police",
  "ambulance",
  "fire",
  "medical",
  "women_child",
  "disaster_mgmt",
  "help_center",
];

export default async function EmergencyPage() {
  const t = await getTranslations("emergency");
  const result = await getEmergencyServices();

  const grouped = new Map<EmergencyCategory, EmergencyService[]>();
  if (result.ok) {
    for (const service of result.data.items) {
      const bucket = grouped.get(service.category) ?? [];
      bucket.push(service);
      grouped.set(service.category, bucket);
    }
  }

  return (
    <div className="container-app section-y">
      <PageHeading title={t("pageTitle")} intro={t("pageIntro")} />

      {/* Placement rule: inline, top of page content, below the page H1. */}
      <SafetyBanner variant="emergency" />

      {/* Static, UI-authored real-world guidance. Deliberately NOT a seeded,
          callable directory row — see API_CONTRACT.md §4. */}
      <section
        className="mt-6 rounded-md border border-surface-border bg-surface-subtle p-4"
        aria-labelledby="real-emergency-heading"
      >
        <h2 id="real-emergency-heading" className="text-xl font-semibold">
          {t("realWorldGuidanceTitle")}
        </h2>
        <p className="mt-2 text-ink-primary">{t("realWorldGuidance")}</p>
      </section>

      <div className="mt-6">
        <Link
          href="/emergency/sos"
          className="btn-secondary min-h-[3.5rem] w-full text-lg sm:w-auto"
        >
          {t("sosButton")} — {t("sosCta")}
        </Link>
      </div>

      {!result.ok ? (
        <div className="mt-8">
          <ErrorState detail={result.error} action={<RetryLink />} />
        </div>
      ) : result.data.items.length === 0 ? (
        <div className="mt-8">
          <EmptyState message={t("emptyState")} />
        </div>
      ) : (
        <>
          <DataFreshnessTimestamp
            className="mt-8"
            updatedAt={result.data.last_updated}
          />
          {CATEGORY_ORDER.filter((category) => grouped.has(category)).map(
            (category) => (
              <section
                key={category}
                className="mt-8"
                aria-labelledby={`category-${category}`}
              >
                <h2 id={`category-${category}`} className="text-xl font-semibold md:text-2xl">
                  {t(`category.${category}`)}
                </h2>
                <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
                  {grouped.get(category)!.map((service) => (
                    <EmergencyServiceCard key={service.id} service={service} />
                  ))}
                </div>
              </section>
            ),
          )}
        </>
      )}
    </div>
  );
}
