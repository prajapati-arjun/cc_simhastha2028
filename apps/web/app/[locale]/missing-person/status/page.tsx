import { getTranslations } from "next-intl/server";
import { PageHeading } from "@/components/PageShell";
import SafetyBanner from "@/components/SafetyBanner";
import MissingPersonLookup from "./MissingPersonLookup";

export const dynamic = "force-dynamic";

export default async function MissingPersonStatusPage() {
  const t = await getTranslations("missingPerson");
  return (
    <div className="container-reading section-y">
      <PageHeading title={t("statusTitle")} />
      {/* Placement rule: inline, top of page. */}
      <SafetyBanner variant="missing-person" />
      <p className="mt-4 text-ink-secondary">{t("noSearchNotice")}</p>
      <MissingPersonLookup />
    </div>
  );
}
