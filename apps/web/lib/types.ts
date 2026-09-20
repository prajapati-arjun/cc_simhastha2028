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

export type AdminEntityKey = "events" | "announcements" | "temples" | "ghats";

/** Admin list rows are the public shapes plus drafts, so they reuse the types above. */
export type AdminRecord = EventItem | Announcement | Temple | Ghat;
