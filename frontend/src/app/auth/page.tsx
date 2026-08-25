"use client";

import { FormEvent, Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { postJson } from "@/lib/api";
import { OAuthButtons } from "@/components/auth/OAuthButtons";
import { LoadingSpinner } from "@/components/orbit";
import { AuthWebScreen } from "@/components/product-ui/AuthWebScreen";
import s from "@/components/product-ui/productWebScreens.module.css";
import { useAuth } from "@/lib/useAuth";
import { buildAuthHref, getSafeRedirectTarget, resolveTargetAfterAuthSession, assignAfterAuthSession } from "@/lib/authRedirect";
import { beginAuthSession } from "@/lib/authSession";
import { guestSignupHref } from "@/lib/guestAccessStore";
import { t } from "@/lib/i18n";
import {
  mapLoginFailure,
  shouldFocusLoginFieldError,
  type LoginFieldErrors,
} from "@/lib/mapLoginFailure";

type LoginResponse = {
  user_id: number;
  email: string;
  is_paid: boolean;
  token: string;
};

type FieldErrors = LoginFieldErrors;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function AuthPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const mode = "login" as const;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [loading, setLoading] = useState(false);
  const [showContent, setShowContent] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [redirectTarget, setRedirectTarget] = useState("/today");
  const [postAuthTarget, setPostAuthTarget] = useState("/today");
  const [redirectReady, setRedirectReady] = useState(false);
  const leavingAfterAuthRef = useRef(false);
  const softSignupHref = guestSignupHref();
  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const redirectParam = searchParams?.get("redirect");
    const modeParam = searchParams?.get("mode");
    const safeRedirect = getSafeRedirectTarget(redirectParam);
    setRedirectTarget(safeRedirect);
    setPostAuthTarget(safeRedirect);
    setRedirectReady(true);
    if (modeParam === "signup") {
      router.replace(buildAuthHref("signup", redirectParam));
    }
  }, [searchParams, router]);

  useEffect(() => {
    // Do not steal a live submit — handleSubmit resolves onboarding vs Today first.
    if (!redirectReady || authLoading || loading || !isAuthenticated || leavingAfterAuthRef.current) return;
    leavingAfterAuthRef.current = true;
    assignAfterAuthSession(postAuthTarget);
  }, [redirectReady, isAuthenticated, authLoading, loading, postAuthTarget]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      setShowContent(true);
    }
  }, [authLoading, isAuthenticated]);

  // iOS / flaky /auth/me must not leave the login form behind a spinner.
  useEffect(() => {
    if (!authLoading) return;
    const id = window.setTimeout(() => setShowContent(true), 2_000);
    return () => window.clearTimeout(id);
  }, [authLoading]);

  const clearFieldError = (field: keyof FieldErrors) => {
    setErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  };

  const validate = (): FieldErrors => {
    const next: FieldErrors = {};
    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      next.email = t("auth.errors.emailRequired", "Введите email");
    } else if (!EMAIL_RE.test(trimmedEmail)) {
      next.email = t("auth.errors.invalidEmail", "Введите корректный email");
    }
    if (!password) {
      next.password = t("auth.errors.passwordRequired", "Введите пароль");
    }
    return next;
  };

  const focusFirstError = (next: FieldErrors) => {
    if (next.email) {
      emailRef.current?.focus();
      return;
    }
    if (next.password) {
      passwordRef.current?.focus();
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSuccessMessage(null);

    const nextErrors = validate();
    if (nextErrors.email || nextErrors.password) {
      setErrors(nextErrors);
      focusFirstError(nextErrors);
      return;
    }

    setErrors({});
    setLoading(true);
    try {
      const fallbackTarget = getSafeRedirectTarget(redirectTarget);
      const response = await postJson<LoginResponse>("/auth/login", {
        email: email.trim(),
        password,
      });
      beginAuthSession(response.token);
      const target = await resolveTargetAfterAuthSession(fallbackTarget);
      setPostAuthTarget(target);
      setSuccessMessage(t("auth.toast.loginNext", "Вход выполнен. Открываем следующий шаг."));
      leavingAfterAuthRef.current = true;
      // Full document load — App Router replace can hang on iOS Safari / PWA.
      assignAfterAuthSession(target);
    } catch (err) {
      const mapped = mapLoginFailure(err);
      setErrors(mapped);
      // Avoid focusing password on transport errors: Chrome can clear disabled/re-enabled
      // password inputs and fire onChange(""), which would wipe the just-set error.
      if (shouldFocusLoginFieldError(mapped, err)) {
        focusFirstError(mapped);
      }
    } finally {
      setLoading(false);
    }
  };

  if (authLoading && !showContent && !isAuthenticated) {
    return (
      <AuthWebScreen
        mode={mode}
        onSelectLogin={() => {}}
        onSelectSignup={() => {}}
        loginTabLabel=""
        signupTabLabel=""
        headline=""
        lead=""
        formOnly
        loading
      />
    );
  }

  if (isAuthenticated && leavingAfterAuthRef.current) {
    return (
      <AuthWebScreen
        mode={mode}
        onSelectLogin={() => {}}
        onSelectSignup={() => {}}
        loginTabLabel=""
        signupTabLabel=""
        headline=""
        lead=""
        formOnly
        loading
      />
    );
  }

  const emailError = errors.email;
  const passwordError = errors.password;

  return (
    <AuthWebScreen
      mode={mode}
      onSelectLogin={() => {}}
      onSelectSignup={() => router.push(softSignupHref)}
      loginTabLabel={t("auth.page.tab.login", "Вход")}
      signupTabLabel={t("auth.page.tab.signup", "Создать мой Today")}
      loginOnly
      formOnly
      headline={t("auth.page.headline.login", "Войти в аккаунт")}
      lead={t("auth.page.sub.login", "Вход без потери прогресса и данных.")}
      guestNavCtaHref={softSignupHref}
      guestNavCtaLabel={t("auth.page.navCta", "Создать мой Today")}
      visible={showContent}
    >
      <div className={s.authWebPanel}>
        <form onSubmit={handleSubmit} className="orbit-form" noValidate>
          <div className={s.authWebFormField}>
            <label className={s.authWebFormLabel} htmlFor="email">
              {t("auth.common.email", "Эл. почта")}
            </label>
            <input
              ref={emailRef}
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                clearFieldError("email");
              }}
              className={emailError ? `${s.authWebFormInput} ${s.authWebFormInputError}` : s.authWebFormInput}
              placeholder={t("auth.form.emailPlaceholder", "you@example.com")}
              aria-invalid={Boolean(emailError)}
              aria-describedby="email-error"
              readOnly={loading}
            />
            <p id="email-error" className={s.authWebFormErrorSlot} role={emailError ? "alert" : undefined}>
              {emailError ?? "\u00a0"}
            </p>
          </div>

          <div className={s.authWebFormField}>
            <label className={s.authWebFormLabel} htmlFor="password">
              {t("auth.common.password", "Пароль")}
            </label>
            <div className={s.authWebFormPasswordWrap}>
              <input
                ref={passwordRef}
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  clearFieldError("password");
                }}
                className={
                  passwordError ? `${s.authWebFormInput} ${s.authWebFormInputError}` : s.authWebFormInput
                }
                placeholder={t("auth.form.passwordPlaceholder.login", "Введите пароль")}
                aria-invalid={Boolean(passwordError)}
                aria-describedby="password-error"
                readOnly={loading}
              />
              <button
                type="button"
                className={s.authWebFormPasswordToggle}
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                aria-label={showPassword ? "Скрыть пароль" : "Показать пароль"}
              >
                {showPassword ? "Скрыть" : "Показать"}
              </button>
            </div>
            <p
              id="password-error"
              className={s.authWebFormErrorSlot}
              role={passwordError ? "alert" : undefined}
            >
              {passwordError ?? "\u00a0"}
            </p>
          </div>

          {successMessage ? <p className={s.authWebFormSuccess}>{successMessage}</p> : null}

          <button
            type="submit"
            className="orbit-button orbit-button-primary"
            style={{ width: "100%", marginTop: "var(--orbit-space-md)" }}
            disabled={loading}
          >
            {loading ? (
              <span
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "var(--orbit-space-xs)",
                }}
              >
                <LoadingSpinner size="sm" />
                {t("auth.form.pending.login", "Вход…")}
              </span>
            ) : (
              t("auth.form.submit.login", "Войти")
            )}
          </button>

          <div style={{ marginTop: "var(--orbit-space-md)", textAlign: "center" }}>
            <Link
              href={
                redirectTarget === "/today"
                  ? "/auth/forgot-password"
                  : `/auth/forgot-password?redirect=${encodeURIComponent(redirectTarget)}`
              }
              className="orbit-link"
            >
              {t("auth.form.forgotPassword", "Забыли пароль?")}
            </Link>
          </div>

          <OAuthButtons />
        </form>

        <div style={{ marginTop: "var(--orbit-space-lg)", textAlign: "center" }}>
          <p className="orbit-body-sm orbit-text-muted">
            {t("auth.switch.noAccount", "Нет аккаунта?")}{" "}
            <Link href={softSignupHref} className="orbit-link">
              {t("auth.page.navCta", "Создать мой Today")}
            </Link>
          </p>
        </div>
      </div>
    </AuthWebScreen>
  );
}

export default function AuthPage() {
  return (
    <Suspense
      fallback={
        <AuthWebScreen
          mode="login"
          onSelectLogin={() => {}}
          onSelectSignup={() => {}}
          loginTabLabel=""
          signupTabLabel=""
          headline=""
          lead=""
          formOnly
          loading
        />
      }
    >
      <AuthPageContent />
    </Suspense>
  );
}
