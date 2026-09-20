import { apiRequest, type ApiResult } from "@/lib/api";
import type { ListEnvelope } from "@/lib/types";

/**
 * Typed client for the Accommodation & Essential Services API
 * (PRD section 17, roadmap item 2.5).
 *
 * Co-located here rather than in `lib/api.ts` / `lib/types.ts` because both
 * of those are protected files during this sprint's parallel build. Follows
 * that module's exact shape so it can be pasted verbatim later - see this
 * agent's handoff report.
 */

export type AccommodationType =
  | "hotel"
  | "dharamshala"
  | "ashram"
  | "tent_camp"
  | "government";

export type AccommodationPriceTier = "budget" | "mid_range" | "premium";

export type EssentialServiceCategory =
  | "food_service"
  | "bhandara"
  | "drinking_water"
  | "toilet"
  | "changing_facility";

export interface Accommodation {
  id: number;
  slug: string;
  name: string;
  accommodation_type: AccommodationType;
  price_tier: AccommodationPriceTier | null;
  address: string | null;
  contact_name: string | null;
  contact_phone: string | null;
  description: string | null;
  latitude: number | null;
  longitude: number | null;
  zone_id: number | null;
  /** PRD section 17: distinguishes officially verified entries from third-party/commercial ones. */
  verified: boolean;
  status: "draft" | "published" | "archived";
  data_source: "placeholder" | "cms";
  updated_at: string;
}

export interface EssentialService {
  id: number;
  slug: string;
  name: string;
  category: EssentialServiceCategory;
  notes: string | null;
  latitude: number | null;
  longitude: number | null;
  zone_id: number | null;
  verified: boolean;
  status: "draft" | "published" | "archived";
  data_source: "placeholder" | "cms";
  updated_at: string;
}

export function getAccommodationList(params?: {
  accommodation_type?: AccommodationType;
  verified?: boolean;
  limit?: number;
  offset?: number;
}): Promise<ApiResult<ListEnvelope<Accommodation>>> {
  return apiRequest("/api/v1/accommodation", {
    params: params && { ...params, verified: params.verified ? "true" : undefined },
  });
}

export function getEssentialServiceList(params?: {
  category?: EssentialServiceCategory;
  limit?: number;
  offset?: number;
}): Promise<ApiResult<ListEnvelope<EssentialService>>> {
  return apiRequest("/api/v1/accommodation/services", { params });
}
