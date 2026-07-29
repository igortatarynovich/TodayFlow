"use client";

import { FormEvent, Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ApiError, postJson } from "@/lib/api";
import { OAuthButtons } from "@/components/auth/OAuthButtons";
import { LoadingSpinner } from "@/components/orbit";
import { AuthWebScreen } from "@/components/product-ui/AuthWebScreen";
import s from "@/components/product-ui/productWebScreens.module.css";
import { useAuth } from "@/lib/useAuth";
import { buildAuthHref, getSafeRedirectTarget, resolveTargetAfterAuthSession } from "@/lib/authRedirect";
import { beginAuthSession } from "@/lib/authSession";
import { guestSignupHref } from "@/lib/guestAccessStore";
import { t } from "@/lib/i18n";

type LoginResponse = {
  user_id: number;
  email: string;
  is_paid: boolean;
  token: string;
};

type FieldErrors = {
  email?: string;
  password?: string;
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function mapLoginFailure(err: unknown): FieldErrors {
  const invalidCredentials = t("auth.errors.invalidCredentials", "Неверный email или пароль");
  const networkError = t(
    "auth.errors.network",
    "Не удалось подключиться. Попробуйте ещё раз",
  );
  const rateLimited = t(
    "auth.errors.rateLimited",
    "Слишком много попыток. Попробуйте позже",
  );
  const serverError = t("auth.errors.server", "Не удалось подключиться. Попробуйте ещё раз");

  if (err instanceof ApiError) {
    if (err.status === 0) {
      return { password: networkError };
    }
    if (err.status === 429) {
      return { password: rateLimited };
    }
    if (err.status >= 500) {
      return { password: serverError };
    }
    if (err.status === 401) {
      return { email: invalidCredentials, password: invalidCredentials };
    }
  }

  const errorMessage = err instanceof Error ? err.message : t("auth.login.error", "Ошибка входа");
  const lower = errorMessage.toLowerCase();

  if (
    lower.includes("network") ||
    lower.includes("fetch") ||
    lower.includes("подключ") ||
    lower.includes("connection")
  ) {
    return { password: networkError };
  }
  if (lower.includes("too many") || lower.includes("rate") || lower.includes("попыток")) {
    return { password: rateLimited };
  }
  if (
    lower.includes("unauthorized") ||
    lower.includes("credential") ||
    lower.includes("invalid") ||
    lower.includes("неверн") ||
    lower.includes("пароль") ||
    lower.includes("password") ||
    lower.includes("email")
  ) {
    return { email: invalidCredentials, password: invalidCredentials };
  }

  return { password: errorMessage };
}

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
  const softSignupHref = guestSignupHref();
  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const redirectParam = searchParams?.get("redirect");
    const modeParam = searchParams?.get("mode");
    const safeRedirect = getSafeRedirectTarget(redirectParam);
    setRedirectTarget(safeRedirect);
    setPostAuthTarget(safeRedirect);
    if (modeParam === "signup") {
      router.replace(buildAuthHref("signup", redirectParam));
    }
  }, [searchParams, router]);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace(postAuthTarget);
    }
  }, [isAuthenticated, authLoading, postAuthTarget, router]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      setShowContent(true);
    }
  }, [authLoading, isAuthenticated]);

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
    } catch (err) {
      const mapped = mapLoginFailure(err);
      setErrors(mapped);
      focusFirstError(mapped);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || isAuthenticated) {
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
              disabled={loading}
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
                disabled={loading}
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
