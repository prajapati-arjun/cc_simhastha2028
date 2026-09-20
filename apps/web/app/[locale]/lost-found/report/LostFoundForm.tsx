"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import ReferenceNumberDisplay from "@/components/ReferenceNumberDisplay";
import SafetyBanner from "@/components/SafetyBanner";
import {
  FormErrorSummary,
  RadioGroupField,
  SelectField,
  TextAreaField,
  TextField,
} from "@/components/form/Fields";
import { Link } from "@/i18n/navigation";
import { postLostFound } from "@/lib/api";
import { dateTimeLocalToIso, toDateTimeLocalValue } from "@/lib/format";
import type {
  CaseSubmissionResponse,
  LostFoundCategory,
  LostFoundReportType,
} from "@/lib/types";

const CATEGORIES: LostFoundCategory[] = [
  "bag",
  "documents",
  "phone",
  "jewellery",
  "child_item",
  "other",
];

export function LostFoundForm() {
  const t = useTranslations("lostFound");
  const tf = useTranslations("forms");
  const tc = useTranslations("common");

  const [reportType, setReportType] = useState<LostFoundReportType>("lost");
  const [category, setCategory] = useState<LostFoundCategory>("bag");
  const [description, setDescription] = useState("");
  const [locationText, setLocationText] = useState("");
  const [occurredAt, setOccurredAt] = useState(() =>
    toDateTimeLocalValue(new Date()),
  );
  const [reporterName, setReporterName] = useState("");
  const [reporterPhone, setReporterPhone] = useState("");
  const [imageUrl, setImageUrl] = useState("");

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [summary, setSummary] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<CaseSubmissionResponse | null>(null);

  function validate() {
    const errors: Record<string, string> = {};
    if (description.trim().length < 10 || description.trim().length > 2000) {
      errors.description = tf("descriptionLength");
    }
    if (!reporterPhone.trim()) {
      errors.reporterPhone = tf("phoneRequired");
    }
    if (!reporterName.trim()) {
      errors.reporterName = tf("requiredField");
    }
    const iso = dateTimeLocalToIso(occurredAt);
    if (!iso) {
      errors.occurredAt = tf("requiredField");
    } else if (new Date(iso).getTime() > Date.now()) {
      errors.occurredAt = tf("futureDate");
    }
    return errors;
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const errors = validate();
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) {
      setSummary(Object.values(errors));
      return;
    }
    setSummary([]);
    setSubmitting(true);
    const response = await postLostFound({
      report_type: reportType,
      category,
      description: description.trim(),
      location_text: locationText || null,
      latitude: null,
      longitude: null,
      occurred_at: dateTimeLocalToIso(occurredAt)!,
      reporter_name: reporterName.trim(),
      reporter_phone: reporterPhone.trim(),
      image_url: imageUrl || null,
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
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/lost-found/status" className="btn-primary">
            {t("checkStatus")}
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

      <RadioGroupField
        label={t("reportType")}
        name="report_type"
        required
        value={reportType}
        onChange={(value) => setReportType(value as LostFoundReportType)}
        options={[
          { value: "lost", label: t("reportTypeLost") },
          { value: "found", label: t("reportTypeFound") },
        ]}
      />
      <SelectField
        label={t("category")}
        name="category"
        required
        value={category}
        onChange={(value) => setCategory(value as LostFoundCategory)}
        options={CATEGORIES.map((value) => ({
          value,
          label: t(`categoryOptions.${value}`),
        }))}
      />
      <TextAreaField
        label={t("description")}
        name="description"
        required
        rows={5}
        maxLength={2000}
        help={t("descriptionHelp")}
        error={fieldErrors.description}
        value={description}
        onChange={setDescription}
      />
      <TextField
        label={`${t("location")} (${tc("optional")})`}
        name="location_text"
        value={locationText}
        onChange={setLocationText}
      />
      <TextField
        label={t("dateTime")}
        name="occurred_at"
        type="datetime-local"
        required
        error={fieldErrors.occurredAt}
        value={occurredAt}
        onChange={setOccurredAt}
      />
      <TextField
        label={`${t("imageUrl")} (${tc("optional")})`}
        name="image_url"
        type="url"
        inputMode="url"
        value={imageUrl}
        onChange={setImageUrl}
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
        label={t("reporterPhone")}
        name="reporter_phone"
        type="tel"
        inputMode="tel"
        required
        error={fieldErrors.reporterPhone}
        value={reporterPhone}
        onChange={setReporterPhone}
      />

      <SafetyBanner variant="lost-found" showFormNote />

      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? tc("submitting") : tc("submit")}
      </button>
    </form>
  );
}

export default LostFoundForm;
