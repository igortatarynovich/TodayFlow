"use client";

import Link from "next/link";
import React, { FormEvent } from "react";
import { OrientationRail } from "@/components/orbit";
import { t } from "@/lib/i18n";
import type { AstroProfile } from "@/lib/types";

interface AccountAstroProfileFormProps {
  profiles: AstroProfile[];
  profileForm: Partial<AstroProfile>;
  setProfileForm: React.Dispatch<React.SetStateAction<Partial<AstroProfile>>>;
  editingId: number | null;
  setEditingId: React.Dispatch<React.SetStateAction<number | null>>;
  /** Если 0 — дату/время/место менять нельзя (лимит уточнений исчерпан). */
  birthFactsCorrectionsRemaining?: number | null;
  /** Пока > 0 — временная блокировка правок фактов рождения после последнего сохранения. */
  birthFactsCooldownRemainingSeconds?: number | null;
  profileSaving: boolean;
  error: string | null;
  showContent: boolean;
  onSubmit: (e: FormEvent<HTMLFormElement>) => Promise<void>;
}

const RELATION_OPTIONS = [
  { value: "self", label: "Я" },
  { value: "partner", label: "Партнер / супруг" },
  { value: "child", label: "Ребенок" },
  { value: "close_person", label: "Близкий человек" },
];

