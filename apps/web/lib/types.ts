/**
 * TypeScript mirrors of the frozen Sprint 1 API contract.
 * Source of truth: Docs/API_CONTRACT.md. Field names and enum members here are
 * copied verbatim from that document — do not rename them locally. If the API
 * deviates, fix the contract conversation first, then this file.
 */

/** §0 Conventions — every list endpoint returns this envelope. */
export interface ListEnvelope<T> {
  items: T[];
  total: number;
  last_updated: string | null;
}

export type PublicationStatus = "draft" | "published" | "archived";
export type DataSource = "placeholder" | "cms";

/** §1 Events */
export type EventCategory =
  | "snan_parva"
  | "religious"
  | "aarti"
  | "akhada"
  | "cultural"
  | "government";

export interface EventItem {
  id: number;
  slug: string;
  title: string;
  summary: string | null;
  description: string | null;
  category: EventCategory;
  starts_at: string;
  ends_at: string | null;
  venue_name: string | null;
  latitude: number | null;
  longitude: number | null;
  image_url: string | null;
  status: PublicationStatus;
  data_source: DataSource;
  updated_at: string;
}

/** §2 Temples */
export interface Temple {
  id: number;
  slug: string;
  name: string;
  short_description: string | null;
  significance: string | null;
  timings: string | null;
  aarti_schedule: string | null;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  transport_info: string | null;
  accessibility_info: string | null;
  image_url: string | null;
  status: PublicationStatus;
  verified: boolean;
  data_source: DataSource;
  updated_at: string;
}

/** §3 Ghats */
export interface Ghat {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  bathing_info: string | null;
  facilities: string[];
  accessibility_info: string | null;
  latitude: number | null;
  longitude: number | null;
  image_url: string | null;
  status: PublicationStatus;
  data_source: DataSource;
  updated_at: string;
}

export type GhatOperationalStatus = "open" | "restricted" | "closed";

export interface GhatStatus {
  ghat_id: number;
  slug: string;
  name: string;
  status: GhatOperationalStatus;
  /**
   * ALWAYS null in Sprint 1 — no crowd data source exists.
   * Render "Crowd level: not available"; never a fabricated density badge.
   */
  crowd_level: null;
  advisory: string | null;
  data_source: DataSource;
  prototype_notice: string;
  updated_at: string;
}

/** §4 Emergency */
export type EmergencyCategory =
  | "police"
  | "ambulance"
  | "fire"
  | "medical"
  | "women_child"
  | "disaster_mgmt"
  | "help_center";

export interface EmergencyService {
  id: number;
  name: string;
  category: EmergencyCategory;
  phone: string;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  hours: string | null;
  notes: string | null;
  data_source: DataSource;
  prototype_notice: string;
  updated_at: string;
}

export type SosSituationCategory =
  | "medical"
  | "security"
  | "fire"
  | "lost_person"
  | "other";

export interface SosRequest {
  reporter_name?: string | null;
  reporter_phone?: string | null;
  situation_category: SosSituationCategory;
  note?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  consent_given: boolean;
}

export interface SosResponse {
  case_reference: string;
  status: string;
  simulated: true;
  created_at: string;
  prototype_notice: string;
}

/** §5 Lost & Found */
export type LostFoundReportType = "lost" | "found";
export type LostFoundCategory =
  | "bag"
  | "documents"
  | "phone"
  | "jewellery"
  | "child_item"
  | "other";
export type LostFoundStatus =
  | "submitted"
  | "under_review"
  | "verified"
  | "matched"
  | "closed"
  | "rejected";

export interface LostFoundRequest {
  report_type: LostFoundReportType;
  category: LostFoundCategory;
  description: string;
  location_text?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  occurred_at: string;
  reporter_name: string;
  reporter_phone: string;
  image_url?: string | null;
}

export interface CaseSubmissionResponse {
  case_reference: string;
  status: string;
  created_at: string;
  prototype_notice: string;
}

