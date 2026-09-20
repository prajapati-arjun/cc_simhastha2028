import type {
  Announcement,
  CaseSubmissionResponse,
  EmergencyService,
  EventItem,
  Ghat,
  GhatStatus,
  ListEnvelope,
  LostFoundCase,
  LostFoundRequest,
  MissingPersonCase,
  MissingPersonRequest,
  SosRequest,
  SosResponse,
  Temple,
} from "./types";

/**
 * Typed client for the frozen Sprint 1 API contract (Docs/API_CONTRACT.md).
 *
 * Every read returns an ApiResult rather than throwing, so a page renders an
 * ErrorState instead of collapsing to a white screen when the API is down.
 */

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; status: number | null; error: string };

const DEFAULT_TIMEOUT_MS = 8000;

/**
 * Server components inside docker talk to the API service by its compose name;
 * the browser talks to the published host port. API_INTERNAL_URL is optional —
 * NEXT_PUBLIC_API_URL alone is enough for host-side `npm run dev`.
 */
export function apiBaseUrl(): string {
  const serverSide = typeof window === "undefined";
  const base = serverSide
    ? process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL
    : process.env.NEXT_PUBLIC_API_URL;
  return (base || "http://localhost:8000").replace(/\/+$/, "");
}

function buildUrl(path: string, params?: Record<string, string | number | undefined>) {
  const url = new URL(apiBaseUrl() + path);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function request<T>(
  path: string,
  init: RequestInit & { params?: Record<string, string | number | undefined> } = {},
): Promise<ApiResult<T>> {
  const { params, ...rest } = init;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  try {
    const response = await fetch(buildUrl(path, params), {
      ...rest,
      signal: controller.signal,
      // Safety, status and freshness data must never be served from a stale cache.
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...(rest.body ? { "Content-Type": "application/json" } : {}),
        ...(rest.headers || {}),
      },
    });

    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const body = (await response.json()) as { detail?: unknown };
        if (typeof body?.detail === "string") {
          detail = body.detail;
        } else if (Array.isArray(body?.detail)) {
          // FastAPI 422 validation body
          detail = body.detail
            .map((d: { msg?: string }) => d?.msg)
            .filter(Boolean)
            .join("; ") || detail;
        }
      } catch {
        /* non-JSON error body — keep the status-code message */
      }
      return { ok: false, status: response.status, error: detail };
    }

    return { ok: true, data: (await response.json()) as T };
  } catch (error) {
    const message =
      error instanceof Error && error.name === "AbortError"
        ? "Request timed out"
        : error instanceof Error
          ? error.message
          : "Network error";
    return { ok: false, status: null, error: message };
  } finally {
    clearTimeout(timer);
  }
}

/* ---------------------------------------------------------------- reads */

export function getEvents(params?: {
  category?: string;
  from_date?: string;
  to_date?: string;
  limit?: number;
  offset?: number;
}) {
  return request<ListEnvelope<EventItem>>("/api/v1/events", { params });
}

export function getEvent(slug: string) {
  return request<EventItem>(`/api/v1/events/${encodeURIComponent(slug)}`);
}

export function getTemples(params?: { limit?: number; offset?: number }) {
  return request<ListEnvelope<Temple>>("/api/v1/temples", { params });
}

export function getTemple(slug: string) {
  return request<Temple>(`/api/v1/temples/${encodeURIComponent(slug)}`);
}

export function getGhats(params?: { limit?: number; offset?: number }) {
  return request<ListEnvelope<Ghat>>("/api/v1/ghats", { params });
}

/** `{id}` accepts a numeric id or a slug (contract §3). */
export function getGhatStatus(idOrSlug: string | number) {
  return request<GhatStatus>(
    `/api/v1/ghats/${encodeURIComponent(String(idOrSlug))}/status`,
  );
}

export function getEmergencyServices(params?: { category?: string }) {
  return request<ListEnvelope<EmergencyService>>("/api/v1/emergency/services", {
    params,
  });
}

export function getAnnouncements(params?: { limit?: number }) {
  return request<ListEnvelope<Announcement>>("/api/v1/announcements", { params });
}

export function getLostFoundCase(caseReference: string) {
  return request<LostFoundCase>(
    `/api/v1/lost-found/${encodeURIComponent(caseReference)}`,
  );
}

export function getMissingPersonCase(caseReference: string) {
  return request<MissingPersonCase>(
    `/api/v1/missing-person/${encodeURIComponent(caseReference)}`,
  );
}

/* --------------------------------------------------------------- writes */

export function postSos(payload: SosRequest) {
  return request<SosResponse>("/api/v1/emergency/sos", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function postLostFound(payload: LostFoundRequest) {
  return request<CaseSubmissionResponse>("/api/v1/lost-found", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function postMissingPerson(payload: MissingPersonRequest) {
  return request<CaseSubmissionResponse>("/api/v1/missing-person", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/* ---------------------------------------------------- authenticated calls */

export function authedRequest<T>(
  path: string,
  token: string,
  init: RequestInit = {},
): Promise<ApiResult<T>> {
  return request<T>(path, {
    ...init,
    headers: { Authorization: `Bearer ${token}`, ...(init.headers || {}) },
  });
}

export { request as apiRequest };
