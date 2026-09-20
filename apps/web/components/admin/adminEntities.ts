import type { AdminEntityKey } from "@/lib/types";

/**
 * Field configuration for the four CMS entities (UX_PAGE_ARCHITECTURE.md §2.9).
 * Field names match API_CONTRACT.md item shapes exactly.
 */

export type AdminFieldType =
  | "text"
  | "textarea"
  | "select"
  | "datetime"
  | "number"
  | "url"
  | "csv";

export interface AdminField {
  name: string;
  labelKey?: string;
  label: string;
  type: AdminFieldType;
  required?: boolean;
  options?: string[];
}

export interface AdminEntityConfig {
  key: AdminEntityKey;
  /** API path segment under /api/v1/admin/ */
  path: string;
  /** Which field carries the display name in list rows. */
  titleField: "title" | "name";
  labelKey: string;
  fields: AdminField[];
}

export const ADMIN_ENTITIES: Record<AdminEntityKey, AdminEntityConfig> = {
  events: {
    key: "events",
    path: "events",
    titleField: "title",
    labelKey: "entityEvents",
    fields: [
      { name: "title", label: "Title", type: "text", required: true },
      { name: "slug", label: "Slug", type: "text", required: true },
      { name: "summary", label: "Summary", type: "textarea" },
      { name: "description", label: "Description", type: "textarea" },
      {
        name: "category",
        label: "Category",
        type: "select",
        required: true,
        options: [
          "snan_parva",
          "religious",
          "aarti",
          "akhada",
          "cultural",
          "government",
        ],
      },
      { name: "starts_at", label: "Starts at", type: "datetime", required: true },
      { name: "ends_at", label: "Ends at", type: "datetime" },
      { name: "venue_name", label: "Venue", type: "text" },
      { name: "latitude", label: "Latitude", type: "number" },
      { name: "longitude", label: "Longitude", type: "number" },
      { name: "image_url", label: "Image URL", type: "url" },
    ],
  },
  announcements: {
    key: "announcements",
    path: "announcements",
    titleField: "title",
    labelKey: "entityAnnouncements",
    fields: [
      { name: "title", label: "Title", type: "text", required: true },
      { name: "slug", label: "Slug", type: "text", required: true },
      { name: "body", label: "Body", type: "textarea", required: true },
      {
        name: "priority",
        label: "Priority",
        type: "select",
        required: true,
        options: ["normal", "important", "critical"],
      },
      { name: "published_at", label: "Published at", type: "datetime" },
      { name: "expires_at", label: "Expires at", type: "datetime" },
    ],
  },
  temples: {
    key: "temples",
    path: "temples",
    titleField: "name",
    labelKey: "entityTemples",
    fields: [
      { name: "name", label: "Name", type: "text", required: true },
      { name: "slug", label: "Slug", type: "text", required: true },
      { name: "short_description", label: "Short description", type: "textarea" },
      { name: "significance", label: "Significance", type: "textarea" },
      { name: "timings", label: "Timings", type: "text" },
      { name: "aarti_schedule", label: "Aarti schedule", type: "text" },
      { name: "address", label: "Address", type: "text" },
      { name: "latitude", label: "Latitude", type: "number" },
      { name: "longitude", label: "Longitude", type: "number" },
      { name: "transport_info", label: "Transport info", type: "textarea" },
      {
        name: "accessibility_info",
        label: "Accessibility info",
        type: "textarea",
      },
      { name: "image_url", label: "Image URL", type: "url" },
    ],
  },
  ghats: {
    key: "ghats",
    path: "ghats",
    titleField: "name",
    labelKey: "entityGhats",
    fields: [
      { name: "name", label: "Name", type: "text", required: true },
      { name: "slug", label: "Slug", type: "text", required: true },
      { name: "description", label: "Description", type: "textarea" },
      { name: "bathing_info", label: "Bathing info", type: "textarea" },
      {
        name: "facilities",
        label: "Facilities (comma separated)",
        type: "csv",
      },
      {
        name: "accessibility_info",
        label: "Accessibility info",
        type: "textarea",
      },
      { name: "latitude", label: "Latitude", type: "number" },
      { name: "longitude", label: "Longitude", type: "number" },
      { name: "image_url", label: "Image URL", type: "url" },
    ],
  },
};

export const ADMIN_ENTITY_KEYS: AdminEntityKey[] = [
  "events",
  "announcements",
  "temples",
  "ghats",
];
