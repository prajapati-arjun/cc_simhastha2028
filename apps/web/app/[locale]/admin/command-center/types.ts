import type { CrowdBandLevel } from "@/components/CrowdBandBadge";

/**
 * Local mirror of GET /api/v1/command-center/overview (PRD section 24).
 *
 * These types belong conceptually in apps/web/lib/types.ts alongside the
 * rest of the contract mirrors, but that file is being edited concurrently
 * by other agents this sprint, so they are declared locally here instead.
 * See this feature's owning agent's final report for the exact block to
 * add to lib/types.ts during integration.
 */

export interface CommandCenterCrowdReading {
  id: number;
  zone_id: number;
  density_level: CrowdBandLevel;
  estimated_count_band: string | null;
  source: string;
  recorded_at: string;
  recorded_by_user_id: number | null;
  created_at: string;
}

export interface CommandCenterZone {
  zone_id: number;
  zone_slug: string;
  zone_name: string;
  zone_type: string | null;
  /** null when no operator has ever recorded a reading for this zone. */
  latest_crowd_reading: CommandCenterCrowdReading | null;
}

export interface CommandCenterCriticalAlert {
  id: number;
  slug: string;
  title: string;
  body: string;
  priority: string;
  published_at: string | null;
  expires_at: string | null;
}

export interface CommandCenterCaseTotals {
  open_sos_incidents: number;
  open_lost_found_cases: number;
  open_missing_person_cases: number;
}

/** Section 1: real rows read from this project's own database. */
export interface CommandCenterObserved {
  zones: CommandCenterZone[];
  case_totals: CommandCenterCaseTotals;
  case_totals_note: string;
  critical_announcements: CommandCenterCriticalAlert[];
}

/** Section 2: model-generated recommendations. Always empty in this prototype. */
export interface CommandCenterRecommendations {
  available: boolean;
  items: string[];
  note: string;
}

export type CommandCenterDecisionEntityType =
  | "sos_incident"
  | "lost_found_case"
  | "missing_person_case";

export interface CommandCenterDecision {
  entity_type: CommandCenterDecisionEntityType;
  case_reference: string;
  status: string;
  updated_at: string;
}

/** Section 3: state an authenticated admin set explicitly. */
export interface CommandCenterHumanDecisions {
  note: string;
  recent_status_decisions: CommandCenterDecision[];
}

export interface CommandCenterOverview {
  generated_at: string;
  prototype_notice: string;
  observed: CommandCenterObserved;
  recommendations: CommandCenterRecommendations;
  human_decisions: CommandCenterHumanDecisions;
}
