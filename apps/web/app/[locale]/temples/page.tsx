import { getTranslations } from "next-intl/server";
import { TempleCard } from "@/components/Card";
import CachedDataFreshness from "@/components/CachedDataFreshness";
import { PageHeading } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import { EmptyState, ErrorState } from "@/components/States";
import { getTemples } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TemplesPage() {
  const t = await getTranslations("temples");
  const result = await getTemples({ limit: 50 });

  return (
    <div className="container-app section-y">
      <PageHeading title={t("pageTitle")} intro={t("pageIntro")} />
      {!result.ok ? (
        <ErrorState detail={result.error} action={<RetryLink />} />
      ) : result.data.items.length === 0 ? (
        <EmptyState message={t("emptyState")} />
      ) : (
        <>
          <CachedDataFreshness updatedAt={result.data.last_updated} />
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
            {result.data.items.map((temple) => (
              <TempleCard key={temple.id} temple={temple} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
