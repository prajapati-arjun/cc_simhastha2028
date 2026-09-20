import { useTranslations } from "next-intl";
import { CardBase } from "@/components/Card";
import StatusBadge from "@/components/StatusBadge";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import type { ParkingFacility } from "./parkingApi";

/**
 * ParkingCard - co-located with the parking feature rather than added to the
 * shared `components/Card.tsx` (protected-adjacent: three other agents are
 * editing shared components concurrently this sprint). Reuses `CardBase` /
 * `StatusBadge` by import only, so no shared file needs editing.
 */
export function ParkingCard({ facility }: { facility: ParkingFacility }) {
  const t = useTranslations("parking");

  const hasCount = facility.current_occupancy !== null && facility.capacity !== null;
  const full =
    hasCount && (facility.current_occupancy as number) >= (facility.capacity as number);

  return (
    <CardBase
      title={facility.name}
      badge={<StatusBadge label={t(`type.${facility.parking_type}`)} tone="info" />}
    >
      <p className="text-sm text-ink-primary">
        {facility.capacity !== null
          ? t("capacity", { count: facility.capacity })
          : t("capacityUnknown")}
      </p>

      <p className="text-sm font-medium text-ink-primary">
        {facility.current_occupancy !== null
          ? t("occupancy", { count: facility.current_occupancy })
          : t("occupancyUnknown")}
        {full ? (
          <StatusBadge className="ml-2" label={t("full")} tone="warning" />
        ) : null}
      </p>
      {/* Occupancy is operator-entered, never a live sensor/camera feed. */}
      <p className="text-xs text-ink-muted">{t("occupancyNotice")}</p>
      <DataFreshnessTimestamp updatedAt={facility.occupancy_updated_at} />

      {facility.entry_info ? (
        <p className="text-sm text-ink-secondary">
          {t("entry")}: {facility.entry_info}
        </p>
      ) : null}
      {facility.exit_info ? (
        <p className="text-sm text-ink-secondary">
          {t("exit")}: {facility.exit_info}
        </p>
      ) : null}
      {facility.shuttle_note ? (
        <p className="text-sm text-ink-secondary">
          {t("shuttle")}: {facility.shuttle_note}
        </p>
      ) : null}
    </CardBase>
  );
}

export default ParkingCard;
