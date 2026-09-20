"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import SafetyBanner from "@/components/SafetyBanner";
import { ErrorState } from "@/components/States";
import { readSession } from "@/lib/adminAuth";
import { authedRequest } from "@/lib/api";
import { HumanDecisionsSection } from "./HumanDecisionsSection";
import { ObservedSection } from "./ObservedSection";
import { RecommendationsSection } from "./RecommendationsSection";
import type { CommandCenterOverview } from "./types";

/**
 * Command Center overview (PRD section 24). Admin-only, read-only.
 *
 * Renders three visually distinct sections - observed data, model-generated
 * recommendations (always empty in this prototype) and human decisions -
 * per this feature's spec. Auth gating is handled by the shared AdminShell
 * (apps/web/app/[locale]/admin/layout.tsx); this page assumes it is only
 * ever rendered for an authenticated admin session.
 *
 * Uses the generic `authedRequest` escape hatch from lib/api.ts rather than
 * a dedicated typed function, because lib/api.ts is being edited
 * concurrently by other agents this sprint. See this feature's owning
 * agent's final report for the exact `getCommandCenterOverview` function to
 * add there during integration.
 */
export default function CommandCenterPage() {
  const t = useTranslations("commandCenter");
  const tc = useTranslations("common");
  const ts = useTranslations("states");

  const [data, setData] = useState<CommandCenterOverview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = readSession();
    if (!session) return;
    let cancelled = false;
    void authedRequest<CommandCenterOverview>(
      "/api/v1/command-center/overview",
      session.token,
    ).then((response) => {
      if (cancelled) return;
      setLoading(false);
      if (response.ok) {
        setData(response.data);
        setError(null);
      } else {
        setError(response.error);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section>
      <h1>{t("title")}</h1>
      <p className="mt-2 max-w-3xl text-ink-secondary">{t("intro")}</p>

      <SafetyBanner
        variant="crowd-placeholder"
        message={data?.prototype_notice}
        className="mt-4"
      />

      {loading ? (
        <p className="mt-6" role="status" aria-live="polite">
          {tc("loading")}
        </p>
      ) : error ? (
        <div className="mt-6">
          <ErrorState title={ts("errorTitle")} detail={error} />
        </div>
      ) : data ? (
        <>
          <DataFreshnessTimestamp className="mt-4" updatedAt={data.generated_at} />
          <ObservedSection data={data.observed} />
          <RecommendationsSection data={data.recommendations} />
          <HumanDecisionsSection data={data.human_decisions} />
        </>
      ) : null}
    </section>
  );
}
