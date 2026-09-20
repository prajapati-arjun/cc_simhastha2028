/**
 * StatusBadge — always pairs colour with a text label (never colour alone),
 * per UX_DESIGN_SYSTEM.md §5.8 / UX_PAGE_ARCHITECTURE.md §3.
 */

export type BadgeTone =
  | "neutral"
  | "info"
  | "success"
  | "warning"
  | "danger"
  | "accent";

const TONE_CLASS: Record<BadgeTone, string> = {
  neutral: "bg-surface-subtle text-ink-secondary border-surface-border",
  info: "bg-primary-50 text-primary-700 border-primary-200",
  success: "bg-green-50 text-status-success border-green-200",
  warning: "bg-secondary-50 text-secondary-700 border-secondary-200",
  danger: "bg-red-50 text-status-danger border-red-200",
  accent: "bg-secondary-50 text-secondary-700 border-secondary-300",
};

export interface StatusBadgeProps {
  label: string;
  tone?: BadgeTone;
  className?: string;
}

export function StatusBadge({
  label,
  tone = "neutral",
  className = "",
}: StatusBadgeProps) {
  return (
    <span
      className={[
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
        TONE_CLASS[tone],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {label}
    </span>
  );
}

export default StatusBadge;
