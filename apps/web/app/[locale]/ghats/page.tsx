import { getTranslations } from "next-intl/server";
import { GhatCard } from "@/components/Card";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { PageHeading } from "@/components/PageShell";
import RetryLink from "@/components/RetryLink";
import { EmptyState, ErrorState } from "@/components/States";
import { getGhatStatus, getGhats } from "@/lib/api";
import type { GhatStatus } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function GhatsPage() {
  const t = await getTranslations("ghats");
  const result = await getGhats({ limit: 50 });

  // Status comes from the separate per-ghat endpoint (contract §3). A failed
  // status call degrades that one card, it does not fail the directory.
  let statuses: Record<number, GhatStatus | null> = {};
  if (result.ok) {
    const entries = await Promise.all(
      result.data.items.map(async (ghat) => {
        const status = await getGhatStatus(ghat.slug);
        return [ghat.id, status.ok ? status.data : null] as const;
      }),
    );
    statuses = Object.fromEntries(entries);
  }

  return (
    <div className="container-app section-y">
      <PageHeading title={t("pageTitle")} intro={t("pageIntro")} />
      {!result.ok ? (
        <ErrorState detail={result.error} action={<RetryLink />} />
      ) : result.data.items.length === 0 ? (
        <EmptyState message={t("emptyState")} />
      ) : (
        <>
          <DataFreshnessTimestamp updatedAt={result.data.last_updated} />
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
            {result.data.items.map((ghat) => (
              <GhatCard key={ghat.id} ghat={ghat} status={statuses[ghat.id] ?? null} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
