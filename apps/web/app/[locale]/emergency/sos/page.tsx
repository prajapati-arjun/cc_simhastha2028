import { getTranslations } from "next-intl/server";
import { Breadcrumb } from "@/components/PageShell";
import SafetyBanner from "@/components/SafetyBanner";
import SosForm from "./SosForm";

export const dynamic = "force-dynamic";

export default async function SosPage() {
  const t = await getTranslations("emergency");

  return (
    <>
      {/* Placement rule: sticky, showFormNote — the user must not be able to
          scroll this notice away during the SOS flow. */}
      <SafetyBanner variant="emergency" placement="sticky" showFormNote />
      <div className="container-reading section-y">
        <Breadcrumb
          items={[
            { href: "/emergency", label: t("pageTitle") },
            { label: t("sosPageTitle") },
          ]}
        />
        <h1>{t("sosPageTitle")}</h1>
        <p className="mt-2 text-ink-secondary">{t("callDirect")}</p>
        <SosForm />
      </div>
    </>
  );
}
