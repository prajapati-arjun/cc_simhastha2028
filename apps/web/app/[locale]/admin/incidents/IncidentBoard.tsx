"use client";

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { useTranslations } from "next-intl";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { ErrorState } from "@/components/States";
import { authedRequest } from "@/lib/api";
import { readSession } from "@/lib/adminAuth";

/**
 * Admin Incident lifecycle board (PRD section 25).
 *
 * NOTE ON i18n: new during this parallel Phase 3 build, while
 * apps/web/messages/en.json / hi.json are owned by another workstream this
 * sprint. New copy below is plain English rather than useTranslations()
 * calls, so this page does not depend on an edit to a file this workstream
 * cannot touch; existing "admin"/"common" keys are reused via t()/tc()
 * where they already fit. See the final report for the exact "incidents"
 * namespace keys to merge, after which these literals should move there.
 *
 * NOTE ON MOUNTING: the backend router this page calls
 * (app/api/v1/incidents.py) is not yet wired into app/main.py - see the
 * final report / tests/test_incidents.py for why and the exact line to add.
 * This page will 404 against a live API until that line lands.
 */

interface IncidentRow {
  id: number;
  category: string;
  priority: string;
  status: string;
  escalated: boolean;
  title: string;
  description: string | null;
  zone_id: number | null;
  assigned_department: string | null;
  sla_due_at: string | null;
  resolved_at: string | null;
  reported_by_user_id: number | null;
  admin_notes: string | null;
  simulated: boolean;
  created_at: string;
  updated_at: string;
  prototype_notice: string;
}

interface ListEnvelopeLike<T> {
  items: T[];
  total: number;
  last_updated: string | null;
}

const CATEGORIES = ["medical", "security", "fire", "infrastructure", "crowd", "other"];
const PRIORITIES = ["P1", "P2", "P3", "P4"];

//: Mirrors app/services/incident_workflow.py's INCIDENT_TRANSITIONS - a
//: strict linear chain, so each status has at most one "next" move (plus the
//: terminal `closed`).
const STAGES: { status: string; label: string; next: string | null }[] = [
  { status: "reported", label: "Reported", next: "classified" },
  { status: "classified", label: "Classified", next: "assigned" },
  { status: "assigned", label: "Assigned", next: "in_response" },
  { status: "in_response", label: "In response", next: "resolved" },
  { status: "resolved", label: "Resolved", next: "closed" },
  { status: "closed", label: "Closed", next: null },
];

const PRIORITY_STYLES: Record<string, string> = {
  P1: "border-red-200 bg-red-50 text-status-danger",
  P2: "border-amber-200 bg-amber-50 text-amber-700",
  P3: "border-surface-border bg-surface-subtle text-ink-secondary",
  P4: "border-surface-border bg-surface-subtle text-ink-secondary",
};

function slaCountdownLabel(row: IncidentRow, now: number): string {
  if (row.status === "resolved" || row.status === "closed") {
    return "SLA closed out";
  }
  if (!row.sla_due_at) return "No SLA set";
  const dueMs = new Date(row.sla_due_at).getTime();
  const diffMinutes = Math.round((dueMs - now) / 60000);
  if (row.escalated || diffMinutes <= 0) {
    return `SLA breached (${Math.abs(diffMinutes)} min overdue)`;
  }
  return `${diffMinutes} min to SLA`;
}

