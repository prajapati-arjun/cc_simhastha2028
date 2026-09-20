import { getTranslations } from "next-intl/server";
import { PageHeading } from "@/components/PageShell";
import SafetyBanner from "@/components/SafetyBanner";
import LostFoundForm from "./LostFoundForm";

export const dynamic = "force-dynamic";

export default async function LostFoundReportPage() {
  const t = await getTranslations("lostFound");
  return (
    <div className="container-reading section-y">
      <PageHeading title={t("reportTitle")} />
      {/* Placement rule: inline, top of form, showFormNote. */}
      <SafetyBanner variant="lost-found" showFormNote />
      <LostFoundForm />
    </div>
  );
}
