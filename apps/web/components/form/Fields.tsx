"use client";

import { useId, type ReactNode } from "react";

/**
 * Shared form controls — UX_DESIGN_SYSTEM.md §5.7.
 * Every control has a visible <label> (never placeholder-only), marks required
 * fields both visually and with aria-required, and associates its error text
 * through aria-describedby.
 */

interface BaseFieldProps {
  label: string;
  name: string;
  required?: boolean;
  error?: string;
  help?: string;
  className?: string;
}

function FieldWrapper({
  label,
  htmlFor,
  required,
  error,
  help,
  helpId,
  errorId,
  className,
  children,
}: {
  label: string;
  htmlFor: string;
  required?: boolean;
  error?: string;
  help?: string;
  helpId: string;
  errorId: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div className={["flex flex-col gap-1", className].filter(Boolean).join(" ")}>
      <label htmlFor={htmlFor} className="text-sm font-semibold text-ink-primary">
        {label}
        {required ? (
          <span className="text-status-danger" aria-hidden="true">
            {" *"}
          </span>
        ) : null}
      </label>
      {help ? (
        <p id={helpId} className="text-xs text-ink-secondary">
          {help}
        </p>
      ) : null}
      {children}
      {error ? (
        <p id={errorId} role="alert" className="text-sm font-medium text-status-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}

function describedBy(
  help: string | undefined,
  error: string | undefined,
  helpId: string,
  errorId: string,
) {
  return (
    [help ? helpId : null, error ? errorId : null].filter(Boolean).join(" ") ||
    undefined
  );
}

export function TextField({
  label,
  name,
  required,
  error,
  help,
  className,
  type = "text",
  value,
  onChange,
  inputMode,
  maxLength,
}: BaseFieldProps & {
  type?: string;
  value: string;
  onChange: (value: string) => void;
  inputMode?: "text" | "tel" | "numeric" | "url";
  maxLength?: number;
}) {
  const id = useId();
  const helpId = `${id}-help`;
  const errorId = `${id}-error`;
  return (
    <FieldWrapper
      label={label}
      htmlFor={id}
      required={required}
      error={error}
      help={help}
      helpId={helpId}
      errorId={errorId}
      className={className}
    >
      <input
        id={id}
        name={name}
        type={type}
        value={value}
        inputMode={inputMode}
        maxLength={maxLength}
        aria-required={required || undefined}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(help, error, helpId, errorId)}
        onChange={(event) => onChange(event.target.value)}
        className="field-input"
      />
    </FieldWrapper>
  );
}

export function TextAreaField({
  label,
  name,
  required,
  error,
  help,
  className,
  value,
  onChange,
  rows = 4,
  maxLength,
}: BaseFieldProps & {
  value: string;
  onChange: (value: string) => void;
  rows?: number;
  maxLength?: number;
}) {
  const id = useId();
  const helpId = `${id}-help`;
  const errorId = `${id}-error`;
  return (
    <FieldWrapper
      label={label}
      htmlFor={id}
      required={required}
      error={error}
      help={help}
      helpId={helpId}
      errorId={errorId}
      className={className}
    >
      <textarea
        id={id}
        name={name}
        rows={rows}
        value={value}
        maxLength={maxLength}
        aria-required={required || undefined}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(help, error, helpId, errorId)}
        onChange={(event) => onChange(event.target.value)}
        className="field-input"
      />
    </FieldWrapper>
  );
}

export function SelectField({
  label,
  name,
  required,
  error,
  help,
  className,
  value,
  onChange,
  options,
}: BaseFieldProps & {
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
}) {
  const id = useId();
  const helpId = `${id}-help`;
  const errorId = `${id}-error`;
  return (
    <FieldWrapper
      label={label}
      htmlFor={id}
      required={required}
      error={error}
      help={help}
      helpId={helpId}
      errorId={errorId}
      className={className}
    >
      <select
        id={id}
        name={name}
        value={value}
        aria-required={required || undefined}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(help, error, helpId, errorId)}
        onChange={(event) => onChange(event.target.value)}
        className="field-input"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </FieldWrapper>
  );
}

export function RadioGroupField({
  label,
  name,
  required,
  error,
  value,
  onChange,
  options,
}: BaseFieldProps & {
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
}) {
  const id = useId();
  const errorId = `${id}-error`;
  return (
    <fieldset
      aria-required={required || undefined}
      aria-invalid={error ? true : undefined}
      aria-describedby={error ? errorId : undefined}
    >
      <legend className="text-sm font-semibold text-ink-primary">
        {label}
        {required ? (
          <span className="text-status-danger" aria-hidden="true">
            {" *"}
          </span>
        ) : null}
      </legend>
      <div className="mt-2 flex flex-wrap gap-2">
        {options.map((option) => (
          <label
            key={option.value}
            className={[
              "touch-target cursor-pointer gap-2 rounded-md border px-4 text-base",
              value === option.value
                ? "border-primary-500 bg-primary-50 font-semibold text-primary-700"
                : "border-surface-border bg-surface-bg",
            ].join(" ")}
          >
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              className="h-5 w-5"
            />
            {option.label}
          </label>
        ))}
      </div>
      {error ? (
        <p id={errorId} role="alert" className="mt-1 text-sm font-medium text-status-danger">
          {error}
        </p>
      ) : null}
    </fieldset>
  );
}

/** Multi-select toggle group — same visual language as RadioGroupField. */
export function CheckboxGroupField({
  label,
  name,
  required,
  error,
  help,
  value,
  onChange,
  options,
}: BaseFieldProps & {
  value: string[];
  onChange: (value: string[]) => void;
  options: { value: string; label: string }[];
}) {
  const id = useId();
  const helpId = `${id}-help`;
  const errorId = `${id}-error`;

  function toggle(optionValue: string) {
    onChange(
      value.includes(optionValue)
        ? value.filter((v) => v !== optionValue)
        : [...value, optionValue],
    );
  }

  return (
    <fieldset
      aria-required={required || undefined}
      aria-invalid={error ? true : undefined}
      aria-describedby={describedBy(help, error, helpId, errorId)}
    >
      <legend className="text-sm font-semibold text-ink-primary">
        {label}
        {required ? (
          <span className="text-status-danger" aria-hidden="true">
            {" *"}
          </span>
        ) : null}
      </legend>
      {help ? (
        <p id={helpId} className="text-xs text-ink-secondary">
          {help}
        </p>
      ) : null}
      <div className="mt-2 flex flex-wrap gap-2">
        {options.map((option) => {
          const checked = value.includes(option.value);
          return (
            <label
              key={option.value}
              className={[
                "touch-target cursor-pointer gap-2 rounded-md border px-4 text-base",
                checked
                  ? "border-primary-500 bg-primary-50 font-semibold text-primary-700"
                  : "border-surface-border bg-surface-bg",
              ].join(" ")}
            >
              <input
                type="checkbox"
                name={name}
                value={option.value}
                checked={checked}
                onChange={() => toggle(option.value)}
                className="h-5 w-5"
              />
              {option.label}
            </label>
          );
        })}
      </div>
      {error ? (
        <p id={errorId} role="alert" className="mt-1 text-sm font-medium text-status-danger">
          {error}
        </p>
      ) : null}
    </fieldset>
  );
}

/** ConsentCheckbox — explicit, required-checked control (PRD §15 / §31). */
export function ConsentCheckbox({
  label,
  name,
  checked,
  onChange,
  error,
}: {
  label: string;
  name: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  error?: string;
}) {
  const id = useId();
  const errorId = `${id}-error`;
  return (
    <div className="rounded-md border border-surface-border bg-surface-subtle p-3">
      <label htmlFor={id} className="flex min-h-touch cursor-pointer items-start gap-3">
        <input
          id={id}
          name={name}
          type="checkbox"
          checked={checked}
          aria-required="true"
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? errorId : undefined}
          onChange={(event) => onChange(event.target.checked)}
          className="mt-0.5 h-6 w-6 flex-shrink-0"
        />
        <span className="text-sm text-ink-primary">{label}</span>
      </label>
      {error ? (
        <p id={errorId} role="alert" className="mt-1 text-sm font-medium text-status-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function FormErrorSummary({
  title,
  messages,
}: {
  title: string;
  messages: string[];
}) {
  if (messages.length === 0) return null;
  return (
    <div role="alert" className="rounded-md border border-red-200 bg-red-50 p-4">
      <p className="font-semibold text-status-danger">{title}</p>
      <ul className="mt-1 list-inside list-disc text-sm text-ink-primary">
        {messages.map((message) => (
          <li key={message}>{message}</li>
        ))}
      </ul>
    </div>
  );
}
