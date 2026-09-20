import { getTranslations } from "next-intl/server";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { Breadcrumb, DetailSection } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import StatusBadge from "@/components/StatusBadge";
import { ErrorState } from "@/components/States";
import { Link } from "@/i18n/navigation";
import { getGhatStatus, getGhats } from "@/lib/api";

export const dynamic = "force-dynamic";

const KNOWN_FACILITIES = [
  "changing_rooms",
  "drinking_water",
  "toilets",
  "first_aid",
  "lighting",
  "ramp_access",
];

export default async function GhatDetailPage({
  params,
}: {
  params: { slug: string };
}) {
  const t = await getTranslations("ghats");
  const tc = await getTranslations("common");

  // Decision D-03: no dedicated ghat-detail endpoint exists; the directory
  // payload plus /status is enough for this deliberately light page.
  const [listResult, statusResult] = await Promise.all([
    getGhats({ limit: 100 }),
    getGhatStatus(params.slug),
  ]);

  if (!listResult.ok) {
    return (
      <div className="container-reading section-y">
        <ErrorState detail={listResult.error} action={<RetryLink />} />
      </div>
    );
  }

  const ghat = listResult.data.items.find((item) => item.slug === params.slug);
  if (!ghat) {
    return (
      <div className="container-reading section-y">
        <ErrorState
          title={t("notFound")}
          action={
            <Link href="/ghats" className="btn-outline">
              {t("backToList")}
            </Link>
          }
        />
      </div>
    );
  }

  const status = statusResult.ok ? statusResult.data : null;

  return (
    <article className="container-reading section-y">
      <Breadcrumb
        items={[{ href: "/ghats", label: t("pageTitle") }, { label: ghat.name }]}
      />
      <h1>{ghat.name}</h1>

      <div className="card-surface mt-4 p-4">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-sm font-semibold text-ink-secondary">
            {t("statusLabel")}:
          </span>
          {status ? (
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
          ) : (
            <span className="text-sm text-ink-muted">{t("statusUnavailable")}</span>
          )}
        </div>
        {/* crowd_level is always null this sprint — never a fabricated badge. */}
        <p className="mt-2 text-sm text-ink-muted">{tc("crowdLevelUnavailable")}</p>
        <p className="mt-2 text-sm">
          <span className="font-semibold">{t("advisory")}: </span>
          {status?.advisory ?? t("noAdvisory")}
        </p>
        {status ? (
          <p className="mt-2 text-xs text-ink-secondary">{status.prototype_notice}</p>
        ) : null}
      </div>

      {ghat.description ? (
        <p className="mt-6 text-lg text-ink-secondary">{ghat.description}</p>
      ) : null}

      {ghat.bathing_info ? (
        <DetailSection title={t("bathingInfo")}>
          <p className="whitespace-pre-line">{ghat.bathing_info}</p>
        </DetailSection>
      ) : null}

      <DetailSection title={t("facilities")}>
        {ghat.facilities && ghat.facilities.length > 0 ? (
          <ul className="flex flex-wrap gap-2">
            {ghat.facilities.map((facility) => (
              <li key={facility}>
                <StatusBadge
                  label={
                    KNOWN_FACILITIES.includes(facility)
                      ? t(`facility.${facility}`)
                      : facility
                  }
                  tone="info"
                />
              </li>
            ))}
          </ul>
        ) : (
          <p>{tc("notAvailable")}</p>
        )}
      </DetailSection>

      <DetailSection title={t("accessibility")}>
        <p>{ghat.accessibility_info ?? tc("notAvailable")}</p>
      </DetailSection>

      {ghat.latitude !== null && ghat.longitude !== null ? (
        <p className="mt-6">
          <Link
            href={{ pathname: "/map", query: { focus: `ghat:${ghat.slug}` } }}
            className="btn-outline"
          >
            {t("pageTitle")}
          </Link>
        </p>
      ) : null}

      <DataFreshnessTimestamp
        className="mt-8"
        updatedAt={status?.updated_at ?? ghat.updated_at}
      />
    </article>
  );
}
