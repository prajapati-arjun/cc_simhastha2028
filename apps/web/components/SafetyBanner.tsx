import { useTranslations } from "next-intl";

/**
 * SafetyBanner — Docs/UX_DESIGN_SYSTEM.md §3.
 *
 * Tells every user, on every safety-critical screen, that emergency /
 * missing-person / lost-found / crowd data is simulated and NOT connected to
 * real dispatch or authorities.
 *
 * Hard rules from the spec, encoded here so they cannot be bypassed:
 *  - NOT dismissible. There is deliberately no close button and no prop to add one.
 *  - Never rendered with a `status.danger` red background (red is reserved for
 *    density.critical and real error states).
 *  - Default copy per variant is fixed; `message` overrides only for screens
 *    that need extra context on top of, not instead of, the safety meaning.
 */

export type SafetyBannerVariant =
  | "emergency"
  | "missing-person"
  | "lost-found"
  | "crowd-placeholder";

export interface SafetyBannerProps {
  variant: SafetyBannerVariant;
  /** Optional override of the default per-variant copy. */
  message?: string;
  /** 'sticky' pins it under the site header — SOS flow only. */
  placement?: "inline" | "sticky";
  /** Adds the POST-form addendum above a submit button. */
  showFormNote?: boolean;
  className?: string;
}

const MESSAGE_KEY: Record<SafetyBannerVariant, string> = {
  emergency: "emergency",
  "missing-person": "missingPerson",
  "lost-found": "lostFound",
  "crowd-placeholder": "crowdPlaceholder",
};

export function SafetyBanner({
  variant,
  message,
  placement = "inline",
  showFormNote = false,
  className = "",
}: SafetyBannerProps) {
  const t = useTranslations("safetyBanner");
  const sticky = placement === "sticky";

  return (
    <aside
      role="note"
      aria-label={t("label")}
      data-safety-banner={variant}
      className={[
        "w-full border-l-4 border-secondary-500 bg-secondary-50 px-4 py-3",
        sticky
          ? "sticky top-0 z-40 rounded-none shadow-card md:top-[var(--header-height)]"
          : "rounded-md",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="flex items-start gap-3">
        <svg
          aria-hidden="true"
          focusable="false"
          viewBox="0 0 24 24"
          className="mt-0.5 h-5 w-5 flex-shrink-0 fill-current text-secondary-600"
        >
          <path d="M12 2 1 21h22L12 2Zm0 5.5 7.1 12.3H4.9L12 7.5ZM11 11v5h2v-5h-2Zm0 6v2h2v-2h-2Z" />
        </svg>
        <div className="min-w-0">
          <p className="text-sm font-medium text-ink-primary">
            {message ?? t(MESSAGE_KEY[variant])}
          </p>
          {showFormNote ? (
            <p className="mt-1 text-xs text-ink-secondary">{t("formNote")}</p>
          ) : null}
        </div>
      </div>
    </aside>
  );
}

export default SafetyBanner;
