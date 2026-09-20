"use client";

import type { ReactNode } from "react";
import AdminShell from "@/components/admin/AdminShell";
import { usePathname } from "@/i18n/navigation";

/**
 * Every /admin/* route is gated except the login screen itself.
 * Admin navigation is not rendered at all for non-admin sessions.
 */
export default function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  if (pathname.startsWith("/admin/login")) {
    return <>{children}</>;
  }
  return <AdminShell>{children}</AdminShell>;
}