export interface LostFoundCase {
  case_reference: string;
  report_type: LostFoundReportType;
  category: LostFoundCategory;
  status: LostFoundStatus;
  created_at: string;
  updated_at: string;
  prototype_notice: string;
}

/** §6 Missing person */
export type MissingPersonStatus =
  | "submitted"
  | "under_review"
  | "verified"
  | "resolved"
  | "closed";

export interface MissingPersonRequest {
  person_name: string;
  person_age?: number | null;
  person_gender?: string | null;
  physical_description?: string | null;
  last_seen_location_text?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  last_seen_at: string;
  photo_url?: string | null;
  reporter_name: string;
  reporter_phone: string;
  reporter_relationship?: string | null;
  consent_given: boolean;
}

/**
 * Status + timestamps ONLY (decision D-01). The contract forbids the API from
 * echoing person_name, age, description, photo, reporter details or location,
 * so there is deliberately nothing else to render here.
 */
export interface MissingPersonCase {
  case_reference: string;
  status: MissingPersonStatus;
  created_at: string;
  updated_at: string;
  prototype_notice: string;
}

/** §7 Announcements */
export type AnnouncementPriority = "normal" | "important" | "critical";

export interface Announcement {
  id: number;
  slug: string;
  title: string;
  body: string | null;
  priority: AnnouncementPriority;
  published_at: string | null;
  expires_at: string | null;
  status: PublicationStatus;
  data_source: DataSource;
  updated_at: string;
}

/** §8 Auth & admin */
export interface AuthUser {
  id: number;
  username: string;
  full_name: string | null;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

export type AdminEntityKey =
  | "events"
  | "announcements"
  | "temples"
  | "ghats"
  | "parking"
  | "accommodation"
  | "essential_services";

/** Admin list rows are the public shapes plus drafts, so they reuse the types above. */
export type AdminRecord =
  | EventItem
  | Announcement
  | Temple
  | Ghat
  | ParkingFacility
  | Accommodation
  | EssentialService;

/** §10 Pilgrimage Planner (Sprint 2 addendum) */
export type TransportMode = "car" | "bus" | "train" | "walking" | "other";
export type AccommodationPreference =
  | "budget"
  | "mid_range"
  | "premium"
  | "dharamshala"
  | "not_needed";
export type AgeGroup = "infant" | "child" | "adult" | "senior";
export type PilgrimInterest =
  | "spiritual"
  | "cultural"
  | "historical"
  | "family_friendly"
  | "photography";
export type AccessibilityRequirement =
  | "wheelchair"
  | "visual_impairment"
  | "hearing_impairment"
  | "elderly_mobility";

export interface PlannerRequest {
  arrival_date: string;
  departure_date: string;
  party_size: number;
  age_groups: AgeGroup[];
  transport_mode: TransportMode;
  accommodation_preference: AccommodationPreference;
  interests: PilgrimInterest[];
  accessibility_requirements: AccessibilityRequirement[];
}

export interface PlannerTempleSummary {
  id: number;
  slug: string;
  name: string;
  short_description: string | null;
}

export interface PlannerGhatSummary {
  id: number;
  slug: string;
  name: string;
}

export interface PlannerEventSummary {
  id: number;
  slug: string;
  title: string;
  category: EventCategory;
  starts_at: string;
  venue_name: string | null;
}

export interface PlannerDay {
  date: string;
  day_number: number;
  temples: PlannerTempleSummary[];
  ghats: PlannerGhatSummary[];
  events: PlannerEventSummary[];
  rest_period: boolean;
}

/** Stateless — nothing here is persisted, so there is no reference/id to save. */
export interface PlannerResponse {
  arrival_date: string;
  departure_date: string;
  party_size: number;
  age_groups: AgeGroup[];
  transport_mode: TransportMode;
  accommodation_preference: AccommodationPreference;
  interests: PilgrimInterest[];
  accessibility_requirements: AccessibilityRequirement[];
  days: PlannerDay[];
  unscheduled_temples: PlannerTempleSummary[];
  unscheduled_ghats: PlannerGhatSummary[];
  transport_note: string;
  accommodation_note: string;
  accessibility_note: string | null;
  interest_note: string | null;
  data_source: "generated";
  prototype_notice: string;
  generated_at: string;
}

/** §11 Parking (PRD §12, roadmap 2.3) */
export type ParkingType = "bus" | "two_wheeler" | "four_wheeler" | "accessible";

export interface ParkingFacility {
  id: number;
  slug: string;
  name: string;
  parking_type: ParkingType;
  capacity: number | null;
  current_occupancy: number | null;
  occupancy_updated_at: string | null;
  entry_info: string | null;
  exit_info: string | null;
  shuttle_note: string | null;
  latitude: number | null;
  longitude: number | null;
  zone_id: number | null;
  status: PublicationStatus;
  data_source: DataSource;
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
  data_source: DataSource;
  prototype_notice: string;
  updated_at: string;
}

/** §12 Accommodation & essential services (PRD §17, roadmap 2.5) */
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
  verified: boolean;
  status: PublicationStatus;
  data_source: DataSource;
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
  status: PublicationStatus;
  data_source: DataSource;
  updated_at: string;
}

