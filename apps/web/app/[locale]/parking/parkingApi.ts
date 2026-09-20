import { apiRequest, type ApiResult } from "@/lib/api";
import type { ListEnvelope } from "@/lib/types";

/**
 * Typed client for the Parking API (PRD section 12, roadmap item 2.3).
 *
 * Co-located here rather than in `lib/api.ts` / `lib/types.ts` because both
 * of those are protected files during this sprint's parallel build (three
 * other agents editing the same working directory at once). The functions
 * below follow that module's exact shape (`ApiResult<T>`, `apiRequest`
 * timeout/error handling) so they can be pasted verbatim into `lib/api.ts`
 * later - see this agent's handoff report.
 */

export type ParkingType = "bus" | "two_wheeler" | "four_wheeler" | "accessible";

export interface ParkingFacility {
  id: number;
  slug: string;
  name: string;
  parking_type: ParkingType;
  capacity: number | null;
  /** Operator-entered, never a live sensor/camera reading - see occupancy_updated_at. */
  current_occupancy: number | null;
  occupancy_updated_at: string | null;
  entry_info: string | null;
  exit_info: string | null;
  shuttle_note: string | null;
  latitude: number | null;
  longitude: number | null;
  zone_id: number | null;
  status: "draft" | "published" | "archived";
  data_source: "placeholder" | "cms";
  updated_at: string;
}

export interface ParkingAvailability {
  parking_id: number;
  slug: string;
  name: string;
  parking_type: ParkingType;
  capacity: number | null;
  current_occupancy: number | null;
  occupancy_updated_at: string | null;
  data_source: "placeholder" | "cms";
  prototype_notice: string;
  updated_at: string;
}

export function getParkingList(params?: {
  parking_type?: ParkingType;
  limit?: number;
  offset?: number;
}): Promise<ApiResult<ListEnvelope<ParkingFacility>>> {
  return apiRequest("/api/v1/parking", { params });
}

/** `{id}` accepts a numeric id or a slug, matching the ghats status convention. */
export function getParkingAvailability(
  idOrSlug: string | number,
): Promise<ApiResult<ParkingAvailability>> {
  return apiRequest(
    `/api/v1/parking/${encodeURIComponent(String(idOrSlug))}/availability`,
  );
}
