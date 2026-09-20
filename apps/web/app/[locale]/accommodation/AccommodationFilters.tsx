import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import type { AccommodationType } from "./accommodationApi";

const ACCOMMODATION_TYPES: AccommodationType[] = [
  "hotel",
  "dharamshala",
  "ashram",
  "tent_camp",
  "government",
];

/**
 * Filter-by-type pills plus a "verified only" toggle. `otherParams` carries
 * the essential-services section's own query params so switching an
 * accommodation filter never clobbers the services section's filter state.
 */
export function AccommodationFilters({
  active,
  verifiedOnly,
  otherParams,
}: {
  active?: AccommodationType;
  verifiedOnly: boolean;
  otherParams: Record<string, string | undefined>;
}) {
  const t = useTranslations("accommodation");

  function query(overrides: Record<string, string | undefined>) {
    return {
      ...otherParams,
      type: active,
      verified: verifiedOnly ? "1" : undefined,
      ...overrides,
    };
  }

  return (
    <nav aria-label={t("filterLabel")} className="mb-4">
      <ul className="flex flex-wrap gap-2">
        <li>
          <Link
            href={{ pathname: "/accommodation", query: query({ type: undefined }) }}
            aria-current={active ? undefined : "true"}
            className={[
              "touch-target rounded-full border px-4 text-sm font-medium",
              active
                ? "border-surface-border bg-surface-bg text-ink-primary"
                : "border-primary-500 bg-primary-500 text-white",
            ].join(" ")}
          >
            {t("filterAll")}
          </Link>
        </li>
        {ACCOMMODATION_TYPES.map((type) => {
          const isActive = type === active;
          return (
            <li key={type}>
              <Link
                href={{ pathname: "/accommodation", query: query({ type }) }}
                aria-current={isActive ? "true" : undefined}
                className={[
                  "touch-target rounded-full border px-4 text-sm font-medium",
                  isActive
                    ? "border-primary-500 bg-primary-500 text-white"
                    : "border-surface-border bg-surface-bg text-ink-primary",
                ].join(" ")}
              >
                {t(`type.${type}`)}
              </Link>
            </li>
          );
        })}
        <li>
          <Link
            href={{
              pathname: "/accommodation",
              query: query({ verified: verifiedOnly ? undefined : "1" }),
            }}
            aria-pressed={verifiedOnly}
            className={[
              "touch-target rounded-full border px-4 text-sm font-medium",
              verifiedOnly
                ? "border-status-success bg-green-50 text-status-success"
                : "border-surface-border bg-surface-bg text-ink-primary",
            ].join(" ")}
          >
            {t("verifiedOnlyToggle")}
          </Link>
        </li>
      </ul>
    </nav>
  );
}

export default AccommodationFilters;
