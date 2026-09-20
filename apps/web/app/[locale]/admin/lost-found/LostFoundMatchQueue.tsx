"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import DataFreshnessTimestamp from "@/components/DataFreshnessTimestamp";
import { ErrorState } from "@/components/States";
import { authedRequest } from "@/lib/api";
import { readSession } from "@/lib/adminAuth";

/**
 * Admin Lost & Found review queue with a "potential matches" panel
 * (PRD section 16).
 *
 * NOTE ON i18n: this component is new during a parallel Phase 3 build in
 * which apps/web/messages/en.json and hi.json are owned by another
 * workstream this sprint. Copy below is plain English rather than
 * useTranslations() calls for the new strings so this page does not depend
 * on an edit to a file this workstream cannot touch; existing keys already
 * present in the "admin" and "common" namespaces (loading, delete confirm,
 * status labels, etc.) are reused via t()/tc() where they fit. See the
 * final report for the exact en.json/hi.json keys to merge, after which
 * these literals should move to the "incidents" or a new "lostFoundAdmin"
 * namespace.
 *
 * NOTE ON MATCHING: status can only reach "matched" through the explicit
 * confirm-match action below, never through a bare status button - see PRD
 * scope decision: no algorithmic candidate ever auto-links or auto-closes a
 * case. "matched" is deliberately absent from STATUS_ACTIONS.
 */

interface LostFoundAdminRow {
  id: number;
  case_reference: string;
  report_type: string;
  category: string;
  description: string;
  location_text: string | null;
  occurred_at: string | null;
  image_url: string | null;
  reporter_name: string | null;
  reporter_phone: string;
  status: string;
  admin_notes: string | null;
  matched_case_id: number | null;
  created_at: string;
  updated_at: string;
}

interface CandidateMatch {
  id: number;
  case_reference: string;
  report_type: string;
  category: string;
  status: string;
  score: number;
  reasons: string[];
  created_at: string;
}

interface ListEnvelopeLike<T> {
  items: T[];
  total: number;
  last_updated: string | null;
}

//: Mirrors app/services/workflow.py's LOST_FOUND_TRANSITIONS, minus
//: "matched" - that move only ever happens via confirm-match below.
const STATUS_ACTIONS: Record<string, string[]> = {
  submitted: ["under_review", "rejected"],
  under_review: ["verified", "rejected"],
  verified: ["closed"],
  matched: ["closed"],
  closed: [],
  rejected: [],
};

const STATUS_LABELS: Record<string, string> = {
  submitted: "Submitted",
  under_review: "Under review",
  verified: "Verified",
  matched: "Matched",
  closed: "Closed",
  rejected: "Rejected",
};

