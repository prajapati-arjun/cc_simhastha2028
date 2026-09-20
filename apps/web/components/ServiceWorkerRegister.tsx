"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { initSosQueueAutoFlush } from "@/lib/offlineQueue";

/**
 * Mounted once from the root locale layout (PRD §33 offline shell).
 *
 * Registers the offline-shell service worker (public/sw.js) and wires the
 * SOS sync queue (lib/offlineQueue.ts) to auto-flush the moment the browser
 * comes back online. Also renders a small, non-blocking connectivity strip
 * so "you're offline" is never a silent state.
 *
 * Deliberately separate from SafetyBanner: that component always means "this
 * data is simulated / not connected to live dispatch" regardless of network
 * state, and must never be diluted by an unrelated connectivity message —
 * this strip uses its own copy and its own (neutral, non-alarming) styling.
 */
export function ServiceWorkerRegister() {
  const t = useTranslations("offline");
  const [mounted, setMounted] = useState(false);
  const [online, setOnline] = useState(true);

  useEffect(() => {
    setMounted(true);
    setOnline(navigator.onLine);

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {
        // Best-effort only — the app must be fully usable with no offline
        // support too (older browsers, disabled SW, etc.).
      });
    }

    initSosQueueAutoFlush();

    function handleOnline() {
      setOnline(true);
    }
    function handleOffline() {
      setOnline(false);
    }
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  if (!mounted || online) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="w-full border-b border-surface-border bg-surface-subtle px-4 py-2 text-center text-sm text-ink-secondary"
    >
      {t("bannerOffline")}
    </div>
  );
}

export default ServiceWorkerRegister;
