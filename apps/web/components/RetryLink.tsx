"use client";

import { useTranslations } from "next-intl";

/**
 * Retry control for failed GETs. Deliberately not offered on POST confirmation
 * screens (UX_PAGE_ARCHITECTURE.md §3) — re-posting a safety report is harmful.
 */
export function RetryLink() {
  const t = useTranslations("common");
  return (
    <button
      type="button"
      className="btn-outline"
      onClick={() => window.location.reload()}
    >
      {t("retry")}
    </button>
  );
}

export default RetryLink;
