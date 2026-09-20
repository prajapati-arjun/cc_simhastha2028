import { getTranslations } from "next-intl/server";
import CachedDataFreshness from "@/components/CachedDataFreshness";
import { Breadcrumb, DetailSection } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import StatusBadge from "@/components/StatusBadge";
import { ErrorState } from "@/components/States";
import { Link } from "@/i18n/navigation";
import { getTemple } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TempleDetailPage({
  params,
}: {
  params: { slug: string };
}) {
  const t = await getTranslations("temples");
  const result = await getTemple(params.slug);

  if (!result.ok) {
    const missing = result.status === 404;
    return (
      <div className="container-reading section-y">
        <ErrorState
          title={missing ? t("notFound") : undefined}
          detail={missing ? null : result.error}
          action={
            missing ? (
              <Link href="/temples" className="btn-outline">
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

  const temple = result.data;
  const hasGeo = temple.latitude !== null && temple.longitude !== null;

  return (
    <article className="container-reading section-y">
      <Breadcrumb
        items={[{ href: "/temples", label: t("pageTitle") }, { label: temple.name }]}
      />
      {temple.image_url ? (
        /* eslint-disable-next-line @next/next/no-img-element -- CMS image hosts
           are unknown in Sprint 1, so next/image cannot be allowlisted. */
        <img
          src={temple.image_url}
          alt={temple.name}
          className="mb-6 h-56 w-full rounded-md object-cover"
        />
      ) : null}
      <h1>{temple.name}</h1>
      {/* Verified badge renders only when the API says so — never fabricated. */}
      {temple.verified ? (
        <div className="mt-3">
          <StatusBadge label={t("verified")} tone="success" />
        </div>
      ) : null}
      {temple.short_description ? (
        <p className="mt-4 text-lg text-ink-secondary">{temple.short_description}</p>
      ) : null}

      {temple.significance ? (
        <DetailSection title={t("significance")}>
          <p className="whitespace-pre-line">{temple.significance}</p>
        </DetailSection>
      ) : null}

      <DetailSection title={t("timings")}>
        <p>{temple.timings ?? t("timingsUnavailable")}</p>
        {temple.aarti_schedule ? (
          <p className="mt-2">
            <span className="font-semibold">{t("aartiSchedule")}: </span>
            {temple.aarti_schedule}
          </p>
        ) : null}
      </DetailSection>

      <DetailSection title={t("location")}>
        {temple.address ? (
          <p>
            <span className="font-semibold">{t("address")}: </span>
            {temple.address}
          </p>
        ) : null}
        {temple.transport_info ? (
          <p className="mt-2">
            <span className="font-semibold">{t("transport")}: </span>
            {temple.transport_info}
          </p>
        ) : null}
        {hasGeo ? (
          <p className="mt-4">
            <Link
              href={{ pathname: "/map", query: { focus: `temple:${temple.slug}` } }}
              className="btn-outline"
            >
              {t("viewOnMap")}
            </Link>
          </p>
        ) : null}
      </DetailSection>

      {/* Accessibility section always renders, even when sparse (UX §2.3 item 5). */}
      <DetailSection title={t("accessibility")}>
        <p>{temple.accessibility_info ?? t("accessibilityUnavailable")}</p>
      </DetailSection>

      {/* Crowd status is deliberately omitted this sprint — no crowd data source. */}

      <CachedDataFreshness className="mt-8" updatedAt={temple.updated_at} />
    </article>
  );
}
