/**
 * SOS offline sync queue (PRD §33).
 *
 * When the SOS form can't reach the API — genuinely offline, or the request
 * fails for a connectivity reason rather than a validation reason — the
 * report is saved in IndexedDB instead of being dropped. It is sent for real
 * the moment the browser regains connectivity (via the `online` event) and
 * never marked as sent until the API actually accepts it.
 *
 * This module deliberately does NOT change what a successful submission looks
 * like (`postSos` in ./api is untouched) — it only adds a fallback path in
 * front of it, so the SOS demo-notice framing on a real response is preserved
 * exactly as-is.
 */
import { postSos } from "./api";
import type { SosRequest, SosResponse } from "./types";

const DB_NAME = "simhastha-offline";
const DB_VERSION = 1;
const STORE_NAME = "sos-queue";
const QUEUE_EVENT = "simhastha-sos-queue-changed";

export interface QueuedSosItem {
  id: string;
  payload: SosRequest;
  queuedAt: string;
}

export type SosSubmitResult =
  | { ok: true; queued: false; data: SosResponse }
  | { ok: true; queued: true; id: string; queuedAt: string }
  | { ok: false; queued: false; error: string };

export interface FlushResult {
  id: string;
  ok: boolean;
}

function isBrowser(): boolean {
  return typeof window !== "undefined" && "indexedDB" in window;
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (!isBrowser()) {
      reject(new Error("IndexedDB unavailable"));
      return;
    }
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("IndexedDB open failed"));
  });
}

function reqToPromise<T>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("IndexedDB request failed"));
  });
}

async function addItem(item: QueuedSosItem): Promise<void> {
  const db = await openDb();
  const store = db.transaction(STORE_NAME, "readwrite").objectStore(STORE_NAME);
  await reqToPromise(store.add(item));
}

async function getAllItems(): Promise<QueuedSosItem[]> {
  const db = await openDb();
  const store = db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME);
  return reqToPromise(store.getAll());
}

async function deleteItem(id: string): Promise<void> {
  const db = await openDb();
  const store = db.transaction(STORE_NAME, "readwrite").objectStore(STORE_NAME);
  await reqToPromise(store.delete(id));
}

function notifyQueueChanged() {
  if (isBrowser()) {
    window.dispatchEvent(new CustomEvent(QUEUE_EVENT));
  }
}

/** Subscribe to queue changes (item queued, sent, or dropped). Returns an unsubscribe fn. */
export function onSosQueueChanged(handler: () => void): () => void {
  if (!isBrowser()) return () => {};
  window.addEventListener(QUEUE_EVENT, handler);
  return () => window.removeEventListener(QUEUE_EVENT, handler);
}

export async function queueSosRequest(payload: SosRequest): Promise<QueuedSosItem> {
  const item: QueuedSosItem = {
    id: `sos-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    payload,
    queuedAt: new Date().toISOString(),
  };
  await addItem(item);
  notifyQueueChanged();
  return item;
}

export async function getQueuedSosRequests(): Promise<QueuedSosItem[]> {
  if (!isBrowser()) return [];
  try {
    return await getAllItems();
  } catch {
    return [];
  }
}

/**
 * Drop-in replacement for a direct `postSos(payload)` call from the SOS form.
 * - Offline right now: queue immediately, no network attempt (no point waiting
 *   out the 8s timeout in ./api to learn what navigator.onLine already knows).
 * - Online but the request fails for a network reason (status === null —
 *   ./api's `request()` reports timeouts/DNS/connection failures this way):
 *   queue it as a fallback.
 * - Online and the API responds (even with a 4xx, e.g. missing consent):
 *   surface that response as-is. A real validation rejection must never be
 *   silently queued and retried — only connectivity failures are.
 */
export async function submitSosOrQueue(payload: SosRequest): Promise<SosSubmitResult> {
  if (isBrowser() && !navigator.onLine) {
    const item = await queueSosRequest(payload);
    return { ok: true, queued: true, id: item.id, queuedAt: item.queuedAt };
  }

  const response = await postSos(payload);
  if (response.ok) {
    return { ok: true, queued: false, data: response.data };
  }
  if (response.status === null && isBrowser()) {
    const item = await queueSosRequest(payload);
    return { ok: true, queued: true, id: item.id, queuedAt: item.queuedAt };
  }
  return { ok: false, queued: false, error: response.error };
}

/** Attempt to send every queued SOS report. Safe to call whenever; it's a no-op offline. */
export async function flushSosQueue(): Promise<FlushResult[]> {
  if (!isBrowser() || !navigator.onLine) return [];
  const items = await getQueuedSosRequests();
  const results: FlushResult[] = [];

  for (const item of items) {
    const response = await postSos(item.payload);
    if (response.ok) {
      await deleteItem(item.id);
      results.push({ id: item.id, ok: true });
    } else if (response.status !== null) {
      // The API is reachable and rejected it outright — retrying forever would
      // just repeat the same rejection, so drop it rather than loop silently.
      await deleteItem(item.id);
      results.push({ id: item.id, ok: false });
    }
    // else: still no real connection — leave it queued for the next 'online' event.
  }

  if (results.length > 0) notifyQueueChanged();
  return results;
}

let autoFlushRegistered = false;

/** Call once (from a client component mounted globally) to wire auto-flush-on-reconnect. */
export function initSosQueueAutoFlush(): void {
  if (!isBrowser() || autoFlushRegistered) return;
  autoFlushRegistered = true;
  window.addEventListener("online", () => {
    void flushSosQueue();
  });
  if (navigator.onLine) {
    void flushSosQueue();
  }
}
