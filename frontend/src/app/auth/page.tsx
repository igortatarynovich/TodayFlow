"use client";

import { FormEvent, Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { postJson } from "@/lib/api";
import { OAuthButtons } from "@/components/auth/OAuthButtons";
import { LoadingSpinner } from "@/components/orbit";
import { AuthWebScreen } from "@/components/product-ui/AuthWebScreen";
import s from "@/components/product-ui/productWebScreens.module.css";
import { useAuth } from "@/lib/useAuth";
import { buildAuthHref, getSafeRedirectTarget, resolveTargetAfterAuthSession } from "@/lib/authRedirect";
import { beginAuthSession } from "@/lib/authSession";
import { guestSignupHref } from "@/lib/guestAccessStore";
import { t } from "@/lib/i18n";

function isAuthSuccessMessage(message: string | null): boolean {
  if (!message) return false;
  return (
    message === t("auth.toast.signupNext", "Аккаунт создан. Открываем следующий шаг.") ||
    message === t("auth.toast.loginNext", "Вход выполнен. Открываем следующий шаг.")
  );
}

type LoginResponse = {
  user_id: number;
  email: string;
  is_paid: boolean;
  token: string;
};

type ValidationError = {
  field: string;
  message: string;
};

function getRedirectContext(target: string): { title: string; body: string; chip: string } {
  if (target.startsWith("/onboarding")) {
    return {
      title: t("auth.redirect.onboarding.title", "После входа продолжишь сборку своего дня"),
      body: t(
        "auth.redirect.onboarding.body",
        "Сначала коротко соберём основу — имя, дату и место рождения. Это займёт около минуты.",
      ),
      chip: t("auth.redirect.chip.onboarding", "Старт"),
    };
  }
  if (target.startsWith("/profile")) {
    return {
      title: t("auth.redirect.profile.title", "После входа продолжишь сборку своей карты"),
      body: t(
        "auth.redirect.profile.body",
        "Сразу вернём тебя в настройку профиля, чтобы закончить карту и не потерять уже начатый ввод.",
      ),
      chip: t("auth.redirect.chip.profile", "Сборка профиля"),
    };
  }
  if (target.startsWith("/checkout") || target.startsWith("/subscriptions") || target.startsWith("/pricing")) {
    return {
      title: t("auth.redirect.access.title", "После входа вернём к выбору доступа"),
      body: t(
        "auth.redirect.access.body",
        "Авторизация нужна только чтобы не потерять твой выбор плана и провести тебя дальше по оплате без лишних кругов.",
      ),
      chip: t("auth.redirect.chip.access", "Доступ"),
    };
  }
  if (target.startsWith("/compatibility")) {
    return {
      title: t("auth.redirect.compatibility.title", "После входа вернём к разбору совместимости"),
      body: t(
        "auth.redirect.compatibility.body",
        "Ты продолжишь не с главной, а с того сценария отношений, в который уже вошёл.",
      ),
      chip: t("auth.redirect.chip.compatibility", "Совместимость"),
    };
  }
  if (target.startsWith("/flow") || target.startsWith("/tracking")) {
    return {
      title: t("auth.redirect.flow.title", "После входа откроется Flow"),
      body: t(
        "auth.redirect.flow.body",
        "Вернёмся к календарю прогресса, привычкам и целям — там, где ты отслеживаешь свой ритм.",
      ),
      chip: t("auth.redirect.chip.flow", "Flow"),
    };
  }
  if (target.startsWith("/library") || target.startsWith("/account")) {
    return {
      title: t("auth.redirect.account.title", "После входа откроется твой личный контур"),
      body: t(
        "auth.redirect.account.body",
        "Доступ к сохранённому, настройкам и профилям привязан к аккаунту, поэтому после входа сразу вернём тебя туда.",
      ),
      chip: t("auth.redirect.chip.account", "Аккаунт"),
    };
  }
  return {
    title: t("auth.redirect.default.title", "После входа откроется твой следующий шаг"),
    body: t(
      "auth.redirect.default.body",
      "Если профиль готов — откроем твою карту и ритм. Если нет — сначала соберём базовые данные в профиле.",
    ),
    chip: t("auth.redirect.chip.default", "TodayFlow"),
  };
}

function AuthPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const mode = "login" as const;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [loading, setLoading] = useState(false);
  const [showContent, setShowContent] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [redirectTarget, setRedirectTarget] = useState("/today");
  const [postAuthTarget, setPostAuthTarget] = useState("/today");
  const softSignupHref = guestSignupHref();
  const redirectContext = getRedirectContext(redirectTarget);

  useEffect(() => {
    const redirectParam = searchParams?.get("redirect");
    const modeParam = searchParams?.get("mode");
    const safeRedirect = getSafeRedirectTarget(redirectParam);
    setRedirectTarget(safeRedirect);
    setPostAuthTarget(safeRedirect);
    // Password signup retired — send new users into soft onboarding.
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

  const getFieldError = (fieldName: string): string | undefined => {
    return errors.find(e => e.field === fieldName)?.message;
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setMessage(null);
    setErrors([]);

    if (!email || !password) {
      setErrors([{ field: "general", message: t("auth.errors.fillAllFields", "Заполните все поля") }]);
      return;
    }

    setLoading(true);
    try {
      const fallbackTarget = getSafeRedirectTarget(redirectTarget);
      const response = await postJson<LoginResponse>("/auth/login", { email, password });
      beginAuthSession(response.token);
      const target = await resolveTargetAfterAuthSession(fallbackTarget);
      setPostAuthTarget(target);
      setMessage(t("auth.toast.loginNext", "Вход выполнен. Открываем следующий шаг."));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t("auth.login.error", "Ошибка входа");
      setMessage(errorMessage);
      const lower = errorMessage.toLowerCase();
      if (
        lower.includes("email") ||
        lower.includes("существует") ||
        lower.includes("exist") ||
        lower.includes("already")
      ) {
        setErrors([{ field: "email", message: errorMessage }]);
      } else if (
        lower.includes("пароль") ||
        lower.includes("password") ||
        lower.includes("credential") ||
        lower.includes("invalid")
      ) {
        setErrors([{ field: "password", message: errorMessage }]);
      }
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return <AuthWebScreen mode={mode} onSelectLogin={() => {}} onSelectSignup={() => {}} loginTabLabel="" signupTabLabel="" headline="" lead="" loading />;
  }

  if (isAuthenticated) {
    return <AuthWebScreen mode={mode} onSelectLogin={() => {}} onSelectSignup={() => {}} loginTabLabel="" signupTabLabel="" headline="" lead="" loading />;
  }

  return (
    <AuthWebScreen
      mode={mode}
      onSelectLogin={() => {}}
      onSelectSignup={() => router.push(softSignupHref)}
      loginTabLabel={t("auth.page.tab.login", "Вход")}
      signupTabLabel={t("auth.page.tab.signup", "Создать мой Today")}
      loginOnly
      headline={t("auth.page.headline.login", "Войти в аккаунт")}
      lead={t("auth.page.sub.login", "Вход без потери прогресса и данных.")}
      productLine={t("auth.page.productLine", "Один вход для Today, Flow, Guidance, Compatibility и Profile.")}
      guestNavCtaHref={softSignupHref}
      guestNavCtaLabel={t("auth.page.navCta", "Создать мой Today")}
      visible={showContent}
    >
          <div className={s.authWebPanel}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", gap: "var(--orbit-space-md)", flexWrap: "wrap" }}>
              <div>
                <p className={s.authWebPanelEyebrow}>
                  {t("auth.sidebar.eyebrow", "Следующий шаг")}
                </p>
                <h2 className={s.authWebPanelTitle}>
                  {redirectContext.title}
                </h2>
              </div>
              <span className={s.authWebChip}>
                {redirectContext.chip}
              </span>
            </div>
            <p className={s.authWebPanelBody}>
              {redirectContext.body}
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem", marginTop: "0.9rem" }}>
              <Link href="/pricing" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                {t("auth.sidebar.planCta", "Выбрать план")}
              </Link>
              <Link href="/help" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                {t("auth.sidebar.faqCta", "Открыть FAQ")}
              </Link>
            </div>
            <p className="orbit-body-xs" style={{ margin: "0.6rem 0 0", color: "#8a6a3c" }}>
              {t("auth.sidebar.routeSaved", "Маршрут после входа сохраняется автоматически.")}
            </p>

            <div className={s.authWebPointList}>
              {[
                {
                  title: t("auth.sidebar.point1.title", "Один вход для всех экранов"),
                  body: t("auth.sidebar.point1.body", "Today, Flow, Guidance и Compatibility остаются в одном связанном маршруте."),
                },
                {
                  title: t("auth.sidebar.point2.title", "Профиль не теряется"),
                  body: t("auth.sidebar.point2.body", "Если профиль ещё не завершён, сначала доведём до Summary, затем вернём в основной сценарий."),
                },
                {
                  title: t("auth.sidebar.point3.title", "Доступ под контролем"),
                  body: t("auth.sidebar.point3.body", "Пароль можно восстановить по email и изменить в настройках аккаунта."),
                },
              ].map((item, idx) => (
                <div key={`auth-sidebar-${idx}`} className={s.authWebPoint}>
                  <p className={s.authWebPointTitle}>
                    {item.title}
                  </p>
                  <p className={s.authWebPointBody}>
                    {item.body}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className={s.authWebPanel}>
            <form onSubmit={handleSubmit} className="orbit-form">
              {/* Email Field */}
              <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
                <label className="orbit-form-label" htmlFor="email">
                  {t("auth.common.email", "Эл. почта")}
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setErrors(errors.filter((e) => e.field !== "email"));
                  }}
                  className={getFieldError("email") ? "orbit-form-input orbit-form-input-error" : "orbit-form-input"}
                  placeholder={t("auth.form.emailPlaceholder", "you@example.com")}
                  required
                  disabled={loading}
                />
                {getFieldError("email") && (
                  <p className="orbit-form-error" style={{ marginTop: "var(--orbit-space-xs)", fontSize: "0.875rem" }}>
                    {getFieldError("email")}
                  </p>
                )}
              </div>

              {/* Password Field */}
              <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
                <label className="orbit-form-label" htmlFor="password">
                  {t("auth.common.password", "Пароль")}
                </label>
                <div style={{ position: "relative" }}>
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      setErrors(errors.filter((errItem) => errItem.field !== "password"));
                    }}
                    className={getFieldError("password") ? "orbit-form-input orbit-form-input-error" : "orbit-form-input"}
                    placeholder={t("auth.form.passwordPlaceholder.login", "Введите пароль")}
                    required
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: "absolute",
                      right: "var(--orbit-space-sm)",
                      top: "50%",
                      transform: "translateY(-50%)",
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      color: "var(--orbit-color-slate)",
                      fontSize: "0.875rem",
                      padding: "4px",
                    }}
                    tabIndex={-1}
                  >
                    {showPassword ? "👁️" : "👁️‍🗨️"}
                  </button>
                </div>
                {getFieldError("password") && (
                  <p className="orbit-form-error" style={{ marginTop: "var(--orbit-space-xs)", fontSize: "0.875rem" }}>
                    {getFieldError("password")}
                  </p>
                )}
              </div>

              {getFieldError("general") && (
                <div style={{ marginBottom: "var(--orbit-space-md)", padding: "var(--orbit-space-sm)", background: "rgba(244, 165, 160, 0.1)", borderRadius: "var(--orbit-radius-sm)", border: "1px solid var(--orbit-color-coral)" }}>
                  <p className="orbit-body-sm" style={{ color: "var(--orbit-color-coral)", margin: 0 }}>
                    {getFieldError("general")}
                  </p>
                </div>
              )}

              {message && (
                <div
                  style={{
                    marginBottom: "var(--orbit-space-md)",
                    padding: "var(--orbit-space-sm)",
                    background: isAuthSuccessMessage(message)
                      ? "rgba(16, 185, 129, 0.1)"
                      : "rgba(244, 165, 160, 0.1)",
                    borderRadius: "var(--orbit-radius-sm)",
                    border: `1px solid ${isAuthSuccessMessage(message) ? "var(--orbit-color-success)" : "var(--orbit-color-coral)"}`,
                  }}
                >
                  <p
                    className="orbit-body-sm"
                    style={{
                      color: isAuthSuccessMessage(message) ? "var(--orbit-color-success)" : "var(--orbit-color-coral)",
                      margin: 0,
                    }}
                  >
                    {message}
                  </p>
                </div>
              )}

              <button
                type="submit"
                className="orbit-button orbit-button-primary"
                style={{ width: "100%", marginTop: "var(--orbit-space-md)" }}
                disabled={loading}
              >
                {loading ? (
                  <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "var(--orbit-space-xs)" }}>
                    <LoadingSpinner size="sm" />
                    {t("auth.form.pending.login", "Вход…")}
                  </span>
                ) : (
                  t("auth.form.submit.login", "Войти")
                )}
              </button>

              <div style={{ marginTop: "var(--orbit-space-md)", textAlign: "center" }}>
                <Link
                  href={redirectTarget === "/today" ? "/auth/forgot-password" : `/auth/forgot-password?redirect=${encodeURIComponent(redirectTarget)}`}
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
        <AuthWebScreen mode="login" onSelectLogin={() => {}} onSelectSignup={() => {}} loginTabLabel="" signupTabLabel="" headline="" lead="" loading />
      }
    >
      <AuthPageContent />
    </Suspense>
  );
}
