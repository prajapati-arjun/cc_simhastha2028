import { useTranslations } from "next-intl";
import type { ReactNode } from "react";

/**
 * LoadingState / EmptyState / ErrorState — UX_PAGE_ARCHITECTURE.md §3.
 * A failed GET renders ErrorState rather than crashing the route, so the site
 * degrades gracefully whenever the API is unavailable.
 */

export function LoadingState({ rows = 6 }: { rows?: number }) {
  const t = useTranslations("states");
  return (
    <div role="status" aria-live="polite" aria-label={t("loadingLabel")}>
      <span className="sr-only">{t("loadingLabel")}</span>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
        {Array.from({ length: rows }).map((_, index) => (
          <div
            key={index}
            aria-hidden="true"
            className="h-40 animate-pulse rounded-md border border-surface-border bg-surface-subtle"
          />
        ))}
      </div>
    </div>
  );
}

export function EmptyState({
  title,
  message,
  action,
}: {
  title?: string;
  message: string;
  action?: ReactNode;
}) {
  const t = useTranslations("states");
  return (
    <div className="card-surface flex flex-col items-center gap-2 px-6 py-12 text-center">
      <h2 className="text-xl font-semibold">{title ?? t("emptyTitle")}</h2>
      <p className="text-ink-secondary">{message}</p>
      {action}
    </div>
  );
}

export function ErrorState({
  title,
  message,
  detail,
  action,
}: {
  title?: string;
  message?: string;
  detail?: string | null;
  action?: ReactNode;
}) {
  const t = useTranslations("states");
  return (
    <div
      role="alert"
      className="rounded-md border border-red-200 bg-red-50 px-6 py-8 text-center"
    >
      <h2 className="text-xl font-semibold text-status-danger">
        {title ?? t("errorTitle")}
      </h2>
      <p className="mt-2 text-ink-primary">{message ?? t("errorBody")}</p>
      {detail ? (
        <p className="mt-1 text-sm text-ink-secondary">{detail}</p>
      ) : null}
      {action ? <div className="mt-4 flex justify-center">{action}</div> : null}
    </div>
  );
}
