"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { ErrorState } from "@/components/States";
import { ADMIN_ENTITIES, ADMIN_ENTITY_KEYS } from "@/components/admin/adminEntities";
import { Link } from "@/i18n/navigation";
import { authedRequest } from "@/lib/api";
import { readSession } from "@/lib/adminAuth";

type DashboardCounts = Record<string, Record<string, number> | number>;

export default function AdminDashboardPage() {
  const t = useTranslations("admin");
  const tc = useTranslations("common");
  const [counts, setCounts] = useState<DashboardCounts | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = readSession();
    if (!session) return;
    void authedRequest<DashboardCounts>(
      "/api/v1/admin/dashboard",
      session.token,
    ).then((response) => {
      setLoading(false);
      if (response.ok) setCounts(response.data);
      else setError(response.error);
    });
  }, []);

  return (
    <section>
      <h1>{t("dashboard")}</h1>
      <p className="mt-2 text-ink-secondary">{t("dashboardIntro")}</p>

      <ul className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {ADMIN_ENTITY_KEYS.map((key) => (
          <li key={key}>
            <Link
              href={`/admin/${ADMIN_ENTITIES[key].path}`}
              className="card-surface flex min-h-[6rem] flex-col justify-center p-4 font-semibold text-primary-700 hover:shadow-raised"
            >
              {t(ADMIN_ENTITIES[key].labelKey)}
            </Link>
          </li>
        ))}
      </ul>

      <h2 className="mt-8 text-xl font-semibold">{t("counts")}</h2>
      {loading ? (
        <p className="mt-2" role="status" aria-live="polite">
          {tc("loading")}
        </p>
      ) : error ? (
        <div className="mt-2">
          <ErrorState detail={error} />
        </div>
      ) : counts ? (
        <pre className="mt-2 overflow-x-auto rounded-md border border-surface-border bg-surface-subtle p-4 text-sm">
          {JSON.stringify(counts, null, 2)}
        </pre>
      ) : null}
    </section>
  );
}
