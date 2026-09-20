"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

/**
 * ReferenceNumberDisplay — post-submit confirmation code block.
 * The opaque case reference is the ONLY way a reporter can read their case back
 * (decision D-01), so it is displayed prominently and is copyable.
 */
export function ReferenceNumberDisplay({
  label,
  reference,
  note,
}: {
  label: string;
  reference: string;
  note?: string;
}) {
  const t = useTranslations("common");
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(reference);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable — the code is still visible and selectable */
    }
  }

  return (
    <div className="card-surface p-4">
      <p className="text-sm font-medium text-ink-secondary">{label}</p>
      <div className="mt-1 flex flex-wrap items-center gap-3">
        <code className="select-all rounded-sm bg-surface-subtle px-3 py-2 text-xl font-bold tracking-wider text-ink-primary">
          {reference}
        </code>
        <button type="button" className="btn-outline" onClick={copy}>
          {copied ? t("copied") : t("copy")}
        </button>
      </div>
      {note ? <p className="mt-3 text-sm text-ink-secondary">{note}</p> : null}
    </div>
  );
}

export default ReferenceNumberDisplay;
