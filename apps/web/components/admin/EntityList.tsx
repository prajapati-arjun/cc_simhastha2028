"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { ErrorState } from "@/components/States";
import { Link } from "@/i18n/navigation";
import { authedRequest } from "@/lib/api";
import { readSession } from "@/lib/adminAuth";
import type { AdminEntityKey, ListEnvelope, PublicationStatus } from "@/lib/types";
import { ADMIN_ENTITIES } from "./adminEntities";
import PublishToggle from "./PublishToggle";

type Row = Record<string, unknown> & {
  id: number;
  status: PublicationStatus;
  updated_at: string;
};

export function EntityList({ entityKey }: { entityKey: AdminEntityKey }) {
  const config = ADMIN_ENTITIES[entityKey];
  const t = useTranslations("admin");
  const tc = useTranslations("common");

  const [rows, setRows] = useState<Row[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(async () => {
    const session = readSession();
    if (!session) return;
    setLoading(true);
    const response = await authedRequest<ListEnvelope<Row>>(
      `/api/v1/admin/${config.path}`,
      session.token,
    );
    setLoading(false);
    if (response.ok) {
      setRows(response.data.items);
      setLastUpdated(response.data.last_updated);
      setError(null);
    } else {
      setError(response.error);
    }
  }, [config.path]);

  useEffect(() => {
    void load();
  }, [load]);

  async function changeStatus(row: Row, next: PublicationStatus) {
    const session = readSession();
    if (!session) return;
    setBusyId(row.id);
    const response = await authedRequest(
      `/api/v1/admin/${config.path}/${row.id}`,
      session.token,
      { method: "PATCH", body: JSON.stringify({ status: next }) },
    );
    setBusyId(null);
    if (response.ok) {
      void load();
    } else {
      setError(response.error);
    }
  }

  async function remove(row: Row) {
    if (!window.confirm(t("deleteConfirm"))) return;
    const session = readSession();
    if (!session) return;
    setBusyId(row.id);
    const response = await authedRequest(
      `/api/v1/admin/${config.path}/${row.id}`,
      session.token,
      { method: "DELETE" },
    );
    setBusyId(null);
    if (response.ok) {
      void load();
    } else {
      setError(response.error);
    }
  }

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1>{t(config.labelKey)}</h1>
        <Link href={`/admin/${config.path}/new`} className="btn-primary">
          {t("createNew")}
        </Link>
      </div>

      <DataFreshnessTimestamp className="mt-2" updatedAt={lastUpdated} />

      {error ? (
        <div className="mt-4">
          <ErrorState detail={error} />
        </div>
      ) : null}

      {loading ? (
        <p className="mt-6" role="status" aria-live="polite">
          {tc("loading")}
        </p>
      ) : rows.length === 0 && !error ? (
        <p className="mt-6 text-ink-secondary">{t("emptyList")}</p>
      ) : (
        <div className="mt-6 overflow-x-auto">
          <table className="w-full min-w-[40rem] border-collapse text-left">
            <caption className="sr-only">{t(config.labelKey)}</caption>
            <thead>
              <tr className="border-b border-surface-border">
                <th scope="col" className="py-2 pr-4 text-sm font-semibold">
                  {t("colTitle")}
                </th>
                <th scope="col" className="py-2 pr-4 text-sm font-semibold">
                  {t("colStatus")}
                </th>
                <th scope="col" className="py-2 pr-4 text-sm font-semibold">
                  {t("colUpdated")}
                </th>
                <th scope="col" className="py-2 text-sm font-semibold">
                  {t("colActions")}
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-b border-surface-border align-top">
                  <th scope="row" className="py-3 pr-4 font-medium">
                    {String(row[config.titleField] ?? row.id)}
                  </th>
                  <td className="py-3 pr-4">
                    <PublishToggle
                      status={row.status}
                      disabled={busyId === row.id}
                      onChange={(next) => changeStatus(row, next)}
                    />
                  </td>
                  <td className="py-3 pr-4 text-sm text-ink-secondary">
                    {row.updated_at}
                  </td>
                  <td className="py-3">
                    <div className="flex flex-wrap gap-2">
                      <Link
                        href={`/admin/${config.path}/${row.id}/edit`}
                        className="btn-outline text-sm"
                      >
                        {t("edit")}
                      </Link>
                      <button
                        type="button"
                        className="btn-outline text-sm text-status-danger"
                        disabled={busyId === row.id}
                        onClick={() => remove(row)}
                      >
                        {tc("delete")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default EntityList;
