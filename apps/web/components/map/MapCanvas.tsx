"use client";

import maplibregl, { type Map as MapLibreMap, type Marker } from "maplibre-gl";
import { useTranslations } from "next-intl";
import { useEffect, useRef } from "react";
import "maplibre-gl/dist/maplibre-gl.css";
import { LAYER_COLOR, LAYER_SHAPE, type LayerKey } from "./LayerTogglePanel";
import type { MapFeature } from "./types";

/**
 * MapCanvas — MapLibre GL with FREE OpenStreetMap raster tiles.
 * No paid provider, no API key. OSM attribution is mandatory and is rendered by
 * the built-in AttributionControl from the source definition below.
 */

const UJJAIN_CENTER: [number, number] = [75.7885, 23.1765];

const OSM_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      maxzoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors',
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};

function markerElement(
  feature: MapFeature,
  label: string,
  onSelect: () => void,
) {
  const button = document.createElement("button");
  button.type = "button";
  button.setAttribute("aria-label", label);
  button.style.cssText =
    "width:22px;height:22px;border:2px solid #fff;cursor:pointer;padding:0;" +
    `background:${LAYER_COLOR[feature.layer as LayerKey]};` +
    "box-shadow:0 1px 3px rgba(16,28,64,0.5);";
  const shape = LAYER_SHAPE[feature.layer as LayerKey];
  if (shape === "circle") button.style.borderRadius = "9999px";
  if (shape === "square") button.style.borderRadius = "2px";
  if (shape === "diamond") button.style.transform = "rotate(45deg)";
  if (shape === "triangle") {
    button.style.clipPath = "polygon(50% 0%, 100% 100%, 0% 100%)";
    button.style.border = "none";
  }
  button.addEventListener("click", onSelect);
  return button;
}

export function MapCanvas({
  features,
  focusKey,
  onSelect,
}: {
  features: MapFeature[];
  focusKey?: string;
  onSelect: (feature: MapFeature | null) => void;
}) {
  const t = useTranslations("map");
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Marker[]>([]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: OSM_STYLE,
      center: UJJAIN_CENTER,
      zoom: 12,
      attributionControl: { compact: false },
    });
    map.addControl(new maplibregl.NavigationControl({}), "top-right");
    map.keyboard.enable();
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = features.map((feature) => {
      const element = markerElement(
        feature,
        t("markerAria", { name: feature.name }),
        () => onSelect(feature),
      );
      return new maplibregl.Marker({ element })
        .setLngLat([feature.longitude, feature.latitude])
        .addTo(map);
    });

    return () => {
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current = [];
    };
  }, [features, onSelect, t]);

  // ?focus=temple:{slug} deep-link: centre on the feature and open its card.
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !focusKey) return;
    const target = features.find((feature) => feature.key === focusKey);
    if (!target) return;
    const reduceMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    map.flyTo({
      center: [target.longitude, target.latitude],
      zoom: 15,
      duration: reduceMotion ? 0 : 800,
    });
    onSelect(target);
  }, [focusKey, features, onSelect]);

  return (
    <div
      ref={containerRef}
      role="application"
      aria-label={t("mapLabel")}
      className="h-full w-full"
    />
  );
}

export default MapCanvas;
