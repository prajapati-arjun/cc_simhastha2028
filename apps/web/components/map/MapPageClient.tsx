"use client";

import dynamic from "next/dynamic";
import { useTranslations } from "next-intl";
import { useCallback, useMemo, useState } from "react";
import SafetyBanner from "@/components/SafetyBanner";
import { Link } from "@/i18n/navigation";
import { CROWD_PLACEHOLDER_FEATURES } from "./crowdPlaceholder";
import LayerTogglePanel, { type LayerKey } from "./LayerTogglePanel";
import type { MapFeature } from "./types";

// MapLibre touches `window` on import, so it must never be server-rendered.
const MapCanvas = dynamic(() => import("./MapCanvas"), {
  ssr: false,
  loading: () => <div className="h-full w-full animate-pulse bg-surface-subtle" />,
});

export function MapPageClient({
  features,
  focusKey,
  loadError,
}: {
  features: MapFeature[];
  focusKey?: string;
  loadError?: string | null;
}) {
  const t = useTranslations("map");
  const tc = useTranslations("common");

  const [layers, setLayers] = useState<Record<LayerKey, boolean>>({
    temples: true,
    ghats: true,
    emergency: true,
    // Placeholder layer is OFF by default (UX §4).
    crowd: false,
  });
  const [selected, setSelected] = useState<MapFeature | null>(null);

  const visibleFeatures = useMemo(() => {
    const live = features.filter((feature) => layers[feature.layer]);
    return layers.crowd ? [...live, ...CROWD_PLACEHOLDER_FEATURES] : live;
  }, [features, layers]);

  const handleToggle = useCallback((layer: LayerKey, next: boolean) => {
    setLayers((current) => ({ ...current, [layer]: next }));
    if (!next) setSelected(null);
  }, []);

  const handleSelect = useCallback((feature: MapFeature | null) => {
    setSelected(feature);
  }, []);

  return (
    <div className="container-app py-6">
      <h1>{t("pageTitle")}</h1>
      <p className="mt-2 text-ink-secondary">{t("pageIntro")}</p>

      {/* Banner appears only while the placeholder layer is ON, directly above
          the map panel, and disappears when the layer is toggled off. */}
      {layers.crowd ? (
        <div className="mt-4">
          <SafetyBanner variant="crowd-placeholder" />
        </div>
      ) : null}

      {loadError ? (
        <p role="alert" className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm">
          {t("loadError")} {loadError}
        </p>
      ) : null}

      <div className="relative mt-4 h-[60vh] min-h-[24rem] overflow-hidden rounded-md border border-surface-border">
        <MapCanvas
          features={visibleFeatures}
          focusKey={focusKey}
          onSelect={handleSelect}
        />
        <LayerTogglePanel layers={layers} onToggle={handleToggle} />
      </div>

      <p className="mt-2 text-xs text-ink-secondary">{t("attribution")}</p>

      <div aria-live="polite">
        {selected ? (
          <div className="card-surface mt-4 p-4">
            <h2 className="text-lg font-semibold">{selected.name}</h2>
            {selected.meta ? (
              <p className="mt-1 text-sm text-ink-secondary">{selected.meta}</p>
            ) : null}
            <div className="mt-3 flex flex-wrap gap-3">
              {selected.href ? (
                <Link href={selected.href} className="btn-outline">
                  {t("openDetail")}
                </Link>
              ) : null}
              <button
                type="button"
                className="btn-outline"
                onClick={() => setSelected(null)}
              >
                {tc("cancel")}
              </button>
            </div>
          </div>
        ) : null}
      </div>

      {/* Non-visual fallback: the same points as a keyboard-reachable list, so
          the map is not the only path to this information (§5.6). */}
      <details className="mt-6">
        <summary className="touch-target cursor-pointer justify-start text-sm font-semibold text-primary-700">
          {t("pageIntro")}
        </summary>
        <ul className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {visibleFeatures.map((feature) => (
            <li key={feature.key} className="card-surface p-3">
              <p className="font-medium">{feature.name}</p>
              {feature.href ? (
                <Link href={feature.href} className="link-inline text-sm">
                  {t("openDetail")}
                </Link>
              ) : (
                <p className="text-sm text-ink-secondary">{feature.meta}</p>
              )}
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}

export default MapPageClient;
