import type { ReactNode } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import StatusBadge from "./StatusBadge";
import { formatDateTime } from "@/lib/format";
import type {
  EmergencyService,
  EventItem,
  Ghat,
  GhatStatus,
  Temple,
} from "@/lib/types";

/** Shared card shell: optional media, title, meta rows, whole-card link. */
export function CardBase({
  href,
  title,
  badge,
  media,
  children,
}: {
  href?: string;
  title: string;
  badge?: ReactNode;
  media?: ReactNode;
  children?: ReactNode;
}) {
  const body = (
    <>
      {media}
      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold leading-snug text-ink-primary">
            {title}
          </h3>
          {badge}
        </div>
        {children}
      </div>
    </>
  );

  const className =
    "card-surface flex h-full min-h-touch flex-col overflow-hidden transition-shadow hover:shadow-raised";

  if (!href) {
    return <article className={className}>{body}</article>;
  }

  return (
    <article className={className}>
      <Link href={href} className="flex h-full flex-col rounded-md">
        {body}
      </Link>
    </article>
  );
}

function CardImage({ src, alt }: { src: string | null; alt: string }) {
  if (!src) {
    return (
      <div
        aria-hidden="true"
        className="h-32 w-full bg-primary-50"
        role="presentation"
      />
    );
  }
  /* eslint-disable-next-line @next/next/no-img-element -- remote CMS hosts are
     not known in Sprint 1, so next/image remotePatterns cannot be allowlisted. */
  return <img src={src} alt={alt} className="h-32 w-full object-cover" />;
}

export function EventCard({ event }: { event: EventItem }) {
  const t = useTranslations("events");
  const locale = useLocale();
  const starts = formatDateTime(event.starts_at, locale);

  return (
    <CardBase
      href={`/events/${event.slug}`}
      title={event.title}
      badge={<StatusBadge label={t(`category.${event.category}`)} tone="info" />}
      media={<CardImage src={event.image_url} alt={event.title} />}
    >
      {starts ? (
        <p className="text-sm font-medium text-ink-primary">
          <time dateTime={event.starts_at}>{starts}</time>
        </p>
      ) : null}
      {event.venue_name ? (
        <p className="text-sm text-ink-secondary">
          {t("venue")}: {event.venue_name}
        </p>
      ) : null}
      {event.summary ? (
        <p className="text-sm text-ink-secondary">{event.summary}</p>
      ) : null}
    </CardBase>
  );
}

export function TempleCard({ temple }: { temple: Temple }) {
  const t = useTranslations("temples");
  return (
    <CardBase
      href={`/temples/${temple.slug}`}
      title={temple.name}
      badge={
        temple.verified ? (
          <StatusBadge label={t("verified")} tone="success" />
        ) : undefined
      }
      media={<CardImage src={temple.image_url} alt={temple.name} />}
    >
      {temple.short_description ? (
        <p className="text-sm text-ink-secondary">{temple.short_description}</p>
      ) : null}
    </CardBase>
  );
}

export function GhatCard({
  ghat,
  status,
}: {
  ghat: Ghat;
  status: GhatStatus | null;
}) {
  const t = useTranslations("ghats");
  const tc = useTranslations("common");
  return (
    <CardBase
      href={`/ghats/${ghat.slug}`}
      title={ghat.name}
      badge={
        status ? (
          <StatusBadge
            label={t(`status.${status.status}`)}
            tone={
              status.status === "open"
                ? "success"
                : status.status === "restricted"
                  ? "warning"
                  : "danger"
            }
          />
        ) : undefined
      }
      media={<CardImage src={ghat.image_url} alt={ghat.name} />}
    >
      {ghat.description ? (
        <p className="text-sm text-ink-secondary">{ghat.description}</p>
      ) : null}
      {/* crowd_level is always null in Sprint 1 — never render a fake density badge */}
      <p className="text-sm text-ink-muted">{tc("crowdLevelUnavailable")}</p>
    </CardBase>
  );
}

export function EmergencyServiceCard({
  service,
}: {
  service: EmergencyService;
}) {
  const t = useTranslations("emergency");
  return (
    <CardBase title={service.name}>
      <p>
        <a
          href={`tel:${service.phone.replace(/[^+\d]/g, "")}`}
          className="touch-target justify-start rounded-md px-0 text-base font-semibold text-primary-700 underline underline-offset-2"
          aria-label={t("callLabel", { name: service.name })}
        >
          {service.phone}
        </a>
      </p>
      {service.address ? (
        <p className="text-sm text-ink-secondary">{service.address}</p>
      ) : null}
      {service.hours ? (
        <p className="text-sm text-ink-secondary">
          {t("hours")}: {service.hours}
        </p>
      ) : null}
      {service.notes ? (
        <p className="text-sm font-medium text-secondary-700">{service.notes}</p>
      ) : null}
    </CardBase>
  );
}
