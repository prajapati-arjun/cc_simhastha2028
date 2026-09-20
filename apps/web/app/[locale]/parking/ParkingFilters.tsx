import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import type { ParkingType } from "./parkingApi";

const PARKING_TYPES: ParkingType[] = ["bus", "two_wheeler", "four_wheeler", "accessible"];

/** Filter-by-type pill nav, mirroring the pattern in app/[locale]/events/page.tsx. */
export function ParkingFilters({ active }: { active?: ParkingType }) {
  const t = useTranslations("parking");

  return (
    <nav aria-label={t("filterLabel")} className="mb-6">
      <ul className="flex flex-wrap gap-2">
        <li>
          <Link
            href="/parking"
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
        {PARKING_TYPES.map((type) => {
          const isActive = type === active;
          return (
            <li key={type}>
              <Link
                href={{ pathname: "/parking", query: { type } }}
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
      </ul>
    </nav>
  );
}

export default ParkingFilters;
