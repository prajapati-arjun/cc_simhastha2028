/**
 * Simhastha 2028 — offline shell service worker (PRD §33).
 *
 * Deliberately narrow scope for a demo prototype: it caches the app shell
 * plus exactly three read-only surfaces — the emergency directory, temple
 * info, and events/calendar — and the SOS report form shell (so the sync
 * queue in lib/offlineQueue.ts has something to run inside while offline).
 * Everything else (admin, planner, lost-found, missing-person, and every
 * /api/v1/* call to the API origin) is left untouched and goes straight to
 * the network. Caching a safety-critical write path, or any surface not
 * explicitly reviewed for staleness handling, would risk letting stale or
 * simulated data look more authoritative than it is — see
 * Docs/PROTOTYPE_LIMITATIONS.md.
 *
 * Strategy: stale-while-revalidate for the cacheable page navigations below
 * (instant response from cache when present, refreshed in the background),
 * cache-first for hashed Next.js static assets, and a locale-aware offline
 * fallback page when a navigation has neither a cached copy nor a network.
 */

const VERSION = "v1";
const STATIC_CACHE = `simhastha-static-${VERSION}`;
const PAGES_CACHE = `simhastha-pages-${VERSION}`;

// English is served unprefixed, Hindi at /hi/... (i18n/routing.ts, localePrefix: "as-needed").
const PRECACHE_URLS = [
  "/manifest.json",
  "/icons/icon.svg",
  "/icons/icon-maskable.svg",
  "/offline",
  "/hi/offline",
  "/emergency",
  "/hi/emergency",
  "/emergency/sos",
  "/hi/emergency/sos",
  "/temples",
  "/hi/temples",
  "/events",
  "/hi/events",
];

const CACHEABLE_PATH_RE =
  /^\/(hi\/)?(emergency(\/sos)?|temples(\/[^/]+)?|events(\/[^/]+)?|offline)\/?$/;

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(PAGES_CACHE);
      await Promise.all(
        PRECACHE_URLS.map((url) =>
          cache.add(url).catch(() => {
            // Best-effort warmup only — e.g. the API being down on first
            // install must not fail the whole service worker registration.
          }),
        ),
      );
      self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((key) => key !== STATIC_CACHE && key !== PAGES_CACHE)
          .map((key) => caches.delete(key)),
      );
      await self.clients.claim();
    })(),
  );
});

function isCacheablePage(url) {
  return CACHEABLE_PATH_RE.test(url.pathname);
}

function isStaticAsset(url) {
  return url.origin === self.location.origin && url.pathname.startsWith("/_next/static/");
}

function isPrecachedAsset(url) {
  return url.pathname === "/manifest.json" || url.pathname.startsWith("/icons/");
}

function offlineFallbackFor(pathname) {
  return pathname.startsWith("/hi/") ? "/hi/offline" : "/offline";
}

async function handleNavigate(request, event) {
  const url = new URL(request.url);
  const cache = await caches.open(PAGES_CACHE);
  const cached = await cache.match(request);

  const networkUpdate = fetch(request)
    .then((response) => {
      if (response && response.ok) cache.put(request, response.clone());
      return response;
    })
    .catch(() => null);

  if (cached) {
    // Serve the cached page instantly; keep refreshing it in the background
    // for next time. `waitUntil` keeps the worker alive long enough to finish.
    event.waitUntil(networkUpdate);
    return cached;
  }

  const fresh = await networkUpdate;
  if (fresh) return fresh;

  const fallback = await cache.match(offlineFallbackFor(url.pathname));
  return fallback || Response.error();
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response && response.ok) cache.put(request, response.clone());
    return response;
  } catch {
    return Response.error();
  }
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // never intercept the API origin

  if (request.mode === "navigate" && isCacheablePage(url)) {
    event.respondWith(handleNavigate(request, event));
    return;
  }

  if (isStaticAsset(url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  if (isPrecachedAsset(url)) {
    event.respondWith(cacheFirst(request, PAGES_CACHE));
    return;
  }

  // Everything else (other pages, admin, planner, lost-found, missing-person,
  // every /api/v1/* call) falls through to normal, un-intercepted network handling.
});