export function LostFoundMatchQueue() {
  const t = useTranslations("admin");
  const tc = useTranslations("common");

  const [rows, setRows] = useState<LostFoundAdminRow[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [notesDraft, setNotesDraft] = useState<Record<number, string>>({});
  const [candidatesByCase, setCandidatesByCase] = useState<
    Record<number, CandidateMatch[] | "loading" | string>
  >({});

  const load = useCallback(async () => {
    const session = readSession();
    if (!session) return;
    setLoading(true);
    const response = await authedRequest<ListEnvelopeLike<LostFoundAdminRow>>(
      "/api/v1/admin/lost-found",
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

  async function changeStatus(row: LostFoundAdminRow, next: string) {
    const session = readSession();
    if (!session) return;
    setBusyId(row.id);
    const response = await authedRequest(`/api/v1/admin/lost-found/${row.id}`, session.token, {
      method: "PATCH",
      body: JSON.stringify({ status: next }),
    });
    setBusyId(null);
    if (response.ok) {
      void load();
    } else {
      setError(response.error);
    }
  }

  async function saveNotes(row: LostFoundAdminRow) {
    const session = readSession();
    if (!session) return;
    const notes = notesDraft[row.id] ?? row.admin_notes ?? "";
    setBusyId(row.id);
    const response = await authedRequest(`/api/v1/admin/lost-found/${row.id}`, session.token, {
      method: "PATCH",
      body: JSON.stringify({ status: row.status, admin_notes: notes }),
    });
    setBusyId(null);
    if (response.ok) {
      void load();
    } else {
      setError(response.error);
    }
  }

  async function loadCandidates(row: LostFoundAdminRow) {
    const session = readSession();
    if (!session) return;
    setCandidatesByCase((prev) => ({ ...prev, [row.id]: "loading" }));
    const response = await authedRequest<CandidateMatch[]>(
      `/api/v1/lost-found/${row.id}/candidate-matches`,
      session.token,
    );
    setCandidatesByCase((prev) => ({
      ...prev,
      [row.id]: response.ok ? response.data : response.error,
    }));
  }

  async function confirmMatch(row: LostFoundAdminRow, candidate: CandidateMatch) {
    const session = readSession();
    if (!session) return;
    if (
      !window.confirm(
        `Confirm that "${row.case_reference}" and "${candidate.case_reference}" are the ` +
          "same item? Both cases will move to Matched. This cannot be undone automatically.",
      )
    ) {
      return;
    }
    setBusyId(row.id);
    const response = await authedRequest(
      `/api/v1/lost-found/${row.id}/confirm-match`,
      session.token,
      { method: "POST", body: JSON.stringify({ matched_case_id: candidate.id }) },
    );
    setBusyId(null);
    if (response.ok) {
      setCandidatesByCase((prev) => {
        const { [row.id]: _removed, ...rest } = prev;
        return rest;
      });
      void load();
    } else {
      setError(response.error);
    }
  }

  return (
    <section>
      <h1>Lost &amp; Found review queue</h1>
      <p className="mt-2 text-ink-secondary">
        Demo prototype — every case here lives in this project&apos;s own test database.
        Matching two cases always requires the explicit &quot;Confirm match&quot; action below;
        nothing is linked or closed automatically by the candidate scorer.
      </p>

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
      ) : rows.length === 0 ? (
        <p className="mt-6 text-ink-secondary">{t("emptyList")}</p>
      ) : (
        <ul className="mt-6 flex flex-col gap-4">
          {rows.map((row) => {
            const expanded = expandedId === row.id;
            const candidates = candidatesByCase[row.id];
            return (
              <li key={row.id} className="card-surface p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold">
                      {row.case_reference}{" "}
                      <span className="text-ink-secondary">
                        ({row.report_type} · {row.category})
                      </span>
                    </p>
                    <p className="text-sm text-ink-secondary">
                      {STATUS_LABELS[row.status] ?? row.status}
                      {row.matched_case_id ? ` · matched with case #${row.matched_case_id}` : ""}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(STATUS_ACTIONS[row.status] ?? []).map((next) => (
                      <button
                        key={next}
                        type="button"
                        className="btn-outline text-sm"
                        disabled={busyId === row.id}
                        onClick={() => changeStatus(row, next)}
                      >
                        Move to {STATUS_LABELS[next] ?? next}
                      </button>
                    ))}
                    <button
                      type="button"
                      className="btn-outline text-sm"
                      onClick={() => setExpandedId(expanded ? null : row.id)}
                    >
                      {expanded ? "Hide detail" : "Show detail"}
                    </button>
                  </div>
                </div>

                {expanded ? (
                  <div className="mt-4 flex flex-col gap-4 border-t border-surface-border pt-4">
                    <div>
                      <p className="text-sm font-semibold">Description</p>
                      <p className="text-sm text-ink-secondary">{row.description}</p>
                      {row.location_text ? (
                        <p className="mt-1 text-sm text-ink-secondary">
                          Location: {row.location_text}
                        </p>
                      ) : null}
                      <p className="mt-1 text-sm text-ink-secondary">
                        Reporter: {row.reporter_name ?? "(not given)"} · {row.reporter_phone}
                      </p>
                    </div>

                    <div>
                      <label htmlFor={`notes-${row.id}`} className="text-sm font-semibold">
                        Reviewer notes
                      </label>
                      <textarea
                        id={`notes-${row.id}`}
                        className="mt-1 w-full rounded-md border border-surface-border p-2 text-sm"
                        rows={2}
                        value={notesDraft[row.id] ?? row.admin_notes ?? ""}
                        onChange={(event) =>
                          setNotesDraft((prev) => ({ ...prev, [row.id]: event.target.value }))
                        }
                      />
                      <button
                        type="button"
                        className="btn-outline mt-2 text-sm"
                        disabled={busyId === row.id}
                        onClick={() => saveNotes(row)}
                      >
                        {tc("save")}
                      </button>
                    </div>

                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-sm font-semibold">Potential matches</p>
                        <button
                          type="button"
                          className="btn-outline text-sm"
                          onClick={() => loadCandidates(row)}
                        >
                          Find potential matches
                        </button>
                      </div>
                      <p className="mt-1 text-xs text-ink-secondary">
                        Heuristic ranking only (category, description keywords, date/location
                        proximity) — not AI/ML. Always review before confirming.
                      </p>

                      {candidates === "loading" ? (
                        <p className="mt-2 text-sm" role="status" aria-live="polite">
                          {tc("loading")}
                        </p>
                      ) : typeof candidates === "string" ? (
                        <p className="mt-2 text-sm text-status-danger">{candidates}</p>
                      ) : Array.isArray(candidates) ? (
                        candidates.length === 0 ? (
                          <p className="mt-2 text-sm text-ink-secondary">
                            No candidate matches found.
                          </p>
                        ) : (
                          <ul className="mt-2 flex flex-col gap-2">
                            {candidates.map((candidate) => (
                              <li
                                key={candidate.id}
                                className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-surface-border p-2"
                              >
                                <div>
                                  <p className="text-sm font-medium">
                                    {candidate.case_reference}{" "}
                                    <span className="text-ink-secondary">
                                      (score {candidate.score.toFixed(1)})
                                    </span>
                                  </p>
                                  <p className="text-xs text-ink-secondary">
                                    {candidate.reasons.join("; ")}
                                  </p>
                                </div>
                                <button
                                  type="button"
                                  className="btn-primary text-sm"
                                  disabled={busyId === row.id}
                                  onClick={() => confirmMatch(row, candidate)}
                                >
                                  Confirm match
                                </button>
                              </li>
                            ))}
                          </ul>
                        )
                      ) : null}
                    </div>
                  </div>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

export default LostFoundMatchQueue;
