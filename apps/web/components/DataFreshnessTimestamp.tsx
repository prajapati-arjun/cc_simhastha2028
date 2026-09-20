import { useLocale, useTranslations } from "next-intl";
import { formatDateTime } from "@/lib/format";

/**
 * DataFreshnessTimestamp — fed by the contract's list-envelope `last_updated`
 * field (API_CONTRACT.md §0) or a record's `updated_at`. PRD §8 / §33.
 */
export interface DataFreshnessTimestampProps {
  updatedAt: string | null | undefined;
  isCached?: boolean;
  className?: string;
}

export function DataFreshnessTimestamp({
  updatedAt,
  isCached = false,
  className = "",
}: DataFreshnessTimestampProps) {
  const t = useTranslations("common");
  const locale = useLocale();
  const formatted = formatDateTime(updatedAt, locale);

  return (
    <p className={["text-sm text-ink-secondary", className].filter(Boolean).join(" ")}>
      <time dateTime={updatedAt ?? undefined}>
        {formatted ? t("lastUpdated", { date: formatted }) : t("lastUpdatedUnknown")}
      </time>
      {isCached ? " " : null}
    </p>
  );
}

export default DataFreshnessTimestamp;
