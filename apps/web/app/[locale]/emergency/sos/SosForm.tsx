"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import ReferenceNumberDisplay from "@/components/ReferenceNumberDisplay";
import SafetyBanner from "@/components/SafetyBanner";
import {
  ConsentCheckbox,
  FormErrorSummary,
  SelectField,
  TextAreaField,
  TextField,
} from "@/components/form/Fields";
import { Link } from "@/i18n/navigation";
import { submitSosOrQueue } from "@/lib/offlineQueue";
import SosQueuedNotice from "@/components/SosQueuedNotice";
import type { SosResponse, SosSituationCategory } from "@/lib/types";

const SITUATIONS: SosSituationCategory[] = [
  "medical",
  "security",
  "fire",
  "lost_person",
  "other",
];

export function SosForm() {
  const t = useTranslations("emergency");
  const tf = useTranslations("forms");
  const tc = useTranslations("common");

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [situation, setSituation] = useState<SosSituationCategory>("medical");
  const [note, setNote] = useState("");
  const [consent, setConsent] = useState(false);
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [geoMessage, setGeoMessage] = useState<string | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [consentError, setConsentError] = useState<string | undefined>();
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<SosResponse | null>(null);
  const [queued, setQueued] = useState<{ id: string; queuedAt: string } | null>(null);

  function requestLocation() {
    if (typeof navigator === "undefined" || !navigator.geolocation) {
      setGeoMessage(t("locationUnavailable"));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoords({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setGeoMessage(t("locationCaptured"));
      },
      () => setGeoMessage(t("locationUnavailable")),
    );
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setErrors([]);
    setConsentError(undefined);

    // Consent gate, per PRD §15 — the API also rejects consent_given:false with 422.
    if (!consent) {
      setConsentError(t("sosConsentRequired"));
      setErrors([t("sosConsentRequired")]);
      return;
    }

    setSubmitting(true);
    const response = await submitSosOrQueue({
      reporter_name: name || null,
      reporter_phone: phone || null,
      situation_category: situation,
      note: note || null,
      latitude: coords?.lat ?? null,
      longitude: coords?.lng ?? null,
      consent_given: true,
    });
    setSubmitting(false);

    if (response.ok && !response.queued) {
      setResult(response.data);
      return;
    }
    if (response.ok && response.queued) {
      setQueued({ id: response.id, queuedAt: response.queuedAt });
      return;
    }
    setErrors([response.error]);
  }

  if (queued) {
    return <SosQueuedNotice id={queued.id} queuedAt={queued.queuedAt} />;
  }

  if (result) {
    return (
      <div className="mt-6">
        <h2 className="text-2xl font-semibold">{t("sosConfirmTitle")}</h2>
        <div className="mt-4">
          <ReferenceNumberDisplay
            label={tc("copy")}
            reference={result.case_reference}
          />
        </div>
        {/* The demo notice is repeated on the confirmation screen, verbatim
            from the API response, alongside the standing banner above. */}
        <p className="mt-4 rounded-md border border-secondary-500 bg-secondary-50 p-4 text-sm font-medium">
          {result.prototype_notice}
        </p>
        <p className="mt-4 font-semibold">{t("callDirect")}</p>
        <div className="mt-6">
          <Link href="/emergency" className="btn-outline">
            {tc("back")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5" noValidate>
      <FormErrorSummary title={tf("errorSummary")} messages={errors} />

      <SelectField
        label={t("situationCategory")}
        name="situation_category"
        required
        value={situation}
        onChange={(value) => setSituation(value as SosSituationCategory)}
        options={SITUATIONS.map((value) => ({
          value,
          label: t(`situation.${value}`),
        }))}
      />
      <TextField
        label={`${t("reporterName")} (${tc("optional")})`}
        name="reporter_name"
        value={name}
        onChange={setName}
      />
      <TextField
        label={`${t("reporterPhone")} (${tc("optional")})`}
        name="reporter_phone"
        type="tel"
        inputMode="tel"
        value={phone}
        onChange={setPhone}
      />
      <TextAreaField
        label={`${t("note")} (${tc("optional")})`}
        name="note"
        value={note}
        onChange={setNote}
      />

      <div>
        <button type="button" className="btn-outline" onClick={requestLocation}>
          {t("useMyLocation")}
        </button>
        <p className="mt-2 text-sm text-ink-secondary" aria-live="polite">
          {geoMessage ?? t("locationNotShared")}
        </p>
      </div>

      <ConsentCheckbox
        label={t("sosConsent")}
        name="consent_given"
        checked={consent}
        onChange={setConsent}
        error={consentError}
      />

      {/* Form-note variant sits directly above the submit button. */}
      <SafetyBanner variant="emergency" showFormNote />

      <button type="submit" className="btn-secondary text-lg" disabled={submitting}>
        {submitting ? tc("submitting") : t("submitSos")}
      </button>
    </form>
  );
}

export default SosForm;
