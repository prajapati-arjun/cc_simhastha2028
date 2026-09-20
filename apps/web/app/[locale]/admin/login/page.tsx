"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import { TextField } from "@/components/form/Fields";
import { useRouter } from "@/i18n/navigation";
import { apiRequest } from "@/lib/api";
import { isAdminRole, saveSession } from "@/lib/adminAuth";
import type { LoginResponse } from "@/lib/types";

export default function AdminLoginPage() {
  const t = useTranslations("admin");
  const tc = useTranslations("common");
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    const response = await apiRequest<LoginResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    setSubmitting(false);

    if (!response.ok) {
      setError(t("loginFailed"));
      return;
    }
    if (!isAdminRole(response.data.user.role)) {
      setError(t("loginFailed"));
      return;
    }
    saveSession({ token: response.data.access_token, user: response.data.user });
    router.replace("/admin");
  }

  return (
    <div className="container-app section-y">
      <div className="mx-auto w-full max-w-md card-surface p-6">
        <h1 className="text-2xl font-bold">{t("loginTitle")}</h1>
        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5" noValidate>
          {error ? (
            <p role="alert" className="rounded-md border border-red-200 bg-red-50 p-3 text-sm font-medium text-status-danger">
              {error}
            </p>
          ) : null}
          <TextField
            label={t("username")}
            name="username"
            required
            value={username}
            onChange={setUsername}
          />
          <TextField
            label={t("password")}
            name="password"
            type="password"
            required
            value={password}
            onChange={setPassword}
          />
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? tc("submitting") : t("signIn")}
          </button>
        </form>
      </div>
    </div>
  );
}
