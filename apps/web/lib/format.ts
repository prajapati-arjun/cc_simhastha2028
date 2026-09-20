/**
 * Date/number formatting helpers.
 *
 * All API timestamps are ISO-8601 UTC (contract §0). Everything is rendered in
 * Asia/Kolkata with an explicit timeZone so the server-rendered string and the
 * client-hydrated string always match, regardless of where the container runs.
 */

const TIME_ZONE = "Asia/Kolkata";

function intlLocale(locale: string) {
  return locale === "hi" ? "hi-IN" : "en-IN";
}

export function formatDateTime(iso: string | null | undefined, locale = "en") {
  if (!iso) return null;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return null;
  return new Intl.DateTimeFormat(intlLocale(locale), {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: TIME_ZONE,
  }).format(date);
}

export function formatDate(iso: string | null | undefined, locale = "en") {
  if (!iso) return null;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return null;
  return new Intl.DateTimeFormat(intlLocale(locale), {
    dateStyle: "medium",
    timeZone: TIME_ZONE,
  }).format(date);
}

/** Value for a `datetime-local` input, in the browser's own local time. */
export function toDateTimeLocalValue(date: Date) {
  const pad = (n: number) => String(n).padStart(2, "0");
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
    `T${pad(date.getHours())}:${pad(date.getMinutes())}`
  );
}

/** `datetime-local` value -> ISO-8601 UTC string for the API. */
export function dateTimeLocalToIso(value: string): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString();
}
