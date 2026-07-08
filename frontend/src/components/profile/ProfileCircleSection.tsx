"use client";

import Link from "next/link";
import { ProfileExpandableSection } from "@/components/profile/ProfileExpandableSection";
import { profileCircleRoleHint, profileCircleRoleLabel, profileCircleRoute } from "@/components/profile/profileCircleHelpers";
import { ProfileSurfaceTile, profileSurfaceStyles } from "@/components/profile/ProfileSurface";
import { astroBirthFactsCaption } from "@/lib/accountAstroMeta";
import type { CompatibilityProfileLike } from "@/lib/compatibilityRoutes";

export type ProfileCircleSectionProps = {
  profileCircleItems: CompatibilityProfileLike[];
  primaryCircleProfileId: number | null | undefined;
  secondaryCircleItems: CompatibilityProfileLike[];
};

export function ProfileCircleSection({
  profileCircleItems,
  primaryCircleProfileId,
  secondaryCircleItems,
}: ProfileCircleSectionProps) {
  return (
    <ProfileExpandableSection
      id="profile-circle"
      title="Круг людей и значимые связи"
      subtitle="Профиль должен помнить не только тебя, но и тех, через кого чаще всего возникает реальный вопрос: партнер, ребенок, близкий человек."
    >
      <div style={{ display: "grid", gap: "0.8rem" }}>
        <ProfileSurfaceTile tone="soft">
          <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
            Как это читать
          </p>
          <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
            Ты остаешься главным корнем системы. Остальные профили не конкурируют с твоей картой, а добавляют второй слой там, где вопрос связан с конкретным человеком.
          </p>
        </ProfileSurfaceTile>

        {profileCircleItems.length ? (
          <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
            {profileCircleItems.map((item) => {
              const route = profileCircleRoute(item, primaryCircleProfileId);
              const birthFactsLine = astroBirthFactsCaption(item);
              return (
                <ProfileSurfaceTile
                  key={item.id}
                  className={item.is_primary ? profileSurfaceStyles.primaryRing : profileSurfaceStyles.secondaryRing}
                >
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
                    <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                      {item.label}
                    </p>
                    <span
                      className="orbit-body-xs"
                      style={{
                        padding: "0.24rem 0.55rem",
                        borderRadius: "999px",
                        background: item.is_primary ? "rgba(200,154,92,0.16)" : "rgba(15,23,42,0.06)",
                        color: item.is_primary ? "#8a6f49" : "#475569",
                        fontWeight: 700,
                      }}
                    >
                      {profileCircleRoleLabel(item)}
                    </span>
                  </div>
                  <p className="orbit-body-xs" style={{ margin: "0.38rem 0 0", color: "#64748b", lineHeight: 1.65 }}>
                    {item.birth_date ? new Date(item.birth_date).toLocaleDateString("ru-RU") : "Дата рождения появится после сборки"}
                    {item.location_name ? ` · ${item.location_name}` : ""}
                    {item.sun_sign ? ` · ${item.sun_sign}` : ""}
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.48rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                    {profileCircleRoleHint(item)}
                  </p>
                  {birthFactsLine ? (
                    <p className="orbit-body-xs" style={{ margin: "0.42rem 0 0", color: "#64748b", lineHeight: 1.65 }}>
                      {birthFactsLine}{" "}
                      <Link href="/profile" className="orbit-link-subtle" style={{ whiteSpace: "nowrap" }}>
                        Профиль →
                      </Link>
                    </p>
                  ) : null}
                  <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap", marginTop: "0.75rem" }}>
                    <Link href={route.href} className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                      {route.label}
                    </Link>
                    {item.is_primary ? null : (
                      <Link href="/account/profiles" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                        Управлять кругом
                      </Link>
                    )}
                  </div>
                </ProfileSurfaceTile>
              );
            })}
          </div>
        ) : (
          <ProfileSurfaceTile>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#475569", lineHeight: 1.7 }}>
              Пока здесь только твоя личная карта. Добавь партнера, ребенка или важного человека, чтобы профиль перестал быть изолированной схемой и начал работать с реальными отношениями.
            </p>
            <div style={{ marginTop: "0.75rem" }}>
              <Link href="/account/profiles" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                Открыть круг людей
              </Link>
            </div>
          </ProfileSurfaceTile>
        )}

        {secondaryCircleItems.length ? (
          <ProfileSurfaceTile tone="soft">
            <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
              Что уже открыто через круг
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
              Сейчас в системе есть {secondaryCircleItems.length}{" "}
              {secondaryCircleItems.length === 1
                ? "дополнительный профиль"
                : secondaryCircleItems.length < 5
                  ? "дополнительных профиля"
                  : "дополнительных профилей"}
              . Это значит, что вопросы про отношения, семью и близких уже можно читать не через абстрактный совет, а через конкретную пару или связь.
            </p>
          </ProfileSurfaceTile>
        ) : null}
      </div>
    </ProfileExpandableSection>
  );
}