export function IncidentBoard() {
  const t = useTranslations("admin");
  const tc = useTranslations("common");

  const [rows, setRows] = useState<IncidentRow[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    category: "medical",
    priority: "P3",
    title: "",
    description: "",
    zone_id: "",
    assigned_department: "",
  });
  const [createError, setCreateError] = useState<string | null>(null);

  const load = useCallback(async () => {
    const session = readSession();
    if (!session) return;
    setLoading(true);
    const response = await authedRequest<ListEnvelopeLike<IncidentRow>>(
      "/api/v1/incidents",
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
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  // Recompute SLA countdowns every 30s without a full reload, so a screen
  // left open on a command-center display keeps its urgency readable.
  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 30000);
    return () => clearInterval(interval);
  }, []);

  const columns = useMemo(() => {
    return STAGES.map((stage) => ({
      ...stage,
      items: rows.filter((row) => row.status === stage.status),
    }));
  }, [rows]);

  async function transition(row: IncidentRow, next: string) {
    const session = readSession();
    if (!session) return;
    setBusyId(row.id);
    const response = await authedRequest(`/api/v1/incidents/${row.id}/transition`, session.token, {
      method: "POST",
      body: JSON.stringify({ status: next }),
    });
    setBusyId(null);
    if (response.ok) {
      void load();
    } else {
      setError(response.error);
    }
  }

  async function createIncident(event: FormEvent) {
    event.preventDefault();
    const session = readSession();
    if (!session) return;
    setCreateError(null);
    const response = await authedRequest("/api/v1/incidents", session.token, {
      method: "POST",
      body: JSON.stringify({
        category: form.category,
        priority: form.priority,
        title: form.title,
        description: form.description || null,
        zone_id: form.zone_id ? Number(form.zone_id) : null,
        assigned_department: form.assigned_department || null,
      }),
    });
    if (response.ok) {
      setForm({
        category: "medical",
        priority: "P3",
        title: "",
        description: "",
        zone_id: "",
        assigned_department: "",
      });
      setShowCreate(false);
      void load();
    } else {
      setCreateError(response.error);
    }
  }

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1>Incident management</h1>
        <button type="button" className="btn-primary" onClick={() => setShowCreate((s) => !s)}>
          {showCreate ? tc("cancel") : "Record incident"}
        </button>
      </div>
      <p className="mt-2 text-ink-secondary">
        Demo prototype — every incident here lives in this project&apos;s own test database and
        moves through its lifecycle only by the admin actions below. Nothing is dispatched and no
        police, medical, fire or government system is notified.
      </p>

      <DataFreshnessTimestamp className="mt-2" updatedAt={lastUpdated} />

      {showCreate ? (
        <form onSubmit={createIncident} className="card-surface mt-4 flex flex-col gap-3 p-4">
          {createError ? <ErrorState detail={createError} /> : null}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <label className="flex flex-col gap-1 text-sm">
              Category
              <select
                className="rounded-md border border-surface-border p-2"
                value={form.category}
                onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              Priority
              <select
                className="rounded-md border border-surface-border p-2"
                value={form.priority}
                onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
              >
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label className="flex flex-col gap-1 text-sm">
            Title
            <input
              required
              minLength={3}
              className="rounded-md border border-surface-border p-2"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            Description
            <textarea
              className="rounded-md border border-surface-border p-2"
              rows={2}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
          </label>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <label className="flex flex-col gap-1 text-sm">
              Zone id ({tc("optional")})
              <input
                type="number"
                className="rounded-md border border-surface-border p-2"
                value={form.zone_id}
                onChange={(e) => setForm((f) => ({ ...f, zone_id: e.target.value }))}
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              Assigned department ({tc("optional")})
              <input
                className="rounded-md border border-surface-border p-2"
                value={form.assigned_department}
                onChange={(e) => setForm((f) => ({ ...f, assigned_department: e.target.value }))}
              />
            </label>
          </div>
          <div>
            <button type="submit" className="btn-primary">
              {tc("submit")}
            </button>
          </div>
        </form>
      ) : null}

      {error ? (
        <div className="mt-4">
          <ErrorState detail={error} />
        </div>
      ) : null}

      {loading ? (
        <p className="mt-6" role="status" aria-live="polite">
          {tc("loading")}
        </p>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-6">
          {columns.map((column) => (
            <div key={column.status} className="flex flex-col gap-2">
              <h2 className="text-sm font-semibold text-ink-secondary">
                {column.label} ({column.items.length})
              </h2>
              <div className="flex flex-col gap-2">
                {column.items.length === 0 ? (
                  <p className="text-xs text-ink-secondary">{t("emptyList")}</p>
                ) : (
                  column.items.map((row) => (
                    <div key={row.id} className="card-surface flex flex-col gap-2 p-3 text-sm">
                      <div className="flex items-center justify-between gap-2">
                        <span
                          className={[
                            "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold",
                            PRIORITY_STYLES[row.priority] ?? PRIORITY_STYLES.P3,
                          ].join(" ")}
                        >
                          {row.priority}
                        </span>
                        <span className="text-xs text-ink-secondary">{row.category}</span>
                      </div>
                      <p className="font-medium">{row.title}</p>
                      {row.assigned_department ? (
                        <p className="text-xs text-ink-secondary">
                          Dept: {row.assigned_department}
                        </p>
                      ) : null}
                      <p
                        className={[
                          "text-xs font-semibold",
                          row.escalated ? "text-status-danger" : "text-ink-secondary",
                        ].join(" ")}
                      >
                        {slaCountdownLabel(row, now)}
                      </p>
                      {column.next ? (
                        <button
                          type="button"
                          className="btn-outline text-xs"
                          disabled={busyId === row.id}
                          onClick={() => transition(row, column.next as string)}
                        >
                          Move to {STAGES.find((s) => s.status === column.next)?.label}
                        </button>
                      ) : null}
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default IncidentBoard;
