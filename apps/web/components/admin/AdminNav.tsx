"use client";

import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { clearSession } from "@/lib/adminAuth";
import { ADMIN_ENTITY_KEYS, ADMIN_ENTITIES } from "./adminEntities";
import type { AuthUser } from "@/lib/types";

/** Admin chrome. Rendered only for an authenticated admin session. */
export function AdminNav({ user }: { user: AuthUser }) {
  const t = useTranslations("admin");
  const router = useRouter();

  return (
    <div className="border-b border-surface-border bg-surface-subtle">
      <div className="container-app flex flex-wrap items-center justify-between gap-3 py-3">
        <nav aria-label="Admin" className="flex flex-wrap items-center gap-1">
          <Link href="/admin" className="touch-target rounded-md px-3 text-sm font-semibold text-primary-700">
            {t("dashboard")}
          </Link>
          <Link href="/admin/command-center" className="touch-target rounded-md px-3 text-sm font-medium text-ink-primary hover:bg-surface-bg">
            {t("commandCenterNav")}
          </Link>
          <Link href="/admin/lost-found" className="touch-target rounded-md px-3 text-sm font-medium text-ink-primary hover:bg-surface-bg">
            {t("lostFoundQueueTitle")}
          </Link>
          {ADMIN_ENTITY_KEYS.map((key) => (
            <Link
              key={key}
              href={`/admin/${ADMIN_ENTITIES[key].path}`}
              className="touch-target rounded-md px-3 text-sm font-medium text-ink-primary hover:bg-surface-bg"
            >
              {t(ADMIN_ENTITIES[key].labelKey)}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <span className="text-sm text-ink-secondary">
            {t("signedInAs", {
              name: user.full_name || user.username,
              role: user.role,
            })}
          </span>
          <button
            type="button"
            className="btn-outline text-sm"
            onClick={() => {
              clearSession();
              router.replace("/admin/login");
            }}
          >
            {t("signOut")}
          </button>
        </div>
      </div>
    </div>
  );
}

export default AdminNav;
