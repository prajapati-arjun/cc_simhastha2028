import { getTranslations } from "next-intl/server";
import { PageHeading } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import { Link } from "@/i18n/navigation";

export const dynamic = "force-dynamic";

/**
 * Offline fallback page (PRD §33). Precached by public/sw.js at install time
 * (both locale variants) and served by the service worker whenever a
 * navigation fails with no cached copy of the requested page available.
 *
 * Intentionally does not attempt to show any app data — offering "not
 * available offline yet" plus a path to the surfaces that ARE cached is more
 * honest than trying to render a shell around missing data.
 */
export default async function OfflinePage() {
  const t = await getTranslations("offline");

  return (
    <div className="container-reading section-y">
      <PageHeading title={t("pageTitle")} intro={t("pageIntro")} />
      <div className="mt-6 flex flex-wrap items-center gap-3">
        <RetryLink />
        <Link href="/emergency" className="btn-outline">
          {t("goEmergency")}
        </Link>
        <Link href="/temples" className="btn-outline">
          {t("goTemples")}
        </Link>
        <Link href="/events" className="btn-outline">
          {t("goEvents")}
        </Link>
      </div>
    </div>
  );
}
