import { useTranslations } from "next-intl";
import type { CommandCenterRecommendations } from "./types";

/**
 * Section 2 of the command centre (PRD section 24): model-generated
 * recommendations. No such engine exists in this prototype, so this section
 * is always empty - it must never be filled in with a simulated suggestion.
 * Visually distinct (dashed border, muted) from the "observed" and
 * "human decisions" sections so nobody mistakes it for either.
 */
export function RecommendationsSection({
  data,
}: {
  data: CommandCenterRecommendations;
}) {
  const t = useTranslations("commandCenter");

  return (
    <section
      aria-labelledby="cc-recommendations-heading"
      data-cc-section="recommendations"
      className="mt-8 rounded-md border-l-4 border-dashed border-ink-secondary bg-surface-subtle p-4"
    >
      <h2 id="cc-recommendations-heading" className="text-xl font-semibold">
        {t("recommendations.title")}
      </h2>
      {data.available && data.items.length > 0 ? (
        <ul className="mt-3 list-disc space-y-1 pl-5 text-ink-primary">
          {data.items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 rounded-md border border-surface-border bg-surface-bg px-3 py-2 text-sm font-medium text-ink-secondary">
          {t("recommendations.notAvailable")}
        </p>
      )}
      <p className="mt-2 text-xs text-ink-secondary">{data.note}</p>
    </section>
  );
}

export default RecommendationsSection;
