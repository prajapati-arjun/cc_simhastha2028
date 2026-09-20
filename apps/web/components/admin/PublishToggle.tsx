"use client";

import { useTranslations } from "next-intl";
import type { PublicationStatus } from "@/lib/types";

/**
 * PublishToggle — explicit two-state Draft <-> Published control.
 * Saving a record NEVER publishes it silently; publication is always this
 * deliberate action (UX_PAGE_ARCHITECTURE.md §2.9).
 *
 * Sprint 1 ships this single toggle only. The PRD §28 five-stage workflow is
 * explicitly descoped — do not extend this component into one.
 */
export function PublishToggle({
  status,
  onChange,
  disabled,
}: {
  status: PublicationStatus;
  onChange: (next: PublicationStatus) => void;
  disabled?: boolean;
}) {
  const t = useTranslations("admin");
  const published = status === "published";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span
        className={[
          "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
          published
            ? "border-green-200 bg-green-50 text-status-success"
            : "border-surface-border bg-surface-subtle text-ink-secondary",
        ].join(" ")}
      >
        {published ? t("statusPublished") : t("statusDraft")}
      </span>
      <button
        type="button"
        disabled={disabled}
        onClick={() => onChange(published ? "draft" : "published")}
        className="btn-outline text-sm"
      >
        {published ? t("unpublish") : t("publish")}
      </button>
    </div>
  );
}

export default PublishToggle;
