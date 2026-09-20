import { useTranslations } from "next-intl";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";

/**
 * CrowdBandBadge — PRD section 10/26.
 *
 * Renders an aggregate zone-level crowd density band (green/yellow/orange/
 * red) only. There is deliberately no prop for a headcount or a per-person
 * figure - PRD section 26 requires no biometrics and no facial recognition,
 * ever, and PRD section 10 does not require individual-level tracking for
 * basic crowd density.
 *
 * `level` is intentionally typed as `CrowdBandLevel | null | undefined` so a
 * zone with no operator-entered reading yet renders the "not available"
 * state below rather than a caller defaulting it to a fabricated colour -
 * matching the existing `crowdLevelUnavailable` convention used by
 * GhatStatusOut (Docs/API_CONTRACT.md section 3).
 *
 * Contract note: this component's TypeScript types are declared locally
 * because apps/web/lib/types.ts is being edited concurrently by another
 * agent this sprint. See this component's owning agent's final report for
 * the exact CrowdZone / CrowdReading types to add there during integration.
 */

export type CrowdBandLevel = "green" | "yellow" | "orange" | "red";

export interface CrowdBandBadgeProps {
  level: CrowdBandLevel | null | undefined;
  /** Pass the reading's `recorded_at` (or omit entirely to hide the freshness line). */
  recordedAt?: string | null;
  className?: string;
}

const LEVEL_STYLES: Record<CrowdBandLevel, string> = {
  green: "border-green-300 bg-green-50 text-green-800",
  yellow: "border-yellow-300 bg-yellow-50 text-yellow-800",
  orange: "border-orange-300 bg-orange-50 text-orange-800",
  red: "border-red-300 bg-red-50 text-red-800",
};

export function CrowdBandBadge({
  level,
  recordedAt,
  className = "",
}: CrowdBandBadgeProps) {
  const t = useTranslations("crowd");

  return (
    <div className={className}>
      {level ? (
        <span
          data-crowd-band={level}
          className={[
            "inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium",
            LEVEL_STYLES[level],
          ].join(" ")}
        >
          {t(`level.${level}`)}
        </span>
      ) : (
        <span className="inline-flex items-center rounded-full border border-surface-border bg-surface-subtle px-3 py-1 text-sm font-medium text-ink-secondary">
          {t("levelUnavailable")}
        </span>
      )}
      {recordedAt !== undefined ? (
        <DataFreshnessTimestamp className="mt-1" updatedAt={recordedAt} />
      ) : null}
    </div>
  );
}

export default CrowdBandBadge;
