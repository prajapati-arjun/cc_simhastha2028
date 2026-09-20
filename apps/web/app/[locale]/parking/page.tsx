import { getTranslations } from "next-intl/server";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { PageHeading } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import { EmptyState, ErrorState } from "@/components/States";
import ParkingFilters from "./ParkingFilters";
import ParkingList from "./ParkingList";
import { getParkingList, type ParkingType } from "./parkingApi";

export const dynamic = "force-dynamic";

const PARKING_TYPES: ParkingType[] = ["bus", "two_wheeler", "four_wheeler", "accessible"];

export default async function ParkingPage({
  searchParams,
}: {
  searchParams: { type?: string };
}) {
  const t = await getTranslations("parking");
  const activeType = PARKING_TYPES.includes(searchParams.type as ParkingType)
    ? (searchParams.type as ParkingType)
    : undefined;

  const result = await getParkingList({ parking_type: activeType, limit: 100 });

  return (
    <div className="container-app section-y">
      <PageHeading title={t("pageTitle")} intro={t("pageIntro")} />

      <ParkingFilters active={activeType} />

      {!result.ok ? (
        <ErrorState detail={result.error} action={<RetryLink />} />
      ) : result.data.items.length === 0 ? (
        <EmptyState message={t("emptyState")} />
      ) : (
        <>
          <DataFreshnessTimestamp updatedAt={result.data.last_updated} />
          <ParkingList items={result.data.items} />
        </>
      )}
    </div>
  );
}
