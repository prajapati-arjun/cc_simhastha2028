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
import { postMissingPerson } from "@/lib/api";
import { dateTimeLocalToIso, toDateTimeLocalValue } from "@/lib/format";
import type { CaseSubmissionResponse } from "@/lib/types";

const GENDERS = ["male", "female", "other", "unspecified"] as const;

export function MissingPersonForm() {
  const t = useTranslations("missingPerson");
  const tf = useTranslations("forms");
  const tc = useTranslations("common");

  const [personName, setPersonName] = useState("");
  const [personAge, setPersonAge] = useState("");
  const [personGender, setPersonGender] = useState<string>("unspecified");
  const [physicalDescription, setPhysicalDescription] = useState("");
  const [lastSeenLocation, setLastSeenLocation] = useState("");
  const [lastSeenAt, setLastSeenAt] = useState(() =>
    toDateTimeLocalValue(new Date()),
  );
  const [photoUrl, setPhotoUrl] = useState("");
  const [reporterName, setReporterName] = useState("");
  const [reporterPhone, setReporterPhone] = useState("");
  const [relationship, setRelationship] = useState("");
  const [consent, setConsent] = useState(false);

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [summary, setSummary] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<CaseSubmissionResponse | null>(null);

  function validate() {
    const errors: Record<string, string> = {};
    if (!personName.trim()) errors.personName = tf("requiredField");
    if (personAge.trim()) {
      const age = Number(personAge);
      if (!Number.isFinite(age) || age < 0 || age > 120) {
        errors.personAge = tf("invalidNumber");
      }
    }
    if (!reporterName.trim()) errors.reporterName = tf("requiredField");
    if (!reporterPhone.trim()) errors.reporterPhone = tf("phoneRequired");
    const iso = dateTimeLocalToIso(lastSeenAt);
    if (!iso) {
      errors.lastSeenAt = tf("requiredField");
    } else if (new Date(iso).getTime() > Date.now()) {
      errors.lastSeenAt = tf("futureDate");
    }
    return errors;
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const errors = validate();
    if (!consent) errors.consent = t("consentRequired");
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) {
      setSummary(Object.values(errors));
      return;
    }
    setSummary([]);
    setSubmitting(true);
    const response = await postMissingPerson({
      person_name: personName.trim(),
      person_age: personAge.trim() ? Number(personAge) : null,
      person_gender: personGender === "unspecified" ? null : personGender,
      physical_description: physicalDescription || null,
      last_seen_location_text: lastSeenLocation || null,
      latitude: null,
      longitude: null,
      last_seen_at: dateTimeLocalToIso(lastSeenAt)!,
      photo_url: photoUrl || null,
      reporter_name: reporterName.trim(),
      reporter_phone: reporterPhone.trim(),
      reporter_relationship: relationship || null,
      consent_given: true,
    });
    setSubmitting(false);
    if (response.ok) {
      setResult(response.data);
      return;
    }
    setSummary([response.status ? response.error : tf("networkError")]);
  }

  if (result) {
    return (
      <div className="mt-6">
        <h2 className="text-2xl font-semibold">{t("confirmTitle")}</h2>
        <div className="mt-4">
          <ReferenceNumberDisplay
            label={t("referenceNumber")}
            reference={result.case_reference}
            note={t("referenceKeepSafe")}
          />
        </div>
        <p className="mt-4 rounded-md border border-secondary-500 bg-secondary-50 p-4 text-sm font-medium">
          {result.prototype_notice}
        </p>
        <p className="mt-4 font-semibold">{t("policeNote")}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/missing-person/status" className="btn-primary">
            {t("statusTitle")}
          </Link>
          <Link href="/" className="btn-outline">
            {tc("back")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5" noValidate>
      <FormErrorSummary title={tf("errorSummary")} messages={summary} />

      <TextField
        label={t("personName")}
        name="person_name"
        required
        error={fieldErrors.personName}
        value={personName}
        onChange={setPersonName}
      />
      <TextField
        label={`${t("age")} (${tc("optional")})`}
        name="person_age"
        type="number"
        inputMode="numeric"
        error={fieldErrors.personAge}
        value={personAge}
        onChange={setPersonAge}
      />
      <SelectField
        label={t("gender")}
        name="person_gender"
        value={personGender}
        onChange={setPersonGender}
        options={GENDERS.map((value) => ({
          value,
          label: t(`genderOptions.${value}`),
        }))}
      />
      <TextAreaField
        label={`${t("physicalDescription")} (${tc("optional")})`}
        name="physical_description"
        rows={4}
        value={physicalDescription}
        onChange={setPhysicalDescription}
      />
      <TextField
        label={`${t("lastSeenLocation")} (${tc("optional")})`}
        name="last_seen_location_text"
        value={lastSeenLocation}
        onChange={setLastSeenLocation}
      />
      <TextField
        label={t("lastSeenDateTime")}
        name="last_seen_at"
        type="datetime-local"
        required
        error={fieldErrors.lastSeenAt}
        value={lastSeenAt}
        onChange={setLastSeenAt}
      />
      <TextField
        label={`${t("photoUrl")} (${tc("optional")})`}
        name="photo_url"
        type="url"
        inputMode="url"
        value={photoUrl}
        onChange={setPhotoUrl}
      />
      <TextField
        label={t("reporterName")}
        name="reporter_name"
        required
        error={fieldErrors.reporterName}
        value={reporterName}
        onChange={setReporterName}
      />
      <TextField
        label={t("reporterContact")}
        name="reporter_phone"
        type="tel"
        inputMode="tel"
        required
        error={fieldErrors.reporterPhone}
        value={reporterPhone}
        onChange={setReporterPhone}
      />
      <TextField
        label={`${t("relationship")} (${tc("optional")})`}
        name="reporter_relationship"
        value={relationship}
        onChange={setRelationship}
      />

      <ConsentCheckbox
        label={t("consent")}
        name="consent_given"
        checked={consent}
        onChange={setConsent}
        error={fieldErrors.consent}
      />

      <SafetyBanner variant="missing-person" showFormNote />

      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? tc("submitting") : tc("submit")}
      </button>
    </form>
  );
}

export default MissingPersonForm;
