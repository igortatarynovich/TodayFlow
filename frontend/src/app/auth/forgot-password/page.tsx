"use client";

import { FormEvent, useState, useEffect } from "react";
import Link from "next/link";
import { postJson } from "@/lib/api";
import { t } from "@/lib/i18n";
import { useToast } from "@/components/ToastProvider";
import { LoadingSpinner } from "@/components/orbit";
import { DsButton } from "@/design-system";
import { AuthWebFormScreen } from "@/components/product-ui/AuthWebFormScreen";
import s from "@/components/product-ui/productWebScreens.module.css";

export default function ForgotPasswordPage() {
  const toast = useToast();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    setShowContent(true);
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await postJson<{ message: string }>("/auth/forgot-password", { email });
      setSuccess(true);
      toast.success(response.message || t("auth.forgotPassword.success", "Инструкции по восстановлению пароля отправлены на ваш email"));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t("auth.forgotPassword.error", "Ошибка при запросе восстановления пароля");
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthWebFormScreen
      title={t("auth.forgotPassword.title", "Восстановление пароля")}
      lead={t("auth.forgotPassword.subtitle", "Введите ваш email, и мы отправим инструкции по восстановлению пароля")}
      backHref="/auth?mode=login"
      backLabel={t("auth.forgotPassword.backToLoginLink", "← Вернуться к входу")}
      visible={showContent}
    >
      {success ? (
        <div style={{ textAlign: "center" }}>
          <svg
            className={s.authWebSuccessIcon}
            width={64}
            height={64}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <h2 className={s.authWebPanelTitle}>{t("auth.forgotPassword.checkEmail", "Проверьте ваш email")}</h2>
          <p className={s.authWebPanelBody}>
            {t("auth.forgotPassword.emailSent", "Мы отправили инструкции по восстановлению пароля на адрес")}{" "}
            <strong>{email}</strong>
          </p>
          <p className={s.authWebFormHint} style={{ marginTop: "1rem" }}>
            {t("auth.forgotPassword.checkSpam", "Если письмо не пришло, проверьте папку \"Спам\" или попробуйте еще раз через несколько минут.")}
          </p>
          <div className={s.authWebFormActions} style={{ marginTop: "1.5rem" }}>
            <Link href="/auth?mode=login">
              <DsButton variant="primary" size="block">
                {t("auth.forgotPassword.backToLogin", "Вернуться к входу")}
              </DsButton>
            </Link>
            <DsButton
              variant="secondary"
              size="block"
              onClick={() => {
                setSuccess(false);
                setEmail("");
              }}
            >
              {t("auth.forgotPassword.sendAgain", "Отправить еще раз")}
            </DsButton>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className={s.authWebFormField}>
            <label className={s.authWebFormLabel} htmlFor="forgot-email">
              {t("auth.forgotPassword.emailLabel", "Email адрес")}
            </label>
            <input
              id="forgot-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t("auth.form.emailPlaceholder", "you@example.com")}
              required
              className={s.authWebFormInput}
            />
            <p className={s.authWebFormHint}>
              {t("auth.forgotPassword.emailHint", "Мы отправим ссылку для восстановления пароля на этот адрес")}
            </p>
          </div>

          <DsButton variant="primary" size="block" type="submit" disabled={loading || !email}>
            {loading ? (
              <span style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem" }}>
                <LoadingSpinner size="sm" />
                {t("auth.forgotPassword.sending", "Отправка...")}
              </span>
            ) : (
              t("auth.forgotPassword.submit", "Отправить инструкции")
            )}
          </DsButton>

          <Link href="/auth?mode=login" className={s.authWebFormFooterLink}>
            {t("auth.forgotPassword.backToLoginLink", "← Вернуться к входу")}
          </Link>
        </form>
      )}
    </AuthWebFormScreen>
  );
}
