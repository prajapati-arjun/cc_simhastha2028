"use client";

import { useEffect, useState } from "react";
import DataFreshnessTimestamp from "./DataFreshnessTimestamp";

export interface CachedDataFreshnessProps {
  updatedAt: string | null | undefined;
  className?: string;
}

/**
 * Drop-in replacement for <DataFreshnessTimestamp> on the three offline-shell
 * surfaces (emergency directory, temples, events — PRD §33).
 *
 * These pages are server components fetched with `cache: "no-store"` (see
 * lib/api.ts) — `updatedAt` reflects data freshness at the moment THIS
 * response was generated, not "now". The service worker (public/sw.js) may
 * later replay that exact same HTML response from its cache when the network
 * is unavailable; the server component has no way to know at render time
 * whether it's rendering a live response or one that's about to be cached and
 * replayed. The one thing knowable after the fact, client-side, is whether
 * the browser is currently offline — if it is, whatever is on screen can only
 * have come from a cache, so `isCached` is derived from that rather than
 * threaded through from the server.
 */
export function CachedDataFreshness({ updatedAt, className }: CachedDataFreshnessProps) {
  const [isCached, setIsCached] = useState(false);

  useEffect(() => {
    const update = () => setIsCached(!navigator.onLine);
    update();
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () => {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
    };
  }, []);

  return (
    <DataFreshnessTimestamp updatedAt={updatedAt} isCached={isCached} className={className} />
  );
}

export default CachedDataFreshness;
