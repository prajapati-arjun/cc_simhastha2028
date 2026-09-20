"use client";

import type { AuthUser } from "./types";

/**
 * Admin session storage.
 *
 * Sprint 1 keeps the JWT in localStorage: the contract issues a bearer token
 * (§8) rather than an HttpOnly cookie, and all admin screens are client-rendered.
 * Documented as a prototype limitation — a production build should move this to
 * an HttpOnly, SameSite cookie set by a server route.
 */

const TOKEN_KEY = "simhastha.admin.token";
const USER_KEY = "simhastha.admin.user";

export interface AdminSession {
  token: string;
  user: AuthUser;
}

export function saveSession(session: AdminSession) {
  try {
    window.localStorage.setItem(TOKEN_KEY, session.token);
    window.localStorage.setItem(USER_KEY, JSON.stringify(session.user));
  } catch {
    /* storage unavailable (private mode) — session simply will not persist */
  }
}

export function readSession(): AdminSession | null {
  try {
    const token = window.localStorage.getItem(TOKEN_KEY);
    const rawUser = window.localStorage.getItem(USER_KEY);
    if (!token || !rawUser) return null;
    return { token, user: JSON.parse(rawUser) as AuthUser };
  } catch {
    return null;
  }
}

export function clearSession() {
  try {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(USER_KEY);
  } catch {
    /* ignore */
  }
}

const ADMIN_ROLES = ["super_admin", "content_manager"];

export function isAdminRole(role: string | undefined | null) {
  return !!role && ADMIN_ROLES.includes(role);
}
