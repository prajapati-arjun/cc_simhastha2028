import { useTranslations } from "next-intl";
import CrowdBandBadge from "@/components/CrowdBandBadge";
import type { CommandCenterObserved } from "./types";

/**
 * Section 1 of the command centre (PRD section 24): observed data only -
 * the latest operator-entered crowd reading per zone, open safety-case
 * totals, and active critical announcements. Everything here is a real row
 * read from this project's own database.
 */
export function ObservedSection({ data }: { data: CommandCenterObserved }) {
  const t = useTranslations("commandCenter");

  return (
    <section
      aria-labelledby="cc-observed-heading"
      data-cc-section="observed"
      className="mt-8 rounded-md border-l-4 border-primary-500 bg-primary-50 p-4"
    >
      <h2 id="cc-observed-heading" className="text-xl font-semibold">
        {t("observed.title")}
      </h2>
      <p className="mt-1 text-sm text-ink-secondary">{t("observed.intro")}</p>

      <h3 className="mt-5 text-sm font-semibold uppercase tracking-wide text-ink-secondary">
        {t("observed.zonesTitle")}
      </h3>
      {data.zones.length === 0 ? (
        <p className="mt-2 text-sm text-ink-secondary">{t("observed.noZones")}</p>
      ) : (
        <div className="mt-2 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.zones.map((zone) => (
            <div key={zone.zone_id} className="card-surface p-4">
              <p className="font-semibold">{zone.zone_name}</p>
              {zone.zone_type ? (
                <p className="text-xs text-ink-secondary">{zone.zone_type}</p>
              ) : null}
              <CrowdBandBadge
                className="mt-3"
                level={zone.latest_crowd_reading?.density_level ?? null}
                recordedAt={zone.latest_crowd_reading?.recorded_at ?? null}
              />
            </div>
          ))}
        </div>
      )}

      <h3 className="mt-6 text-sm font-semibold uppercase tracking-wide text-ink-secondary">
        {t("observed.caseTotalsTitle")}
      </h3>
      <dl className="mt-2 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="card-surface p-4">
          <dt className="text-sm text-ink-secondary">{t("observed.openSos")}</dt>
          <dd className="text-2xl font-semibold">
            {data.case_totals.open_sos_incidents}
          </dd>
        </div>
        <div className="card-surface p-4">
          <dt className="text-sm text-ink-secondary">{t("observed.openLostFound")}</dt>
          <dd className="text-2xl font-semibold">
            {data.case_totals.open_lost_found_cases}
          </dd>
        </div>
        <div className="card-surface p-4">
          <dt className="text-sm text-ink-secondary">
            {t("observed.openMissingPerson")}
          </dt>
          <dd className="text-2xl font-semibold">
            {data.case_totals.open_missing_person_cases}
          </dd>
        </div>
      </dl>
      <p className="mt-2 text-xs text-ink-secondary">{data.case_totals_note}</p>

      <h3 className="mt-6 text-sm font-semibold uppercase tracking-wide text-ink-secondary">
        {t("observed.criticalAlertsTitle")}
      </h3>
      {data.critical_announcements.length === 0 ? (
        <p className="mt-2 text-sm text-ink-secondary">
          {t("observed.noCriticalAlerts")}
        </p>
      ) : (
        <ul className="mt-2 space-y-2">
          {data.critical_announcements.map((alert) => (
            <li
              key={alert.id}
              className="rounded-md border border-red-200 bg-red-50 p-3"
            >
              <p className="font-semibold text-status-danger">{alert.title}</p>
              <p className="mt-1 text-sm text-ink-primary">{alert.body}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default ObservedSection;
