"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { postJson } from "@/lib/api";
import { t } from "@/lib/i18n";
import { resolveTargetAfterAuthSession } from "@/lib/authRedirect";
import { beginAuthSession } from "@/lib/authSession";
import { LoadingSpinner } from "@/components/orbit";

type OAuthState = { redirect?: string };

function parseOAuthState(raw: string | null): OAuthState {
  if (!raw) return {};
  try {
    const decoded = decodeURIComponent(raw);
    const data = JSON.parse(decoded) as unknown;
    if (data && typeof data === "object" && "redirect" in data) {
      const redirect = (data as OAuthState).redirect;
      if (typeof redirect === "string" && redirect.startsWith("/") && !redirect.startsWith("//")) {
        return { redirect };
      }
    }
  } catch {
    /* ignore */
  }
  return {};
}

function GoogleOAuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      const errParam = searchParams.get("error");
      const errDesc = searchParams.get("error_description");
      if (errParam) {
        setError(errDesc || errParam);
        return;
      }

      const code = searchParams.get("code");
      if (!code) {
        setError(t("auth.oauth.callback.missingCode", "Не удалось получить код от Google"));
        return;
      }

      const state = parseOAuthState(searchParams.get("state"));
      const nextRaw = state.redirect;

      const redirectUri = `${window.location.origin}/auth/google/callback`;

      try {
        const result = await postJson<{ token: string }>("/oauth/google/code", {
          code,
          redirect_uri: redirectUri,
        });
        if (cancelled) return;
        beginAuthSession(result.token);
        const target = await resolveTargetAfterAuthSession(nextRaw);
        router.replace(target);
      } catch (e) {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : t("auth.oauth.callback.exchangeFailed", "Не удалось завершить вход через Google"));
      }
    };

    void run();
    return () => {
      cancelled = true;
    };
  }, [router, searchParams]);

  if (error) {
    return (
      <main className="orbit-page orbit-auth-page">
        <div
          className="orbit-hero-content-container"
          style={{ maxWidth: "480px", margin: "0 auto", padding: "var(--orbit-space-2xl)", textAlign: "center" }}
        >
          <p className="orbit-body" style={{ color: "var(--orbit-color-coral)" }}>
            {error}
          </p>
          <Link href="/auth?mode=login" className="orbit-button orbit-button-primary" style={{ marginTop: "var(--orbit-space-lg)", display: "inline-block" }}>
            {t("auth.oauth.callback.backToAuth", "Вернуться ко входу")}
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="orbit-page orbit-auth-page">
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "50vh",
          gap: "var(--orbit-space-md)",
        }}
      >
        <LoadingSpinner size="lg" />
        <p className="orbit-body orbit-text-muted">{t("auth.oauth.callback.googleProcessing", "Завершаем вход через Google…")}</p>
      </div>
    </main>
  );
}

export default function GoogleOAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <main className="orbit-page orbit-auth-page">
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "50vh" }}>
            <LoadingSpinner size="lg" />
          </div>
        </main>
      }
    >
      <GoogleOAuthCallbackContent />
    </Suspense>
  );
}
