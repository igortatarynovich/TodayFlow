"use client";

import { buildNumerologySignatureCards } from "@/components/profile/profileNumerologySignature";
import type { ProfileSectionId } from "@/components/profile/profileSections";
import { ProfileMobileStatCard } from "@/components/profile/ProfileMobileStatCard";
import { ProfileSurfacePanel, ProfileSurfaceTile } from "@/components/profile/ProfileSurface";
import type { CoreProfile } from "@/lib/types";

export type ProfileOverviewIntroProps = {
  displayName: string;
  birthDateLabel: string;
  moonLabel: string;
  sunSign: string;
  risingSign?: string | null;
  lifePath: number | null | undefined;
  coreNumerology?: CoreProfile["numerology"] | null;
  archetypeSeed: string;
  rhythmStyle: string;
  sunElementHint?: string | null;
  risingHint?: string | null;
  synthesisParagraph: string;
  onGoRhythm: (id: ProfileSectionId) => void;
};

export function ProfileOverviewIntro({
  displayName,
  birthDateLabel,
  moonLabel,
  sunSign,
  risingSign,
  lifePath,
  coreNumerology,
  archetypeSeed,
  rhythmStyle,
  sunElementHint,
  risingHint,
  synthesisParagraph,
  onGoRhythm,
}: ProfileOverviewIntroProps) {
  const numerologyStrip = buildNumerologySignatureCards(coreNumerology);
  const showFullNumerology = numerologyStrip.length > 0;
  const rhythmReadable =
    rhythmStyle && rhythmStyle !== "Ритм проявится после сборки" ? rhythmStyle : null;

  return (
    <>
      <ProfileSurfacePanel eyebrow="Портрет" panelClass="portrait">
        <p className="orbit-display-sm" style={{ margin: "0.15rem 0 0", color: "#0f172a", fontWeight: 700, lineHeight: 1.25 }}>
          {displayName}
        </p>
        <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#64748b" }}>
          {birthDateLabel}
        </p>
        <div style={{ marginTop: "0.85rem", display: "grid", gap: "0.65rem", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
          <ProfileMobileStatCard label="Знак" value={sunSign} hint={sunElementHint || "Солнечный знак — базовая подача и мотивация."} />
          <ProfileMobileStatCard label="Луна" value={moonLabel} hint="Как ты чувствуешь и восстанавливаешься." />
          <ProfileMobileStatCard
            label="Асцендент"
            value={risingSign || "Не определён"}
            hint={risingHint || "Точнее с надёжным временем рождения."}
          />
          {!showFullNumerology ? (
            <ProfileMobileStatCard label="Число пути" value={lifePath != null ? String(lifePath) : "—"} hint="Линия решений и повторяющихся задач." />
          ) : null}
          <ProfileMobileStatCard label="Архетип" value={archetypeSeed} hint="Якорь личности рядом с картой." />
          {rhythmReadable ? <ProfileMobileStatCard label="Ритм" value={rhythmReadable} hint="Как тебе проще держать день без перегруза." /> : null}
        </div>
        <div style={{ marginTop: "0.75rem", display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => onGoRhythm("chart")}>
            Карта рождения
          </button>
          <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => onGoRhythm("pulse")}>
            Живой слой
          </button>
        </div>
      </ProfileSurfacePanel>

      <ProfileSurfacePanel eyebrow="Кто ты в этой системе" panelClass="plain">
        <p className="orbit-body-sm" style={{ margin: 0, color: "#1e293b", lineHeight: 1.75 }}>
          {synthesisParagraph}
        </p>
      </ProfileSurfacePanel>

      {showFullNumerology ? (
        <ProfileSurfacePanel eyebrow="Числа рождения" panelClass="numerology">
          <p className="orbit-body-xs" style={{ margin: 0, color: "#64748b", lineHeight: 1.65 }}>
            Путь, имя, внутренняя линия, подача и личный год — как они влияют на решения, отношения и ритм.
          </p>
          <div
            style={{
              display: "grid",
              gap: "0.6rem",
              gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
              marginTop: "0.75rem",
            }}
          >
            {numerologyStrip.map((item) => (
              <ProfileSurfaceTile key={item.key} tone="numerology">
                <p className="orbit-body-xs" style={{ margin: 0, color: "#7c6a94", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700 }}>
                  {item.label}
                </p>
                <p className="orbit-body-sm" style={{ margin: "0.3rem 0 0", color: "#0f172a", fontWeight: 700 }}>
                  {item.value}
                </p>
                {item.hint ? (
                  <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#64748b" }}>
                    {item.hint}
                  </p>
                ) : null}
              </ProfileSurfaceTile>
            ))}
          </div>
          <div style={{ marginTop: "0.75rem" }}>
            <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => onGoRhythm("chart")}>
              Открыть карту рождения
            </button>
          </div>
        </ProfileSurfacePanel>
      ) : null}
    </>
  );
}
