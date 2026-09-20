"use client";

import { useTranslations } from "next-intl";
import type { ReactNode } from "react";
import AdminNav from "./AdminNav";
import { useAdminSession } from "./useAdminSession";

/**
 * Gate for every /admin route except the login screen.
 * Unauthenticated or non-admin sessions are redirected to /admin/login and the
 * admin navigation is never rendered for them.
 */
export function AdminShell({ children }: { children: ReactNode }) {
  const t = useTranslations("admin");
  const tc = useTranslations("common");
  const state = useAdminSession();

  if (state.status === "loading") {
    return (
      <div className="container-app section-y" role="status" aria-live="polite">
        {tc("loading")}
      </div>
    );
  }

  if (state.status === "anonymous") {
    return (
      <div className="container-app section-y">
        <p>{t("requiresAuth")}</p>
      </div>
    );
  }

  return (
    <>
      <AdminNav user={state.session.user} />
      <div className="container-app section-y">{children}</div>
    </>
  );
}

export default AdminShell;
