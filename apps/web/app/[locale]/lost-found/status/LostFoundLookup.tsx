"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import StatusBadge from "@/components/StatusBadge";
import { TextField } from "@/components/form/Fields";
import { getLostFoundCase } from "@/lib/api";
import type { LostFoundCase } from "@/lib/types";

/**
 * Lookup by opaque case reference only (decision D-01).
 * There is deliberately no list, no browse, and no search by name or phone.
 */
export function LostFoundLookup() {
  const t = useTranslations("lostFound");
  const tf = useTranslations("forms");
  const tc = useTranslations("common");

  const [reference, setReference] = useState("");
  const [error, setError] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LostFoundCase | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(undefined);
    setResult(null);
    if (!reference.trim()) {
      setError(tf("requiredField"));
      return;
    }
    setLoading(true);
    const response = await getLostFoundCase(reference.trim().toUpperCase());
    setLoading(false);
    if (response.ok) {
      setResult(response.data);
      return;
    }
    setError(response.status === 404 ? t("lookupNotFound") : response.error);
  }

  return (
    <div className="mt-6">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <TextField
          label={t("lookupLabel")}
          name="case_reference"
          required
          help={t("lookupHelp")}
          error={error}
          value={reference}
          onChange={setReference}
        />
        <button type="submit" className="btn-primary self-start" disabled={loading}>
          {loading ? tc("loading") : t("lookupSubmit")}
        </button>
      </form>

      <div aria-live="polite">
        {result ? (
          <div className="card-surface mt-6 p-4">
            <p className="text-sm text-ink-secondary">{t("referenceNumber")}</p>
            <p className="text-xl font-bold">{result.case_reference}</p>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-ink-secondary">
                {t("resultStatus")}:
              </span>
              <StatusBadge label={t(`status.${result.status}`)} tone="info" />
            </div>
            <p className="mt-3 text-sm text-ink-secondary">
              {t("resultUpdated")}: {result.updated_at}
            </p>
            <p className="mt-3 text-xs text-ink-secondary">
              {result.prototype_notice}
            </p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default LostFoundLookup;
