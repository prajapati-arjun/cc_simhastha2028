import { getTranslations } from "next-intl/server";
import { PageHeading } from "@/components/PageShell";
import PlannerForm from "./PlannerForm";

export const dynamic = "force-dynamic";

export default async function PlannerPage() {
  const t = await getTranslations("planner");
  return (
    <div className="container-reading section-y">
      <PageHeading title={t("pageTitle")} intro={t("pageIntro")} />
      <PlannerForm />
    </div>
  );
}
