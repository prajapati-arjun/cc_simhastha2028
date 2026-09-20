import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { EventCard } from "@/components/Card";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { ErrorState } from "@/components/States";
import StatusBadge from "@/components/StatusBadge";
import { getAnnouncements, getEvents } from "@/lib/api";

// Safety, status and freshness data is never prerendered at build time.
export const dynamic = "force-dynamic";

const CTAS = [
  { href: "/map", key: "ctaMap" },
  { href: "/events", key: "ctaEvents" },
  { href: "/temples", key: "ctaTemples" },
  { href: "/emergency", key: "ctaEmergency" },
] as const;

const QUICK_ACCESS = [
  { href: "/temples", key: "ctaTemples" },
  { href: "/ghats", key: "quickAccessGhats" },
  { href: "/emergency", key: "ctaEmergency" },
  { href: "/lost-found/report", key: "quickAccessLostFound" },
] as const;

export default async function HomePage() {
  const t = await getTranslations("homepage");
  const [eventsResult, announcementsResult] = await Promise.all([
    getEvents({ limit: 6 }),
    getAnnouncements({ limit: 5 }),
  ]);

  return (
    <div>
      <section className="bg-primary-900 text-white">
        <div className="container-app section-y">
          <h1 className="text-white">{t("heroTitle")}</h1>
          <p className="mt-3 max-w-2xl text-lg text-primary-100">
            {t("heroSubtitle")}
          </p>
          <p className="mt-2 max-w-2xl text-sm text-primary-200">
            {t("prototypeIntro")}
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            {CTAS.map((cta, index) => (
              <Link
                key={cta.href}
                href={cta.href}
                className={
                  index === 0
                    ? "btn-secondary"
                    : "btn border border-white/40 bg-white/10 text-white hover:bg-white/20"
                }
              >
                {t(cta.key)}
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="container-app section-y" aria-labelledby="announcements-heading">
        <h2 id="announcements-heading">{t("announcementsTitle")}</h2>
        {announcementsResult.ok ? (
          announcementsResult.data.items.length > 0 ? (
            <>
              <DataFreshnessTimestamp
                className="mt-1"
                updatedAt={announcementsResult.data.last_updated}
              />
              <ul className="mt-4 flex snap-x gap-4 overflow-x-auto pb-2 md:grid md:grid-cols-2 md:overflow-visible">
                {announcementsResult.data.items.map((announcement) => (
                  <li
                    key={announcement.id}
                    className="card-surface min-w-[16rem] flex-1 snap-start p-4"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="text-lg font-semibold">{announcement.title}</h3>
                      <StatusBadge
                        label={announcement.priority}
                        tone={
                          announcement.priority === "critical"
                            ? "danger"
                            : announcement.priority === "important"
                              ? "warning"
                              : "neutral"
                        }
                      />
                    </div>
                    {announcement.body ? (
                      <p className="mt-2 text-sm text-ink-secondary">
                        {announcement.body}
                      </p>
                    ) : null}
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p className="mt-2 text-ink-secondary">{t("noAnnouncements")}</p>
          )
        ) : (
          <ErrorState detail={announcementsResult.error} />
        )}
      </section>

      <section
        className="bg-surface-subtle"
        aria-labelledby="events-heading"
      >
        <div className="container-app section-y">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 id="events-heading">{t("todaysEventsTitle")}</h2>
            <Link href="/events" className="link-inline">
              {t("viewAllEvents")}
            </Link>
          </div>
          {eventsResult.ok ? (
            <>
              <DataFreshnessTimestamp
                className="mt-1"
                updatedAt={eventsResult.data.last_updated}
              />
              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
                {eventsResult.data.items.map((event) => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>
            </>
          ) : (
            <div className="mt-4">
              <ErrorState detail={eventsResult.error} />
            </div>
          )}
        </div>
      </section>

      <section className="container-app section-y" aria-labelledby="quick-access-heading">
        <h2 id="quick-access-heading">{t("quickAccessTitle")}</h2>
        <ul className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
          {QUICK_ACCESS.map((tile) => (
            <li key={tile.href}>
              <Link
                href={tile.href}
                className="card-surface flex min-h-[6rem] flex-col items-center justify-center gap-2 p-4 text-center font-semibold text-primary-700 hover:shadow-raised"
              >
                {t(tile.key)}
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