/** §13 Crowd Analytics (PRD §10/§26) */
export type CrowdDensityLevel = "green" | "yellow" | "orange" | "red";
export type CrowdEstimatedCountBand =
  | "under_500"
  | "500_to_2000"
  | "2000_to_10000"
  | "over_10000";
export type CrowdReadingSource = "operator_entered" | "manual_estimate";

export interface CrowdReading {
  id: number;
  zone_id: number;
  density_level: CrowdDensityLevel;
  estimated_count_band: CrowdEstimatedCountBand | null;
  source: CrowdReadingSource;
  recorded_at: string;
  recorded_by_user_id: number | null;
  created_at: string;
}

export interface CrowdZoneSummary {
  zone_id: number;
  zone_slug: string;
  zone_name: string;
  zone_type: string | null;
  latest_reading: CrowdReading | null;
  prototype_notice: string;
}

export interface CrowdZoneDetail extends CrowdZoneSummary {
  history: CrowdReading[];
}

export interface CrowdReadingRequest {
  density_level: CrowdDensityLevel;
  estimated_count_band?: CrowdEstimatedCountBand | null;
  source: CrowdReadingSource;
  recorded_at?: string | null;
}

export interface CrowdReadingCreatedResponse {
  reading: CrowdReading;
  prototype_notice: string;
}

/** §14 Command Center (PRD §24) */
export interface CommandCenterZone {
  zone_id: number;
  zone_slug: string;
  zone_name: string;
  zone_type: string | null;
  latest_crowd_reading: CrowdReading | null;
}

export interface CommandCenterCriticalAlert {
  id: number;
  slug: string;
  title: string;
  body: string;
  priority: AnnouncementPriority;
  published_at: string | null;
  expires_at: string | null;
}

export interface CommandCenterCaseTotals {
  open_sos_incidents: number;
  open_lost_found_cases: number;
  open_missing_person_cases: number;
}

export interface CommandCenterObserved {
  zones: CommandCenterZone[];
  case_totals: CommandCenterCaseTotals;
  case_totals_note: string;
  critical_announcements: CommandCenterCriticalAlert[];
}

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

/** §15 Lost & Found matching (PRD §16) — admin-only views */
export interface LostFoundAdminCase {
  id: number;
  case_reference: string;
  report_type: LostFoundReportType;
  category: LostFoundCategory;
  description: string;
  location_text: string | null;
  latitude: number | null;
  longitude: number | null;
  occurred_at: string | null;
  image_url: string | null;
  reporter_name: string | null;
  reporter_phone: string;
  status: LostFoundStatus;
  admin_notes: string | null;
  matched_case_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface LostFoundCandidateMatch {
  id: number;
  case_reference: string;
  report_type: LostFoundReportType;
  category: LostFoundCategory;
  status: LostFoundStatus;
  score: number;
  reasons: string[];
  created_at: string;
}
