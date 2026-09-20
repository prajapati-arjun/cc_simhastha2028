"use client";

import { useLocale, useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { formatDateTime } from "@/lib/format";
import { getQueuedSosRequests, onSosQueueChanged } from "@/lib/offlineQueue";

export interface SosQueuedNoticeProps {
  id: string;
  queuedAt: string;
}

/**
 * Shown by the SOS form in place of the normal confirmation screen when the
 * report was queued (offline / no connectivity) rather than actually
 * accepted by the API. Never implies dispatch happened — mirrors the
 * standing SOS demo-notice framing (Docs/PROTOTYPE_LIMITATIONS.md) and adds
 * to it, since "queued" is an extra caveat on top of "simulated", not a
 * replacement for it.
 *
 * Polls the local queue (and listens for the queue-changed event fired by
 * lib/offlineQueue.ts) so that once the item is actually flushed to the API
 * after reconnecting, this same screen updates to reflect that — without
 * requiring the user to do anything or reload.
 */
export function SosQueuedNotice({ id, queuedAt }: SosQueuedNoticeProps) {
  const t = useTranslations("offline");
  const tc = useTranslations("common");
  const locale = useLocale();
  const [flushed, setFlushed] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function check() {
      const items = await getQueuedSosRequests();
      if (!cancelled && !items.some((item) => item.id === id)) {
        setFlushed(true);
      }
    }

    check();
    const unsubscribe = onSosQueueChanged(check);
    return () => {
      cancelled = true;
      unsubscribe();
    };
  }, [id]);

  const formatted = formatDateTime(queuedAt, locale);

  return (
    <div
      role="status"
      aria-live="polite"
      className="mt-6 rounded-md border border-secondary-500 bg-secondary-50 p-4"
    >
      <h2 className="text-2xl font-semibold">
        {flushed ? t("sosFlushedTitle") : t("sosQueuedTitle")}
      </h2>
      <p className="mt-2 text-ink-primary">
        {flushed ? t("sosFlushedMessage") : t("sosQueuedMessage")}
      </p>
      {!flushed ? (
        <p className="mt-2 text-sm font-medium text-ink-secondary">{t("sosQueuedWaiting")}</p>
      ) : null}
      {/* Repeats the "this is a prototype, not live dispatch" framing even
          once sent — a queued report is still a simulated one. */}
      <p className="mt-4 text-sm font-medium">{t("sosQueuedNoticeRepeat")}</p>
      {formatted ? (
        <p className="mt-2 text-xs text-ink-secondary">{tc("lastUpdated", { date: formatted })}</p>
      ) : null}
    </div>
  );
}

export default SosQueuedNotice;
