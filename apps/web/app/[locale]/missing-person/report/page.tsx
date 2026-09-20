import { getTranslations } from "next-intl/server";
import { PageHeading } from "@/components/PageShell";
import SafetyBanner from "@/components/SafetyBanner";
import MissingPersonForm from "./MissingPersonForm";

export const dynamic = "force-dynamic";

export default async function MissingPersonReportPage() {
  const t = await getTranslations("missingPerson");
  return (
    <div className="container-reading section-y">
      <PageHeading title={t("pageTitle")} />
      {/* Placement rule: inline, top of form, showFormNote. */}
      <SafetyBanner variant="missing-person" showFormNote />
      <p className="mt-4 rounded-md border border-surface-border bg-surface-subtle p-4 text-sm font-medium">
        {t("policeNote")}
      </p>
      <MissingPersonForm />
    </div>
  );
}
