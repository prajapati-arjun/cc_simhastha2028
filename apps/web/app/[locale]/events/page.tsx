import { getTranslations } from "next-intl/server";
import { EventCard } from "@/components/Card";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { PageHeading } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import { EmptyState, ErrorState } from "@/components/States";
import { Link } from "@/i18n/navigation";
import { getEvents } from "@/lib/api";
import type { EventCategory } from "@/lib/types";

export const dynamic = "force-dynamic";

const CATEGORIES: EventCategory[] = [
  "snan_parva",
  "religious",
  "aarti",
  "akhada",
  "cultural",
  "government",
];

export default async function EventsPage({
  searchParams,
}: {
  searchParams: { category?: string };
}) {
  const t = await getTranslations("events");
  const activeCategory = CATEGORIES.includes(searchParams.category as EventCategory)
    ? (searchParams.category as EventCategory)
    : undefined;

  const result = await getEvents({ category: activeCategory, limit: 100 });

  return (
    <div className="container-app section-y">
      <PageHeading title={t("pageTitle")} intro={t("pageIntro")} />

      <nav aria-label={t("filterLabel")} className="mb-6">
        <ul className="flex flex-wrap gap-2">
          <li>
            <Link
              href="/events"
              aria-current={activeCategory ? undefined : "true"}
              className={[
                "touch-target rounded-full border px-4 text-sm font-medium",
                activeCategory
                  ? "border-surface-border bg-surface-bg text-ink-primary"
                  : "border-primary-500 bg-primary-500 text-white",
              ].join(" ")}
            >
              {t("filterAll")}
            </Link>
          </li>
          {CATEGORIES.map((category) => {
            const active = category === activeCategory;
            return (
              <li key={category}>
                <Link
                  href={{ pathname: "/events", query: { category } }}
                  aria-current={active ? "true" : undefined}
                  className={[
                    "touch-target rounded-full border px-4 text-sm font-medium",
                    active
                      ? "border-primary-500 bg-primary-500 text-white"
                      : "border-surface-border bg-surface-bg text-ink-primary",
                  ].join(" ")}
                >
                  {t(`category.${category}`)}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {!result.ok ? (
        <ErrorState detail={result.error} action={<RetryLink />} />
      ) : result.data.items.length === 0 ? (
        <EmptyState message={t("emptyState")} />
      ) : (
        <>
          <DataFreshnessTimestamp updatedAt={result.data.last_updated} />
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
            {result.data.items.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
