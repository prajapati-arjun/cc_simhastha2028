"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

/**
 * LayerTogglePanel — UX_PAGE_ARCHITECTURE.md §4.
 * Desktop: always-visible floating card. Mobile: bottom-sheet behind a "Layers"
 * pill. Each row is a real switch (role="switch" + aria-checked), 44px minimum,
 * keyboard operable. Layer state is session-only component state by design.
 */

export type LayerKey = "temples" | "ghats" | "emergency" | "crowd";

export const LAYER_ORDER: LayerKey[] = ["temples", "ghats", "emergency", "crowd"];

export const LAYER_COLOR: Record<LayerKey, string> = {
  temples: "#2f4fb0",
  ghats: "#5c7fd0",
  emergency: "#c62828",
  crowd: "#c99a00",
};

/** Distinct SHAPE as well as colour, for colour-vision-deficient users (§4). */
export const LAYER_SHAPE: Record<LayerKey, string> = {
  temples: "circle",
  ghats: "square",
  emergency: "diamond",
  crowd: "triangle",
};

const LABEL_KEY: Record<LayerKey, string> = {
  temples: "layerTemples",
  ghats: "layerGhats",
  emergency: "layerEmergency",
  crowd: "layerCrowd",
};

function LayerToggle({
  layer,
  checked,
  onChange,
  label,
}: {
  layer: LayerKey;
  checked: boolean;
  onChange: (next: boolean) => void;
  label: string;
}) {
  return (
    <li>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className="flex min-h-touch w-full items-center gap-3 rounded-md px-2 text-left text-sm font-medium hover:bg-surface-subtle"
      >
        <span
          aria-hidden="true"
          className="h-3.5 w-3.5 flex-shrink-0"
          style={{
            backgroundColor: LAYER_COLOR[layer],
            borderRadius: LAYER_SHAPE[layer] === "circle" ? "9999px" : "2px",
            transform:
              LAYER_SHAPE[layer] === "diamond" ? "rotate(45deg)" : undefined,
            clipPath:
              LAYER_SHAPE[layer] === "triangle"
                ? "polygon(50% 0%, 100% 100%, 0% 100%)"
                : undefined,
          }}
        />
        <span className="flex-1">{label}</span>
        <span
          aria-hidden="true"
          className={[
            "flex h-6 w-11 flex-shrink-0 items-center rounded-full p-0.5 transition-colors",
            checked ? "bg-primary-500" : "bg-surface-border",
          ].join(" ")}
        >
          <span
            className={[
              "h-5 w-5 rounded-full bg-white transition-transform",
              checked ? "translate-x-5" : "translate-x-0",
            ].join(" ")}
          />
        </span>
      </button>
    </li>
  );
}

export function LayerTogglePanel({
  layers,
  onToggle,
}: {
  layers: Record<LayerKey, boolean>;
  onToggle: (layer: LayerKey, next: boolean) => void;
}) {
  const t = useTranslations("map");
  const [sheetOpen, setSheetOpen] = useState(false);

  const list = (
    <ul className="flex flex-col gap-1">
      {LAYER_ORDER.map((layer) => (
        <LayerToggle
          key={layer}
          layer={layer}
          checked={layers[layer]}
          label={t(LABEL_KEY[layer])}
          onChange={(next) => onToggle(layer, next)}
        />
      ))}
    </ul>
  );

  return (
    <>
      <section
        aria-label={t("layers")}
        className="pointer-events-auto absolute left-4 top-4 z-20 hidden w-56 rounded-lg bg-surface-bg p-3 shadow-raised md:block"
      >
        <h2 className="mb-2 text-sm font-bold uppercase tracking-wide text-ink-secondary">
          {t("layers")}
        </h2>
        {list}
      </section>

      <div className="pointer-events-auto absolute bottom-4 right-4 z-20 md:hidden">
        {sheetOpen ? (
          <section
            aria-label={t("layers")}
            className="mb-2 w-60 rounded-lg bg-surface-bg p-3 shadow-raised"
          >
            {list}
          </section>
        ) : null}
        <button
          type="button"
          className="btn-primary w-full rounded-full shadow-raised"
          aria-expanded={sheetOpen}
          onClick={() => setSheetOpen((open) => !open)}
        >
          {sheetOpen ? t("layersClose") : t("layers")}
        </button>
      </div>
    </>
  );
}

export default LayerTogglePanel;
