"use client";

import { Suspense, FormEvent, useState, useEffect } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { postJson } from "@/lib/api";
import { t } from "@/lib/i18n";
import { useToast } from "@/components/ToastProvider";
import { LoadingSpinner } from "@/components/orbit";
import { DsButton } from "@/design-system";
import { AuthWebFormScreen } from "@/components/product-ui/AuthWebFormScreen";
import s from "@/components/product-ui/productWebScreens.module.css";

function ResetPasswordContent() {
  const toast = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    const tokenParam = searchParams?.get("token");
    if (tokenParam) {
      setToken(tokenParam);
    } else {
      toast.error(t("auth.resetPassword.tokenNotFound", "Токен восстановления не найден"));
    }
    setShowContent(true);
  }, [searchParams, toast]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    if (password !== confirmPassword) {
      toast.error(t("auth.errors.passwordsDoNotMatch", "Пароли не совпадают"));
      return;
    }

    if (password.length < 8) {
      toast.error(t("auth.errors.passwordMinLength", "Пароль должен содержать минимум 8 символов"));
      return;
    }

    if (!token) {
      toast.error(t("auth.resetPassword.tokenNotFound", "Токен восстановления не найден"));
      return;
    }

    setLoading(true);
    try {
      await postJson<{ message: string }>("/auth/reset-password", {
        token,
        new_password: password,
      });
      setSuccess(true);
      toast.success(t("auth.resetPassword.success", "Пароль успешно изменен"));
      setTimeout(() => {
        router.push("/auth?mode=login");
      }, 2000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t("auth.resetPassword.error", "Ошибка при сбросе пароля");
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!token && !success) {
    return (
      <AuthWebFormScreen
        title={t("auth.resetPassword.newPassword", "Новый пароль")}
        lead={t("auth.resetPassword.tokenNotFound", "Токен восстановления не найден")}
        backHref="/auth/forgot-password"
        visible={showContent}
      >
        <div className={s.authWebFormActions}>
          <Link href="/auth/forgot-password">
            <DsButton variant="primary" size="block">
              {t("auth.resetPassword.requestNewToken", "Запросить новый токен")}
            </DsButton>
          </Link>
        </div>
      </AuthWebFormScreen>
    );
  }

  return (
    <AuthWebFormScreen
      title={success ? t("auth.resetPassword.passwordChanged", "Пароль изменен") : t("auth.resetPassword.newPassword", "Новый пароль")}
      lead={
        success
          ? t("auth.resetPassword.redirectMessage", "Ваш пароль успешно изменен. Вы будете перенаправлены на страницу входа...")
          : t("auth.resetPassword.subtitle", "Введите новый пароль для вашего аккаунта")
      }
      backHref="/auth?mode=login"
      visible={showContent}
    >
      {success ? (
        <div className={s.authWebFormActions}>
          <Link href="/auth?mode=login">
            <DsButton variant="primary" size="block">
              {t("auth.resetPassword.backToLogin", "Вернуться к входу")}
            </DsButton>
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className={s.authWebFormField}>
            <label className={s.authWebFormLabel} htmlFor="reset-password">
              {t("auth.resetPassword.newPasswordLabel", "Новый пароль")}
            </label>
            <input
              id="reset-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t("auth.resetPassword.passwordPlaceholder", "Минимум 8 символов")}
              required
              minLength={8}
              className={s.authWebFormInput}
            />
            <p className={s.authWebFormHint}>
              {t("auth.errors.passwordMinLength", "Пароль должен содержать минимум 8 символов")}
            </p>
          </div>

          <div className={s.authWebFormField}>
            <label className={s.authWebFormLabel} htmlFor="reset-confirm-password">
              {t("auth.resetPassword.confirmPasswordLabel", "Подтвердите пароль")}
            </label>
            <input
              id="reset-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder={t("auth.resetPassword.confirmPlaceholder", "Повторите пароль")}
              required
              minLength={8}
              className={s.authWebFormInput}
            />
          </div>

          <DsButton variant="primary" size="block" type="submit" disabled={loading || !password || !confirmPassword}>
            {loading ? (
              <span style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem" }}>
                <LoadingSpinner size="sm" />
                {t("auth.resetPassword.changing", "Изменение пароля...")}
              </span>
            ) : (
              t("auth.resetPassword.submit", "Изменить пароль")
            )}
          </DsButton>

          <Link href="/auth?mode=login" className={s.authWebFormFooterLink}>
            {t("auth.resetPassword.backToLogin", "← Вернуться к входу")}
          </Link>
        </form>
      )}
    </AuthWebFormScreen>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <AuthWebFormScreen title={t("common.loading", "Загрузка...")} loading />
      }
    >
      <ResetPasswordContent />
    </Suspense>
  );
}
