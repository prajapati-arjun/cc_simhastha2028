"use client";

import { useLocale, useTranslations } from "next-intl";
import { useState } from "react";
import {
  CheckboxGroupField,
  FormErrorSummary,
  SelectField,
  TextField,
} from "@/components/form/Fields";
import { postPlannerItinerary } from "@/lib/api";
import { formatDate, formatDateTime } from "@/lib/format";
import type {
  AccessibilityRequirement,
  AccommodationPreference,
  AgeGroup,
  PilgrimInterest,
  PlannerResponse,
  TransportMode,
} from "@/lib/types";

const AGE_GROUPS: AgeGroup[] = ["infant", "child", "adult", "senior"];
const TRANSPORT_MODES: TransportMode[] = ["car", "bus", "train", "walking", "other"];
const ACCOMMODATION_PREFERENCES: AccommodationPreference[] = [
  "budget",
  "mid_range",
  "premium",
  "dharamshala",
  "not_needed",
];
const INTERESTS: PilgrimInterest[] = [
  "spiritual",
  "cultural",
  "historical",
  "family_friendly",
  "photography",
];
const ACCESSIBILITY_REQUIREMENTS: AccessibilityRequirement[] = [
  "wheelchair",
  "visual_impairment",
  "hearing_impairment",
  "elderly_mobility",
];

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function PlannerForm() {
  const t = useTranslations("planner");
  const tf = useTranslations("forms");
  const tc = useTranslations("common");
  const locale = useLocale();

  const [arrivalDate, setArrivalDate] = useState(todayIso());
  const [departureDate, setDepartureDate] = useState(todayIso());
  const [partySize, setPartySize] = useState("2");
  const [ageGroups, setAgeGroups] = useState<string[]>([]);
  const [transportMode, setTransportMode] = useState<TransportMode>("car");
  const [accommodationPreference, setAccommodationPreference] =
    useState<AccommodationPreference>("budget");
  const [interests, setInterests] = useState<string[]>([]);
  const [accessibilityRequirements, setAccessibilityRequirements] = useState<
    string[]
  >([]);

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [summary, setSummary] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<PlannerResponse | null>(null);

  function validate() {
    const errors: Record<string, string> = {};
    if (!arrivalDate) errors.arrivalDate = tf("requiredField");
    if (!departureDate) errors.departureDate = tf("requiredField");
    if (arrivalDate && departureDate && departureDate < arrivalDate) {
      errors.departureDate = t("departureBeforeArrival");
    }
    const size = Number(partySize);
    if (!Number.isInteger(size) || size < 1) {
      errors.partySize = tf("invalidNumber");
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
    const response = await postPlannerItinerary({
      arrival_date: arrivalDate,
      departure_date: departureDate,
      party_size: Number(partySize),
      age_groups: ageGroups as AgeGroup[],
      transport_mode: transportMode,
      accommodation_preference: accommodationPreference,
      interests: interests as PilgrimInterest[],
      accessibility_requirements:
        accessibilityRequirements as AccessibilityRequirement[],
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
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-2xl font-semibold">{t("resultTitle")}</h2>
          <button
            type="button"
            className="btn-outline"
            onClick={() => setResult(null)}
          >
            {t("planAnother")}
          </button>
        </div>

        <div className="mt-6 flex flex-col gap-6">
          {result.days.map((day) => (
            <section key={day.date} className="card-surface p-4">
              <h3 className="text-lg font-semibold">
                {t("dayLabel", { number: day.day_number })} —{" "}
                <time dateTime={day.date}>{formatDate(day.date, locale)}</time>
              </h3>
              {day.rest_period ? (
                <p className="mt-2 text-sm text-ink-secondary">
                  {t("restPeriod")}
                </p>
              ) : (
                <div className="mt-3 flex flex-col gap-3">
                  {day.temples.length > 0 ? (
                    <div>
                      <p className="text-sm font-semibold text-ink-primary">
                        {t("temples")}
                      </p>
                      <ul className="mt-1 list-inside list-disc text-sm text-ink-secondary">
                        {day.temples.map((temple) => (
                          <li key={temple.id}>{temple.name}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                  {day.ghats.length > 0 ? (
                    <div>
                      <p className="text-sm font-semibold text-ink-primary">
                        {t("ghats")}
                      </p>
                      <ul className="mt-1 list-inside list-disc text-sm text-ink-secondary">
                        {day.ghats.map((ghat) => (
                          <li key={ghat.id}>{ghat.name}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                  {day.events.length > 0 ? (
                    <div>
                      <p className="text-sm font-semibold text-ink-primary">
                        {t("events")}
                      </p>
                      <ul className="mt-1 list-inside list-disc text-sm text-ink-secondary">
                        {day.events.map((eventItem) => (
                          <li key={eventItem.id}>
                            {eventItem.title}
                            {eventItem.venue_name ? ` — ${eventItem.venue_name}` : ""}{" "}
                            ({formatDateTime(eventItem.starts_at, locale)})
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </div>
              )}
            </section>
          ))}
        </div>

        {result.unscheduled_temples.length > 0 ||
        result.unscheduled_ghats.length > 0 ? (
          <div className="mt-6 rounded-md border border-surface-border bg-surface-subtle p-4 text-sm text-ink-secondary">
            <p className="font-semibold text-ink-primary">
              {t("unscheduledTitle")}
            </p>
            {result.unscheduled_temples.length > 0 ? (
              <p className="mt-1">
                {t("unscheduledTemples", {
                  names: result.unscheduled_temples
                    .map((temple) => temple.name)
                    .join(", "),
                })}
              </p>
            ) : null}
            {result.unscheduled_ghats.length > 0 ? (
              <p className="mt-1">
                {t("unscheduledGhats", {
                  names: result.unscheduled_ghats
                    .map((ghat) => ghat.name)
                    .join(", "),
                })}
              </p>
            ) : null}
          </div>
        ) : null}

        <div className="mt-6 flex flex-col gap-2 text-sm text-ink-secondary">
          <p>{result.transport_note}</p>
          <p>{result.accommodation_note}</p>
          {result.accessibility_note ? <p>{result.accessibility_note}</p> : null}
          {result.interest_note ? <p>{result.interest_note}</p> : null}
        </div>

        <p className="mt-4 rounded-md border border-secondary-500 bg-secondary-50 p-4 text-sm font-medium">
          {result.prototype_notice}
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5" noValidate>
      <FormErrorSummary title={tf("errorSummary")} messages={summary} />

      <div className="grid gap-5 sm:grid-cols-2">
        <TextField
          label={t("arrivalDate")}
          name="arrival_date"
          type="date"
          required
          error={fieldErrors.arrivalDate}
          value={arrivalDate}
          onChange={setArrivalDate}
        />
        <TextField
          label={t("departureDate")}
          name="departure_date"
          type="date"
          required
          error={fieldErrors.departureDate}
          value={departureDate}
          onChange={setDepartureDate}
        />
      </div>

      <TextField
        label={t("partySize")}
        name="party_size"
        type="number"
        inputMode="numeric"
        required
        error={fieldErrors.partySize}
        value={partySize}
        onChange={setPartySize}
      />

      <CheckboxGroupField
        label={t("ageGroups")}
        name="age_groups"
        value={ageGroups}
        onChange={setAgeGroups}
        options={AGE_GROUPS.map((value) => ({
          value,
          label: t(`ageGroupOptions.${value}`),
        }))}
      />

      <SelectField
        label={t("transportMode")}
        name="transport_mode"
        required
        value={transportMode}
        onChange={(value) => setTransportMode(value as TransportMode)}
        options={TRANSPORT_MODES.map((value) => ({
          value,
          label: t(`transportModeOptions.${value}`),
        }))}
      />

      <SelectField
        label={t("accommodationPreference")}
        name="accommodation_preference"
        required
        value={accommodationPreference}
        onChange={(value) =>
          setAccommodationPreference(value as AccommodationPreference)
        }
        options={ACCOMMODATION_PREFERENCES.map((value) => ({
          value,
          label: t(`accommodationOptions.${value}`),
        }))}
      />

      <CheckboxGroupField
        label={t("interests")}
        name="interests"
        value={interests}
        onChange={setInterests}
        options={INTERESTS.map((value) => ({
          value,
          label: t(`interestOptions.${value}`),
        }))}
      />

      <CheckboxGroupField
        label={t("accessibilityRequirements")}
        name="accessibility_requirements"
        value={accessibilityRequirements}
        onChange={setAccessibilityRequirements}
        options={ACCESSIBILITY_REQUIREMENTS.map((value) => ({
          value,
          label: t(`accessibilityOptions.${value}`),
        }))}
      />

      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? tc("submitting") : t("generate")}
      </button>
    </form>
  );
}

export default PlannerForm;