export function AccountAstroProfileForm({
  profiles,
  profileForm,
  setProfileForm,
  editingId,
  setEditingId,
  birthFactsCorrectionsRemaining = null,
  birthFactsCooldownRemainingSeconds = null,
  profileSaving,
  error,
  showContent,
  onSubmit,
}: AccountAstroProfileFormProps) {
  const birthFactsLocked =
    typeof birthFactsCorrectionsRemaining === "number" && birthFactsCorrectionsRemaining <= 0;
  const birthFactsCooldownLocked =
    typeof birthFactsCooldownRemainingSeconds === "number" && birthFactsCooldownRemainingSeconds > 0;
  const birthFactsFieldsLocked = birthFactsLocked || birthFactsCooldownLocked;
  return (
    <section 
      className="orbit-account-section"
      style={{
        opacity: showContent ? 1 : 0,
        transform: showContent ? "translateY(0)" : "translateY(30px)",
        transition: "opacity 0.8s ease 0.7s, transform 0.8s ease 0.7s"
      }}
    >
      <div className="orbit-account-form-container">
        <OrientationRail
          sectionLabel={t("account.astroForm.orientation.section", "Astro profile")}
          metaLabel={t("account.astroForm.orientation.meta", "Create")}
          stepLabel={editingId ? "Редактировать профиль" : "Добавить человека"}
        />
        {profiles.length === 0 && (
          <div style={{ 
            marginBottom: "var(--orbit-space-md)"
          }}>
            <p className="orbit-body-sm" style={{ lineHeight: 1.6, marginBottom: "var(--orbit-space-xs)" }}>
              <strong>Как добавить человека в круг:</strong>
            </p>
            <ol style={{ 
              listStyle: "decimal",
              paddingLeft: "var(--orbit-space-lg)",
              margin: 0,
              display: "grid",
              gap: "var(--orbit-space-xs)"
            }}>
              <li className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
                Укажите название профиля так, как тебе будет удобно его узнавать (например: &quot;Я&quot;, &quot;Аня&quot;, &quot;Друг&quot;, &quot;Коллега&quot;)
              </li>
              <li className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
                Введите дату рождения (обязательно)
              </li>
              <li className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
                Укажите место рождения — город и страна (обязательно)
              </li>
              <li className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
                Добавьте время рождения, если известно (или отметьте &quot;Время неизвестно&quot;)
              </li>
            </ol>
            <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-sm)", lineHeight: 1.6 }}>
              После создания профиль автоматически сохранится. Его можно будет использовать для совместимости,
              сравнений и других персональных разборов связи.
            </p>
            <p className="orbit-body-xs" style={{ marginTop: "var(--orbit-space-sm)", lineHeight: 1.6 }}>
              <Link href="/onboarding/core" className="orbit-link">
                Или создайте профиль через форму разбора →
              </Link>
            </p>
          </div>
        )}
        {error && <p className="orbit-error" style={{ marginBottom: "var(--orbit-space-md)" }}>{error}</p>}
        {editingId && birthFactsCooldownLocked && (
          <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)", lineHeight: 1.55 }}>
            {t("account.astro.birthFactsCooldownHint", undefined, {
              minutes: Math.max(1, Math.ceil((birthFactsCooldownRemainingSeconds ?? 0) / 60)),
            })}
          </p>
        )}
        {editingId && typeof birthFactsCorrectionsRemaining === "number" && !birthFactsCooldownLocked && (
          <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)", lineHeight: 1.55 }}>
            {birthFactsLocked
              ? t("account.astro.birthFactsLockedHint")
              : t("account.astro.birthFactsRemaining", undefined, {
                  n: birthFactsCorrectionsRemaining,
                  max: profileForm.birth_facts_corrections_max ?? 3,
                })}
          </p>
        )}
        <form onSubmit={onSubmit} className="orbit-form">
          <label>
            {t("account.astro.label", "Название профиля")} *
            <input
              type="text"
              value={profileForm.label || ""}
              onChange={(e) => setProfileForm({ ...profileForm, label: e.target.value })}
              required
              placeholder={t("account.astro.labelPlaceholder", "Например: Я, Аня, Друг, Коллега")}
            />
          </label>
          <label>
            Роль профиля
            <select
              value={profileForm.relation || "close_person"}
              onChange={(e) => setProfileForm({ ...profileForm, relation: e.target.value as AstroProfile["relation"] })}
            >
              {RELATION_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("account.astro.birthDate", "Дата рождения")} *
            <input
              type="date"
              value={profileForm.birth_date || ""}
              onChange={(e) => setProfileForm({ ...profileForm, birth_date: e.target.value })}
              required
              disabled={birthFactsFieldsLocked}
              style={birthFactsFieldsLocked ? { opacity: 0.65 } : undefined}
            />
          </label>
          <label>
            {t("account.astro.location", "Место рождения")} *
            <input
              type="text"
                value={profileForm.location_name || ""}
                onChange={(e) => setProfileForm({ ...profileForm, location_name: e.target.value })}
              required
              disabled={birthFactsFieldsLocked}
              style={birthFactsFieldsLocked ? { opacity: 0.65 } : undefined}
              placeholder={t("account.astro.locationPlaceholder", "Город, страна")}
            />
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)" }}>
            <input
              type="checkbox"
                checked={profileForm.time_unknown || false}
                onChange={(e) => setProfileForm({ ...profileForm, time_unknown: e.target.checked })}
              disabled={birthFactsFieldsLocked}
            />
            <span className="orbit-body-sm">{t("account.astro.timeUnknown", "Время рождения неизвестно")}</span>
          </label>
          {!profileForm.time_unknown && (
            <label>
              {t("account.astro.birthTime", "Время рождения")}
              <input
                type="time"
                value={profileForm.birth_time || ""}
                onChange={(e) => setProfileForm({ ...profileForm, birth_time: e.target.value })}
                disabled={birthFactsFieldsLocked}
                style={birthFactsFieldsLocked ? { opacity: 0.65 } : undefined}
              />
            </label>
          )}
          {profiles.length === 0 && (
            <label style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)" }}>
              <input
                type="checkbox"
                checked={profileForm.is_primary || false}
                onChange={(e) => setProfileForm({ ...profileForm, is_primary: e.target.checked })}
              />
              <span className="orbit-body-sm">{t("account.astro.setPrimary", "Сделать основным профилем")}</span>
            </label>
          )}
          <div style={{ display: "flex", gap: "var(--orbit-space-md)", marginTop: "var(--orbit-space-md)" }}>
            <button type="submit" disabled={profileSaving} className="orbit-button orbit-button-primary">
              {profileSaving ? t("account.saving", "Сохранение…") : editingId ? t("account.astro.update", "Обновить") : t("account.astro.add", "Добавить")}
            </button>
            {editingId && (
              <button
                type="button"
                className="orbit-button orbit-button-secondary"
                  onClick={() => {
                    setEditingId(null);
                    setProfileForm({ label: "", relation: "close_person", location_name: "", time_unknown: true });
                  }}
              >
                {t("account.astro.cancel", "Отмена")}
              </button>
            )}
          </div>
        </form>
      </div>
    </section>
  );
}
