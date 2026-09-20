"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";
import { ErrorState } from "@/components/States";
import {
  SelectField,
  TextAreaField,
  TextField,
} from "@/components/form/Fields";
import { Link, useRouter } from "@/i18n/navigation";
import { authedRequest } from "@/lib/api";
import { readSession } from "@/lib/adminAuth";
import { dateTimeLocalToIso, toDateTimeLocalValue } from "@/lib/format";
import type { AdminEntityKey, ListEnvelope, PublicationStatus } from "@/lib/types";
import { ADMIN_ENTITIES, type AdminField } from "./adminEntities";
import PublishToggle from "./PublishToggle";

type Row = Record<string, unknown> & { id: number; status: PublicationStatus };
type Values = Record<string, string>;

function toFormValue(field: AdminField, raw: unknown): string {
  if (raw === null || raw === undefined) return "";
  if (field.type === "csv") {
    return Array.isArray(raw) ? raw.join(", ") : String(raw);
  }
  if (field.type === "datetime") {
    const date = new Date(String(raw));
    return Number.isNaN(date.getTime()) ? "" : toDateTimeLocalValue(date);
  }
  return String(raw);
}

function toPayloadValue(field: AdminField, value: string): unknown {
  if (value === "") return null;
  if (field.type === "csv") {
    return value
      .split(",")
      .map((part) => part.trim())
      .filter(Boolean);
  }
  if (field.type === "number") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  if (field.type === "datetime") return dateTimeLocalToIso(value);
  return value;
}

export function EntityForm({
  entityKey,
  recordId,
}: {
  entityKey: AdminEntityKey;
  recordId?: number;
}) {
  const config = ADMIN_ENTITIES[entityKey];
  const t = useTranslations("admin");
  const tc = useTranslations("common");
  const router = useRouter();

  const [values, setValues] = useState<Values>({});
  // New records always start as Draft — publishing is a separate explicit act.
  const [status, setStatus] = useState<PublicationStatus>("draft");
  const [loading, setLoading] = useState(Boolean(recordId));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!recordId) return;
    const session = readSession();
    if (!session) return;
    // The contract does not guarantee an admin GET-by-id, so the edit screen
    // reads the admin list (which includes drafts) and selects the record.
    const response = await authedRequest<ListEnvelope<Row>>(
      `/api/v1/admin/${config.path}`,
      session.token,
    );
    setLoading(false);
    if (!response.ok) {
      setError(response.error);
      return;
    }
    const record = response.data.items.find((item) => item.id === recordId);
    if (!record) {
      setError(`#${recordId}`);
      return;
    }
    const next: Values = {};
    for (const field of config.fields) {
      next[field.name] = toFormValue(field, record[field.name]);
    }
    setValues(next);
    setStatus(record.status);
  }, [config, recordId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const session = readSession();
    if (!session) return;
    setSaving(true);
    setError(null);
    setMessage(null);

    const payload: Record<string, unknown> = { status };
    for (const field of config.fields) {
      payload[field.name] = toPayloadValue(field, values[field.name] ?? "");
    }

    const response = recordId
      ? await authedRequest(
          `/api/v1/admin/${config.path}/${recordId}`,
          session.token,
          { method: "PATCH", body: JSON.stringify(payload) },
        )
      : await authedRequest(`/api/v1/admin/${config.path}`, session.token, {
          method: "POST",
          body: JSON.stringify(payload),
        });

    setSaving(false);
    if (response.ok) {
      setMessage(t("saved"));
      router.push(`/admin/${config.path}`);
      return;
    }
    setError(response.error);
  }

  if (loading) {
    return (
      <p role="status" aria-live="polite">
        {tc("loading")}
      </p>
    );
  }

  return (
    <section>
      <h1>
        {recordId ? t("edit") : t("createNew")} — {t(config.labelKey)}
      </h1>

      {error ? (
        <div className="mt-4">
          <ErrorState title={t("saveFailed")} detail={error} />
        </div>
      ) : null}
      {message ? (
        <p className="mt-4 text-status-success" role="status">
          {message}
        </p>
      ) : null}

      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5" noValidate>
        {config.fields.map((field) => {
          const value = values[field.name] ?? "";
          const onChange = (next: string) =>
            setValues((current) => ({ ...current, [field.name]: next }));

          if (field.type === "textarea") {
            return (
              <TextAreaField
                key={field.name}
                label={field.label}
                name={field.name}
                required={field.required}
                value={value}
                onChange={onChange}
              />
            );
          }
          if (field.type === "select") {
            return (
              <SelectField
                key={field.name}
                label={field.label}
                name={field.name}
                required={field.required}
                value={value || (field.options?.[0] ?? "")}
                onChange={onChange}
                options={(field.options ?? []).map((option) => ({
                  value: option,
                  label: option,
                }))}
              />
            );
          }
          return (
            <TextField
              key={field.name}
              label={field.label}
              name={field.name}
              required={field.required}
              type={
                field.type === "datetime"
                  ? "datetime-local"
                  : field.type === "number"
                    ? "number"
                    : field.type === "url"
                      ? "url"
                      : "text"
              }
              value={value}
              onChange={onChange}
            />
          );
        })}

        <fieldset className="rounded-md border border-surface-border p-4">
          <legend className="px-1 text-sm font-semibold">
            {t("publishStateTitle")}
          </legend>
          <PublishToggle status={status} onChange={setStatus} />
          <p className="mt-2 text-sm text-ink-secondary">{t("publishStateHelp")}</p>
        </fieldset>

        <div className="flex flex-wrap gap-3">
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? tc("submitting") : tc("save")}
          </button>
          <Link href={`/admin/${config.path}`} className="btn-outline">
            {t("backToList")}
          </Link>
        </div>
      </form>
    </section>
  );
}

export default EntityForm;
