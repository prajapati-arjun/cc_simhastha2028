import { getTranslations } from "next-intl/server";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { PageHeading } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import { EmptyState, ErrorState } from "@/components/States";
import AccommodationFilters from "./AccommodationFilters";
import AccommodationList from "./AccommodationList";
import ServiceFilters from "./ServiceFilters";
import ServiceList from "./ServiceList";
import {
  getAccommodationList,
  getEssentialServiceList,
  type AccommodationType,
  type EssentialServiceCategory,
} from "./accommodationApi";

export const dynamic = "force-dynamic";

const ACCOMMODATION_TYPES: AccommodationType[] = [
  "hotel",
  "dharamshala",
  "ashram",
  "tent_camp",
  "government",
];
const SERVICE_CATEGORIES: EssentialServiceCategory[] = [
  "food_service",
  "bhandara",
  "drinking_water",
  "toilet",
  "changing_facility",
];

export default async function AccommodationPage({
  searchParams,
}: {
  searchParams: { type?: string; verified?: string; service?: string };
}) {
  const t = await getTranslations("accommodation");

  const activeType = ACCOMMODATION_TYPES.includes(searchParams.type as AccommodationType)
    ? (searchParams.type as AccommodationType)
    : undefined;
  const verifiedOnly = searchParams.verified === "1";
  const activeService = SERVICE_CATEGORIES.includes(
    searchParams.service as EssentialServiceCategory,
  )
    ? (searchParams.service as EssentialServiceCategory)
    : undefined;

  const [accommodationResult, serviceResult] = await Promise.all([
    getAccommodationList({
      accommodation_type: activeType,
      verified: verifiedOnly,
      limit: 100,
    }),
    getEssentialServiceList({ category: activeService, limit: 100 }),
  ]);

  return (
    <div className="container-app section-y">
      <PageHeading title={t("pageTitle")} intro={t("pageIntro")} />

      <section>
        <h2 className="text-xl font-semibold md:text-2xl">{t("accommodationSectionTitle")}</h2>
        <AccommodationFilters
          active={activeType}
          verifiedOnly={verifiedOnly}
          otherParams={{ service: searchParams.service }}
        />
        {!accommodationResult.ok ? (
          <ErrorState detail={accommodationResult.error} action={<RetryLink />} />
        ) : accommodationResult.data.items.length === 0 ? (
          <EmptyState message={t("emptyState")} />
        ) : (
          <>
            <DataFreshnessTimestamp updatedAt={accommodationResult.data.last_updated} />
            <AccommodationList items={accommodationResult.data.items} />
          </>
        )}
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold md:text-2xl">{t("servicesSectionTitle")}</h2>
        <ServiceFilters
          active={activeService}
          otherParams={{ type: searchParams.type, verified: searchParams.verified }}
        />
        {!serviceResult.ok ? (
          <ErrorState detail={serviceResult.error} action={<RetryLink />} />
        ) : serviceResult.data.items.length === 0 ? (
          <EmptyState message={t("servicesEmptyState")} />
        ) : (
          <>
            <DataFreshnessTimestamp updatedAt={serviceResult.data.last_updated} />
            <ServiceList items={serviceResult.data.items} />
          </>
        )}
      </section>
    </div>
  );
}
