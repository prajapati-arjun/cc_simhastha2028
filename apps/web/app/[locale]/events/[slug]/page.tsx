import { getLocale, getTranslations } from "next-intl/server";
import CachedDataFreshness from "@/components/CachedDataFreshness";
import { Breadcrumb, DetailSection } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import StatusBadge from "@/components/StatusBadge";
import { ErrorState } from "@/components/States";
import { Link } from "@/i18n/navigation";
import { getEvent } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export const dynamic = "force-dynamic";

export default async function EventDetailPage({
  params,
}: {
  params: { slug: string };
}) {
  const t = await getTranslations("events");
  const locale = await getLocale();
  const result = await getEvent(params.slug);

  if (!result.ok) {
    const notFound = result.status === 404;
    return (
      <div className="container-reading section-y">
        <ErrorState
          title={notFound ? t("notFound") : undefined}
          message={notFound ? t("backToList") : undefined}
          detail={notFound ? null : result.error}
          action={
            notFound ? (
              <Link href="/events" className="btn-outline">
                {t("backToList")}
              </Link>
            ) : (
              <RetryLink />
            )
          }
        />
      </div>
    );
  }

  const event = result.data;
  const starts = formatDateTime(event.starts_at, locale);
  const ends = formatDateTime(event.ends_at, locale);
  const hasGeo = event.latitude !== null && event.longitude !== null;

  return (
    <article className="container-reading section-y">
      <Breadcrumb
        items={[
          { href: "/events", label: t("pageTitle") },
          { label: event.title },
        ]}
      />
      <h1>{event.title}</h1>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <StatusBadge label={t(`category.${event.category}`)} tone="info" />
      </div>
      {event.summary ? (
        <p className="mt-4 text-lg text-ink-secondary">{event.summary}</p>
      ) : null}

      <dl className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {starts ? (
          <div>
            <dt className="text-sm font-semibold text-ink-secondary">{t("starts")}</dt>
            <dd>
              <time dateTime={event.starts_at}>{starts}</time>
            </dd>
          </div>
        ) : null}
        {ends ? (
          <div>
            <dt className="text-sm font-semibold text-ink-secondary">{t("ends")}</dt>
            <dd>
              <time dateTime={event.ends_at ?? undefined}>{ends}</time>
            </dd>
          </div>
        ) : null}
        {event.venue_name ? (
          <div>
            <dt className="text-sm font-semibold text-ink-secondary">{t("venue")}</dt>
            <dd>{event.venue_name}</dd>
          </div>
        ) : null}
      </dl>

      {event.description ? (
        <DetailSection title={t("about")}>
          <p className="whitespace-pre-line">{event.description}</p>
        </DetailSection>
      ) : null}

      {hasGeo ? (
        <p className="mt-6">
          <Link
            href={{
              pathname: "/map",
              query: { focus: `event:${event.slug}`, lat: String(event.latitude), lng: String(event.longitude) },
            }}
            className="btn-outline"
          >
            {t("venue")}
          </Link>
        </p>
      ) : null}

      <CachedDataFreshness className="mt-8" updatedAt={event.updated_at} />
    </article>
  );
}
