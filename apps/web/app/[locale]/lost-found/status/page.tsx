import { getTranslations } from "next-intl/server";
import { PageHeading } from "@/components/PageShell";
import SafetyBanner from "@/components/SafetyBanner";
import LostFoundLookup from "./LostFoundLookup";

export const dynamic = "force-dynamic";

export default async function LostFoundStatusPage() {
  const t = await getTranslations("lostFound");
  return (
    <div className="container-reading section-y">
      <PageHeading title={t("statusTitle")} />
      {/* Placement rule: inline, top of page. */}
      <SafetyBanner variant="lost-found" />
      <p className="mt-4 text-ink-secondary">{t("noSearchNotice")}</p>
      <LostFoundLookup />
    </div>
  );
}
