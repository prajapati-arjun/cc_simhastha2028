import type { LayerKey } from "./LayerTogglePanel";

/** A single plottable point, normalised from temples / ghats / emergency rows. */
export interface MapFeature {
  /** Deep-link id, e.g. "temple:mahakaleshwar" — matches ?focus=. */
  key: string;
  layer: LayerKey;
  name: string;
  latitude: number;
  longitude: number;
  /** Route to the detail page, when one exists. */
  href?: string;
  meta?: string;
}
