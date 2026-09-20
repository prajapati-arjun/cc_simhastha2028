import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import type { EssentialServiceCategory } from "./accommodationApi";

const SERVICE_CATEGORIES: EssentialServiceCategory[] = [
  "food_service",
  "bhandara",
  "drinking_water",
  "toilet",
  "changing_facility",
];

export function ServiceFilters({
  active,
  otherParams,
}: {
  active?: EssentialServiceCategory;
  otherParams: Record<string, string | undefined>;
}) {
  const t = useTranslations("accommodation");

  function query(overrides: Record<string, string | undefined>) {
    return { ...otherParams, service: active, ...overrides };
  }

  return (
    <nav aria-label={t("serviceFilterLabel")} className="mb-4">
      <ul className="flex flex-wrap gap-2">
        <li>
          <Link
            href={{ pathname: "/accommodation", query: query({ service: undefined }) }}
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
        {SERVICE_CATEGORIES.map((category) => {
          const isActive = category === active;
          return (
            <li key={category}>
              <Link
                href={{ pathname: "/accommodation", query: query({ service: category }) }}
                aria-current={isActive ? "true" : undefined}
                className={[
                  "touch-target rounded-full border px-4 text-sm font-medium",
                  isActive
                    ? "border-primary-500 bg-primary-500 text-white"
                    : "border-surface-border bg-surface-bg text-ink-primary",
                ].join(" ")}
              >
                {t(`serviceCategory.${category}`)}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export default ServiceFilters;
