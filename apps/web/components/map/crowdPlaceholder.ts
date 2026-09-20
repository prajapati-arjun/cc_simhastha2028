import type { MapFeature } from "./types";

/**
 * STATIC SAMPLE DATA — not a feed, not a measurement, not a forecast.
 *
 * No crowd or traffic API exists in Sprint 1 (API_CONTRACT.md §9 omits them
 * deliberately). These four points exist only to demonstrate the layer-toggle
 * pattern, and the layer cannot be shown without SafetyBanner
 * variant="crowd-placeholder" rendering above the map.
 */
export const CROWD_PLACEHOLDER_FEATURES: MapFeature[] = [
  {
    key: "crowd:sample-a",
    layer: "crowd",
    name: "Sample zone A",
    latitude: 23.1826,
    longitude: 75.7669,
    meta: "Sample data — low",
  },
  {
    key: "crowd:sample-b",
    layer: "crowd",
    name: "Sample zone B",
    latitude: 23.1864,
    longitude: 75.7712,
    meta: "Sample data — moderate",
  },
  {
    key: "crowd:sample-c",
    layer: "crowd",
    name: "Sample zone C",
    latitude: 23.1788,
    longitude: 75.7738,
    meta: "Sample data — high",
  },
  {
    key: "crowd:sample-d",
    layer: "crowd",
    name: "Sample zone D",
    latitude: 23.1902,
    longitude: 75.7655,
    meta: "Sample data — critical",
  },
];
