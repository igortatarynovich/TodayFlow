"use client";

import { t } from "@/lib/i18n";

import { FormEvent } from "react";
import { OrientationRail } from "@/components/orbit";
import type { UserSettings } from "@/lib/types";

interface AccountSettingsFormProps {
  settings: UserSettings | null;
  form: Partial<UserSettings>;
  saving: boolean;
  showContent: boolean;
  greetingOptions: Array<{ value: string; label: string }>;
  languageOptions: Array<{ value: string; label: string }>;
  subscriptionOptions: Array<{ value: string; label: string }>;
  subscriptionSelected: (value: string) => boolean;
  onFormChange: (field: keyof UserSettings, value: any) => void;
  onToggleSubscription: (value: string) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
}

export function AccountSettingsForm({
  settings,
  form,
  saving,
  showContent,
  greetingOptions,
  languageOptions,
  subscriptionOptions,
  subscriptionSelected,
  onFormChange,
  onToggleSubscription,
  onSubmit,
}: AccountSettingsFormProps) {
  if (!settings) return null;

  return (
    <section 
      className="orbit-account-section"
      style={{
        opacity: showContent ? 1 : 0,
        transform: showContent ? "translateY(0)" : "translateY(30px)",
        transition: "opacity 0.8s ease 0.6s, transform 0.8s ease 0.6s"
      }}
    >
      <div className="orbit-account-form-container">
        <OrientationRail
          sectionLabel={t("account.settingsForm.rail.section", "Настройки")}
          metaLabel={t("account.settingsForm.rail.meta", "Профиль")}
          stepLabel={t("account.settings.profile", "Настройки профиля")}
        />
        <form onSubmit={onSubmit} className="orbit-form">
          <label>
            {t("account.email", "Эл. почта")}
            <input
              type="email"
              value={form.email || ""}
              onChange={(e) => onFormChange("email", e.target.value)}
              disabled
            />
          </label>
          <label>
            Имя
            <input
              type="text"
              value={form.first_name || ""}
              onChange={(e) => onFormChange("first_name", e.target.value)}
            />
          </label>
          <label>
            Фамилия
            <input
              type="text"
              value={form.last_name || ""}
              onChange={(e) => onFormChange("last_name", e.target.value)}
            />
          </label>
          <label>
            Приветствие
            <select
              value={form.greeting || "none"}
              onChange={(e) => onFormChange("greeting", e.target.value)}
            >
              {greetingOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Язык
            <select
              value={form.language || "ru"}
              onChange={(e) => onFormChange("language", e.target.value)}
            >
              {languageOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <div>
            <label className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)", display: "block" }}>
              Подписки
            </label>
            {subscriptionOptions.map((opt) => (
              <label key={opt.value} style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)", marginBottom: "var(--orbit-space-xs)" }}>
                <input
                  type="checkbox"
                  checked={subscriptionSelected(opt.value)}
                  onChange={() => onToggleSubscription(opt.value)}
                />
                <span className="orbit-body-sm">{opt.label}</span>
              </label>
            ))}
          </div>
          <button type="submit" disabled={saving} className="orbit-button orbit-button-primary">
            {saving ? t("account.settings.saving", "Сохранение…") : t("account.settings.save", "Сохранить")}
          </button>
        </form>
      </div>
    </section>
  );
}

