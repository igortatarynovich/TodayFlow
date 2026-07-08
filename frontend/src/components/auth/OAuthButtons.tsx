"use client";

import { useState, useEffect } from "react";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { LoadingSpinner } from "@/components/orbit";
import { useRouter, useSearchParams } from "next/navigation";
import { getSafeRedirectTarget, resolveTargetAfterAuthSession } from "@/lib/authRedirect";
import { beginAuthSession } from "@/lib/authSession";
import { t } from "@/lib/i18n";

interface OAuthButtonsProps {
  onSuccess?: () => void;
}

type OAuthProvidersPayload = {
  google?: { enabled: boolean; client_id?: string; code_exchange_enabled?: boolean };
  apple?: { enabled: boolean; client_id?: string };
};

export function OAuthButtons({ onSuccess }: OAuthButtonsProps) {
  const toast = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState<"google" | "apple" | null>(null);
  const [providers, setProviders] = useState<OAuthProvidersPayload>({});
  const redirectTarget = getSafeRedirectTarget(searchParams?.get("redirect"));

  useEffect(() => {
    getJson<{ providers?: OAuthProvidersPayload }>("/oauth/providers")
      .then((data) => setProviders(data.providers || {}))
      .catch(() => setProviders({}));
  }, []);

  const handleGoogleAuth = async () => {
    if (!providers.google?.enabled) {
      toast.error(t("auth.oauth.googleNotConfigured", "Вход через Google не настроен"));
      return;
    }

    setLoading("google");
    try {
      // Initialize Google Sign-In
      // In production, use @react-oauth/google or similar
      if (typeof window !== "undefined" && (window as any).google && providers.google?.client_id) {
        const google = (window as any).google;
        google.accounts.id.initialize({
          client_id: providers.google.client_id,
          callback: handleGoogleCallback,
        });
        google.accounts.id.prompt();
      } else if (providers.google?.client_id && providers.google?.code_exchange_enabled) {
        const clientId = providers.google.client_id;
        const redirectUri = encodeURIComponent(`${window.location.origin}/auth/google/callback`);
        const scope = encodeURIComponent("openid email profile");
        const state = encodeURIComponent(JSON.stringify({ redirect: redirectTarget }));
        window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=${state}`;
      } else if (providers.google?.client_id) {
        toast.error(
          t(
            "auth.oauth.googleRedirectNotConfigured",
            "Вход через Google в этом браузере недоступен: на сервере не настроен обмен кода (нужен client secret).",
          ),
        );
        setLoading(null);
      } else {
        toast.error(t("auth.oauth.googleNotConfigured", "Вход через Google не настроен"));
        setLoading(null);
      }
    } catch (err) {
      toast.error(t("auth.oauth.googleError", "Не удалось войти через Google"));
      setLoading(null);
    }
  };

  const handleGoogleCallback = async (response: { credential: string }) => {
    try {
      const result = await postJson<{ token: string; user_id: number; email: string; is_paid: boolean }>("/oauth/google", {
        id_token: response.credential,
      });
      beginAuthSession(result.token);
      const target = await resolveTargetAfterAuthSession(redirectTarget);
      toast.success(t("auth.oauth.success", "Вход выполнен"));
      onSuccess?.();
      router.replace(target);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("auth.oauth.googleError", "Не удалось войти через Google"));
    } finally {
      setLoading(null);
    }
  };

  const handleAppleAuth = async () => {
    if (!providers.apple?.enabled) {
      toast.error(t("auth.oauth.appleNotConfigured", "Вход через Apple не настроен"));
      return;
    }

    setLoading("apple");
    try {
      // Initialize Apple Sign-In
      // In production, use @invertase/react-native-apple-authentication or similar
      if (typeof window !== "undefined" && (window as any).AppleID && providers.apple?.client_id) {
        const AppleID = (window as any).AppleID;
        AppleID.auth.init({
          clientId: providers.apple.client_id,
          scope: "name email",
          redirectURI: `${window.location.origin}/auth/apple/callback`,
          state: JSON.stringify({ redirect: redirectTarget }),
          usePopup: true,
        });
        AppleID.auth.signIn().then((response: any) => {
          handleAppleCallback(response);
        });
      } else {
        toast.error(t("auth.oauth.appleUnavailable", "Вход через Apple недоступен в этом браузере или не настроен"));
        setLoading(null);
      }
    } catch (err) {
      toast.error(t("auth.oauth.appleError", "Не удалось войти через Apple"));
      setLoading(null);
    }
  };

  const handleAppleCallback = async (response: { authorization: { id_token: string; code?: string }; user?: { email?: string; name?: { firstName?: string; lastName?: string } } }) => {
    try {
      const result = await postJson<{ token: string; user_id: number; email: string; is_paid: boolean }>("/oauth/apple", {
        identity_token: response.authorization.id_token,
        authorization_code: response.authorization.code,
        user: response.user,
      });
      beginAuthSession(result.token);
      const target = await resolveTargetAfterAuthSession(redirectTarget);
      toast.success(t("auth.oauth.success", "Вход выполнен"));
      onSuccess?.();
      router.replace(target);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("auth.oauth.appleError", "Не удалось войти через Apple"));
    } finally {
      setLoading(null);
    }
  };

  if (!providers.google?.enabled && !providers.apple?.enabled) {
    return null; // OAuth not configured
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-sm)", marginTop: "var(--orbit-space-md)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-md)", margin: "var(--orbit-space-md) 0" }}>
        <div style={{ flex: 1, height: "1px", background: "var(--orbit-color-border)" }} />
        <span className="orbit-body-xs orbit-text-muted">{t("auth.oauth.divider", "или")}</span>
        <div style={{ flex: 1, height: "1px", background: "var(--orbit-color-border)" }} />
      </div>

      {providers.google?.enabled && (
        <button
          onClick={handleGoogleAuth}
          disabled={loading !== null}
          className="orbit-button orbit-button-secondary"
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "var(--orbit-space-sm)",
          }}
        >
          {loading === "google" ? (
            <>
              <LoadingSpinner size="sm" />
              <span>{t("auth.oauth.googlePending", "Вход через Google…")}</span>
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 18 18" style={{ flexShrink: 0 }}>
                <path
                  fill="#4285F4"
                  d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"
                />
                <path
                  fill="#34A853"
                  d="M9 18c2.43 0 4.467-.806 5.96-2.184l-2.908-2.258c-.806.54-1.837.86-3.052.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"
                />
                <path
                  fill="#FBBC05"
                  d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707s.102-1.167.282-1.707V4.961H.957C.348 6.175 0 7.55 0 9s.348 2.825.957 4.039l3.007-2.332z"
                />
                <path
                  fill="#EA4335"
                  d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.961L3.964 7.293C4.672 5.163 6.656 3.58 9 3.58z"
                />
              </svg>
              <span>{t("auth.oauth.googleCta", "Войти через Google")}</span>
            </>
          )}
        </button>
      )}

      {providers.apple?.enabled && (
        <button
          onClick={handleAppleAuth}
          disabled={loading !== null}
          className="orbit-button orbit-button-secondary"
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "var(--orbit-space-sm)",
            background: "#000",
            color: "#fff",
          }}
        >
          {loading === "apple" ? (
            <>
              <LoadingSpinner size="sm" />
              <span>{t("auth.oauth.applePending", "Вход через Apple…")}</span>
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="currentColor" style={{ flexShrink: 0 }}>
                <path d="M13.5 0c-1.5 0-2.7 1.2-2.7 2.7 0 1.5 1.2 2.7 2.7 2.7 1.5 0 2.7-1.2 2.7-2.7C16.2 1.2 15 0 13.5 0zm-1.8 4.5c-2.1 0-3.6 1.5-3.6 3.6v6.3c0 2.1 1.5 3.6 3.6 3.6 1.2 0 2.1-.6 2.7-1.2-.6-.6-1.5-1.2-2.7-1.2-1.2 0-2.1.6-2.7 1.2-.6-.6-1.5-1.2-2.7-1.2-2.1 0-3.6 1.5-3.6 3.6v6.3c0 2.1 1.5 3.6 3.6 3.6 1.2 0 2.1-.6 2.7-1.2-.6-.6-1.5-1.2-2.7-1.2-1.2 0-2.1.6-2.7 1.2V8.1c0-2.1 1.5-3.6 3.6-3.6z" />
              </svg>
              <span>{t("auth.oauth.appleCta", "Войти через Apple")}</span>
            </>
          )}
        </button>
      )}
    </div>
  );
}
