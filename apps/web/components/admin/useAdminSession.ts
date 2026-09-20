"use client";

import { useEffect, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { clearSession, isAdminRole, readSession, type AdminSession } from "@/lib/adminAuth";

export type AdminSessionState =
  | { status: "loading" }
  | { status: "anonymous" }
  | { status: "authenticated"; session: AdminSession };

/**
 * Reads the stored admin session on mount and redirects unauthenticated or
 * non-admin visitors to /admin/login. Frontend gating is a convenience —
 * the backend enforces RBAC on every admin endpoint.
 */
export function useAdminSession(options: { redirect?: boolean } = {}) {
  const { redirect = true } = options;
  const router = useRouter();
  const [state, setState] = useState<AdminSessionState>({ status: "loading" });

  useEffect(() => {
    const session = readSession();
    if (!session || !isAdminRole(session.user.role)) {
      if (session) clearSession();
      setState({ status: "anonymous" });
      if (redirect) router.replace("/admin/login");
      return;
    }
    setState({ status: "authenticated", session });
  }, [redirect, router]);

  return state;
}
