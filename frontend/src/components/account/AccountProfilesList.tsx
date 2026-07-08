"use client";

import Link from "next/link";
import { OrientationRail } from "@/components/orbit";
import { astroBirthFactsCaption } from "@/lib/accountAstroMeta";
import { t } from "@/lib/i18n";
import type { AstroProfile } from "@/lib/types";

interface AccountProfilesListProps {
  profiles: AstroProfile[];
  showContent: boolean;
  onSetPrimary: (profileId: number) => void;
  onPrefillFromAccount: (profile: AstroProfile) => void;
  onEdit: (profile: AstroProfile) => void;
  onDelete: (profileId: number) => void;
  onLogout?: () => void;
}

function relationLabel(relation: AstroProfile["relation"] | undefined, isPrimary: boolean) {
  if (isPrimary || relation === "self") return "Личный профиль";
  if (relation === "partner") return "Партнер";
  if (relation === "child") return "Ребенок";
  return "Близкий человек";
}

export function AccountProfilesList({
  profiles,
  showContent,
  onSetPrimary,
  onPrefillFromAccount,
  onEdit,
  onDelete,
  onLogout,
}: AccountProfilesListProps) {
  if (profiles.length === 0) return null;

  return (
    <section
      className="orbit-card"
      style={{
        marginTop: "var(--orbit-space-2xl)",
        opacity: showContent ? 1 : 0,
        transform: showContent ? "translateY(0)" : "translateY(30px)",
        transition: "opacity 0.8s ease 0.6s, transform 0.8s ease 0.6s",
      }}
    >
      <OrientationRail
        sectionLabel={t("account.orientation.section.profile", "Астро · Профиль")}
        metaLabel={t("account.orientation.meta.profile", "Учётная запись и настройки")}
      />
      <header style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-start", justifyContent: "space-between", gap: "var(--orbit-space-md)" }}>
        <div>
          <h2 className="orbit-display-sm" style={{ margin: 0 }}>{t("account.title", "My TodayFlow")}</h2>
          <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-xs)" }}>
            {t("account.subtitle", "Manage your user profile and stored birth data.")}
          </p>
        </div>
        <div style={{ display: "flex", gap: "var(--orbit-space-sm)", flexWrap: "wrap" }}>
          <Link href="/account/settings" className="orbit-link-subtle">
            {t("account.quickLinks.settings", "Настройки →")}
          </Link>
          <Link href="/account/subscriptions" className="orbit-link-subtle">
            {t("account.quickLinks.subscriptions", "Подписки →")}
          </Link>
          <Link href="/account/reports" className="orbit-link-subtle">
            {t("account.quickLinks.reports", "История разборов →")}
          </Link>
          <Link href="/onboarding/core" className="orbit-link-subtle">
            {t("account.quickLinks.birthChart", "Создать новый разбор →")}
          </Link>
          <button type="button" className="orbit-button orbit-button-secondary orbit-button-xs" onClick={onLogout}>
            {t("account.logout", "Выйти")}
          </button>
        </div>
      </header>

      <div style={{ marginTop: "var(--orbit-space-lg)" }}>
        <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
          {t("account.astro.profiles", "Астрологические профили")}
        </h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
          {profiles.map((profile) => {
            const birthFactsLine = astroBirthFactsCaption(profile);
            return (
            <div
              key={profile.id}
              style={{
                padding: "var(--orbit-space-md)",
                border: "1px solid var(--orbit-color-border)",
                borderRadius: "var(--orbit-radius-sm)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "var(--orbit-space-md)",
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)", marginBottom: "var(--orbit-space-xs)" }}>
                  <h4 className="orbit-body" style={{ fontWeight: 600, margin: 0 }}>
                    {profile.label}
                  </h4>
                  {profile.is_primary && (
                    <span className="orbit-badge-xs">{t("account.astro.primary", "Основной")}</span>
                  )}
                </div>
                <p className="orbit-body-sm orbit-text-muted">
                  {profile.birth_date && new Date(profile.birth_date).toLocaleDateString("ru-RU")}
                  {profile.location_name && ` · ${profile.location_name}`}
                </p>
                <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "0.35rem" }}>
                  {relationLabel(profile.relation, Boolean(profile.is_primary))}
                </p>
                {birthFactsLine ? (
                  <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "0.35rem", lineHeight: 1.55 }}>
                    {birthFactsLine}
                  </p>
                ) : null}
              </div>
              <div style={{ display: "flex", gap: "var(--orbit-space-sm)", flexWrap: "wrap" }}>
                {!profile.is_primary && (
                  <button
                    type="button"
                    className="orbit-button orbit-button-secondary orbit-button-xs"
                    onClick={() => onSetPrimary(profile.id)}
                  >
                    {t("account.astro.setPrimary", "Сделать основным")}
                  </button>
                )}
                <button
                  type="button"
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                  onClick={() => onPrefillFromAccount(profile)}
                >
                  {t("account.astro.useForIntake", "Использовать")}
                </button>
                <button
                  type="button"
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                  onClick={() => onEdit(profile)}
                >
                  {t("account.astro.edit", "Редактировать")}
                </button>
                <button
                  type="button"
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                  onClick={() => onDelete(profile.id)}
                  style={{ color: "var(--orbit-color-coral)" }}
                >
                  {t("account.astro.delete", "Удалить")}
                </button>
              </div>
            </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
