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
import { buildAuthHref, getSafeAuthMode, getSafeRedirectTarget, resolveTargetAfterAuthSession } from "@/lib/authRedirect";
import { beginAuthSession } from "@/lib/authSession";
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
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [loading, setLoading] = useState(false);
  const [showContent, setShowContent] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [redirectTarget, setRedirectTarget] = useState("/today");
  const [postAuthTarget, setPostAuthTarget] = useState("/today");
  const authHref = (nextMode: "login" | "signup") => buildAuthHref(nextMode, redirectTarget);
  const redirectContext = getRedirectContext(redirectTarget);

  useEffect(() => {
    const redirectParam = searchParams?.get("redirect");
    const modeParam = searchParams?.get("mode");
    setRedirectTarget(getSafeRedirectTarget(redirectParam));
    setPostAuthTarget(getSafeRedirectTarget(redirectParam));
    setMode(getSafeAuthMode(modeParam));
  }, [searchParams]);

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

  const validateForm = (): boolean => {
    const newErrors: ValidationError[] = [];

    // Email validation
    if (!email) {
      newErrors.push({ field: "email", message: t("auth.errors.emailRequired", "Email обязателен") });
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        newErrors.push({ field: "email", message: t("auth.errors.invalidEmail", "Введите корректный email") });
    }

    // Password validation
    if (!password) {
      newErrors.push({ field: "password", message: t("auth.errors.passwordRequired", "Пароль обязателен") });
    } else if (password.length < 8) {
      newErrors.push({ field: "password", message: t("auth.errors.passwordMinLength", "Пароль должен содержать минимум 8 символов") });
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      newErrors.push({
        field: "password",
        message: t("auth.errors.passwordComplexity", "Пароль должен содержать заглавные и строчные буквы, а также цифры"),
      });
    }

    // Confirm password validation (only for signup)
    if (mode === "signup") {
      if (!confirmPassword) {
        newErrors.push({ field: "confirmPassword", message: t("auth.errors.confirmPasswordRequired", "Подтвердите пароль") });
      } else if (password !== confirmPassword) {
        newErrors.push({ field: "confirmPassword", message: t("auth.errors.passwordsDoNotMatch", "Пароли не совпадают") });
      }

      // Terms validation
      if (!acceptTerms) {
        newErrors.push({ field: "acceptTerms", message: t("auth.errors.termsRequired", "Необходимо согласие с условиями использования") });
      }
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  };

  const getFieldError = (fieldName: string): string | undefined => {
    return errors.find(e => e.field === fieldName)?.message;
  };

  const passwordStrength = (): { strength: "weak" | "medium" | "strong"; text: string } => {
    if (!password) return { strength: "weak", text: "" };
    if (password.length < 8) return { strength: "weak", text: t("auth.password.strength.weak", "Слабый") };
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const score = [hasUpper, hasLower, hasNumber, hasSpecial].filter(Boolean).length;
    if (score <= 2) return { strength: "weak", text: t("auth.password.strength.weak", "Слабый") };
    if (score === 3) return { strength: "medium", text: t("auth.password.strength.medium", "Средний") };
    return { strength: "strong", text: t("auth.password.strength.strong", "Сильный") };
  };

  const strength = passwordStrength();

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setMessage(null);
    setErrors([]);

    if (mode === "signup" && !validateForm()) {
      return;
    }

    if (mode === "login" && (!email || !password)) {
      setErrors([{ field: "general", message: t("auth.errors.fillAllFields", "Заполните все поля") }]);
      return;
    }

    setLoading(true);
    try {
      const fallbackTarget = getSafeRedirectTarget(redirectTarget);
      if (mode === "signup") {
        const response = await postJson<{ token: string }>("/auth/signup", { email, password });
        beginAuthSession(response.token);
        const target = await resolveTargetAfterAuthSession(fallbackTarget);
        setPostAuthTarget(target);
        setMessage(t("auth.toast.signupNext", "Аккаунт создан. Открываем следующий шаг."));
      } else {
        const response = await postJson<LoginResponse>("/auth/login", { email, password });
        beginAuthSession(response.token);
        const target = await resolveTargetAfterAuthSession(fallbackTarget);
        setPostAuthTarget(target);
        setMessage(t("auth.toast.loginNext", "Вход выполнен. Открываем следующий шаг."));
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : mode === "signup" ? t("auth.signup.error", "Ошибка регистрации") : t("auth.login.error", "Ошибка входа");
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

  const switchToLogin = () => {
    setMode("login");
    router.replace(authHref("login"));
    setErrors([]);
    setMessage(null);
  };

  const switchToSignup = () => {
    setMode("signup");
    router.replace(authHref("signup"));
    setErrors([]);
    setMessage(null);
  };

  return (
    <AuthWebScreen
      mode={mode}
      onSelectLogin={switchToLogin}
      onSelectSignup={switchToSignup}
      loginTabLabel={t("auth.page.tab.login", "Вход")}
      signupTabLabel={t("auth.page.tab.signup", "Регистрация")}
      headline={mode === "login" ? t("auth.page.headline.login", "Войти в аккаунт") : t("auth.page.headline.signup", "Создать аккаунт")}
      lead={
        mode === "login"
          ? t("auth.page.sub.login", "Вход без потери прогресса и данных.")
          : t("auth.page.sub.signup", "Создай аккаунт, чтобы запустить персональный контур TodayFlow.")
      }
      productLine={t("auth.page.productLine", "Один вход для Today, Flow, Guidance, Compatibility и Profile.")}
      guestNavCtaHref={authHref("signup")}
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
                      setErrors(errors.filter((e) => e.field !== "password"));
                    }}
                    className={getFieldError("password") ? "orbit-form-input orbit-form-input-error" : "orbit-form-input"}
                    placeholder={
                      mode === "signup"
                        ? t("auth.form.passwordPlaceholder.signup", "Минимум 8 символов")
                        : t("auth.form.passwordPlaceholder.login", "Введите пароль")
                    }
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
                {mode === "signup" && password && (
                  <div style={{ marginTop: "var(--orbit-space-xs)" }}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "var(--orbit-space-xs)",
                        marginBottom: "4px",
                      }}
                    >
                      <div
                        style={{
                          flex: 1,
                          height: "4px",
                          background:
                            strength.strength === "weak"
                              ? "var(--orbit-color-coral)"
                              : strength.strength === "medium"
                                ? "var(--orbit-color-highlight)"
                                : "var(--orbit-color-success)",
                          borderRadius: "2px",
                        }}
                      />
                      <span
                        style={{
                          fontSize: "0.75rem",
                          color:
                            strength.strength === "weak"
                              ? "var(--orbit-color-coral)"
                              : strength.strength === "medium"
                                ? "var(--orbit-color-highlight)"
                                : "var(--orbit-color-success)",
                        }}
                      >
                        {strength.text}
                      </span>
                    </div>
                    <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "4px" }}>
                      {t("auth.form.passwordHint", "Используй заглавные и строчные буквы, цифры")}
                    </p>
                  </div>
                )}
                {getFieldError("password") && (
                  <p className="orbit-form-error" style={{ marginTop: "var(--orbit-space-xs)", fontSize: "0.875rem" }}>
                    {getFieldError("password")}
                  </p>
                )}
              </div>

              {/* Confirm Password Field (only for signup) */}
              {mode === "signup" && (
                <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
                  <label className="orbit-form-label" htmlFor="confirmPassword">
                    {t("auth.errors.confirmPassword", "Подтвердите пароль")}
                  </label>
                  <div style={{ position: "relative" }}>
                    <input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => {
                        setConfirmPassword(e.target.value);
                        setErrors(errors.filter((e) => e.field !== "confirmPassword"));
                      }}
                      className={getFieldError("confirmPassword") ? "orbit-form-input orbit-form-input-error" : "orbit-form-input"}
                      placeholder={t("auth.form.confirmPlaceholder", "Повторите пароль")}
                      required
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
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
                      {showConfirmPassword ? "👁️" : "👁️‍🗨️"}
                    </button>
                  </div>
                  {getFieldError("confirmPassword") && (
                    <p className="orbit-form-error" style={{ marginTop: "var(--orbit-space-xs)", fontSize: "0.875rem" }}>
                      {getFieldError("confirmPassword")}
                    </p>
                  )}
                </div>
              )}

              {/* Terms Checkbox (only for signup) */}
              {mode === "signup" && (
                <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
                  <label
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: "var(--orbit-space-sm)",
                      cursor: "pointer",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={acceptTerms}
                      onChange={(e) => {
                        setAcceptTerms(e.target.checked);
                        setErrors(errors.filter((e) => e.field !== "acceptTerms"));
                      }}
                      style={{ marginTop: "4px", cursor: "pointer" }}
                      disabled={loading}
                    />
                    <span className="orbit-body-xs orbit-text-muted" style={{ lineHeight: 1.5 }}>
                      {t("auth.form.termsAgree", "Я согласен с")}{" "}
                      <Link href="/terms" className="orbit-link-subtle" target="_blank">
                        {t("auth.form.termsLink", "условиями использования")}
                      </Link>{" "}
                      {t("auth.form.termsAnd", "и")}{" "}
                      <Link href="/privacy" className="orbit-link-subtle" target="_blank">
                        {t("auth.form.privacyLink", "политикой конфиденциальности")}
                      </Link>
                    </span>
                  </label>
                  {getFieldError("acceptTerms") && (
                    <p className="orbit-form-error" style={{ marginTop: "var(--orbit-space-xs)", fontSize: "0.875rem" }}>
                      {getFieldError("acceptTerms")}
                    </p>
                  )}
                </div>
              )}

              {/* General Error */}
              {getFieldError("general") && (
                <div style={{ marginBottom: "var(--orbit-space-md)", padding: "var(--orbit-space-sm)", background: "rgba(244, 165, 160, 0.1)", borderRadius: "var(--orbit-radius-sm)", border: "1px solid var(--orbit-color-coral)" }}>
                  <p className="orbit-body-sm" style={{ color: "var(--orbit-color-coral)", margin: 0 }}>
                    {getFieldError("general")}
                  </p>
                </div>
              )}

              {/* Success/Error Message */}
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

              {/* Submit Button */}
              <button
                type="submit"
                className="orbit-button orbit-button-primary"
                style={{ width: "100%", marginTop: "var(--orbit-space-md)" }}
                disabled={loading}
              >
                {loading ? (
                  <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "var(--orbit-space-xs)" }}>
                    <LoadingSpinner size="sm" />
                    {mode === "signup" ? t("auth.form.pending.signup", "Регистрация…") : t("auth.form.pending.login", "Вход…")}
                  </span>
                ) : mode === "signup" ? (
                  t("auth.form.submit.signup", "Зарегистрироваться")
                ) : (
                  t("auth.form.submit.login", "Войти")
                )}
              </button>

              {mode === "login" ? (
                <div style={{ marginTop: "var(--orbit-space-md)", textAlign: "center" }}>
                  <Link
                    href={redirectTarget === "/today" ? "/auth/forgot-password" : `/auth/forgot-password?redirect=${encodeURIComponent(redirectTarget)}`}
                    className="orbit-link"
                  >
                    {t("auth.form.forgotPassword", "Забыли пароль?")}
                  </Link>
                </div>
              ) : null}

              {mode === "login" ? <OAuthButtons /> : null}
            </form>

            {/* Switch Mode Link */}
            <div style={{ marginTop: "var(--orbit-space-lg)", textAlign: "center" }}>
              <p className="orbit-body-sm orbit-text-muted">
                {mode === "login" ? (
                  <>
                    {t("auth.switch.noAccount", "Нет аккаунта?")}{" "}
                    <button
                      type="button"
                      onClick={switchToSignup}
                      style={{ background: "none", border: "none", cursor: "pointer", padding: 0, color: "var(--orbit-color-primary)", textDecoration: "underline" }}
                    >
                      {t("auth.switch.register", "Зарегистрируйся")}
                    </button>
                  </>
                ) : (
                  <>
                    {t("auth.switch.hasAccount", "Уже есть аккаунт?")}{" "}
                    <button
                      type="button"
                      onClick={switchToLogin}
                      style={{ background: "none", border: "none", cursor: "pointer", padding: 0, color: "var(--orbit-color-primary)", textDecoration: "underline" }}
                    >
                      {t("auth.switch.logIn", "Войди")}
                    </button>
                  </>
                )}
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
