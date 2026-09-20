import { useLocale, useTranslations } from "next-intl";
import { formatDateTime } from "@/lib/format";
import type { CommandCenterHumanDecisions } from "./types";

/**
 * Section 3 of the command centre (PRD section 24): human decisions.
 *
 * Every row is a case status an authenticated admin set explicitly (e.g. via
 * the Lost & Found / Missing Person verification queues). Nothing here is
 * inferred or generated - visually distinct from the "recommendations"
 * section above, which is (and must stay) empty.
 */
export function HumanDecisionsSection({
  data,
}: {
  data: CommandCenterHumanDecisions;
}) {
  const t = useTranslations("commandCenter");
  const locale = useLocale();

  return (
    <section
      aria-labelledby="cc-human-decisions-heading"
      data-cc-section="human-decisions"
      className="mt-8 rounded-md border-l-4 border-secondary-500 bg-secondary-50 p-4"
    >
      <h2 id="cc-human-decisions-heading" className="text-xl font-semibold">
        {t("humanDecisions.title")}
      </h2>
      <p className="mt-1 text-sm text-ink-secondary">{data.note}</p>

      {data.recent_status_decisions.length === 0 ? (
        <p className="mt-3 text-sm text-ink-secondary">{t("humanDecisions.empty")}</p>
      ) : (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full min-w-[36rem] border-collapse text-left">
            <caption className="sr-only">{t("humanDecisions.title")}</caption>
            <thead>
              <tr className="border-b border-surface-border">
                <th scope="col" className="py-2 pr-4 text-sm font-semibold">
                  {t("humanDecisions.colType")}
                </th>
                <th scope="col" className="py-2 pr-4 text-sm font-semibold">
                  {t("humanDecisions.colReference")}
                </th>
                <th scope="col" className="py-2 pr-4 text-sm font-semibold">
                  {t("humanDecisions.colStatus")}
                </th>
                <th scope="col" className="py-2 text-sm font-semibold">
                  {t("humanDecisions.colUpdated")}
                </th>
              </tr>
            </thead>
            <tbody>
              {data.recent_status_decisions.map((decision) => (
                <tr
                  key={`${decision.entity_type}-${decision.case_reference}`}
                  className="border-b border-surface-border"
                >
                  <td className="py-2 pr-4 text-sm">
                    {t(`humanDecisions.entity.${decision.entity_type}`)}
                  </td>
                  <td className="py-2 pr-4 text-sm font-mono">
                    {decision.case_reference}
                  </td>
                  <td className="py-2 pr-4 text-sm">{decision.status}</td>
                  <td className="py-2 text-sm text-ink-secondary">
                    {formatDateTime(decision.updated_at, locale)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default HumanDecisionsSection;
