"use client";

import { ProfileExpandableSection } from "@/components/profile/ProfileExpandableSection";
import { ProfileSurfaceTile } from "@/components/profile/ProfileSurface";

export type ProfileOverviewExpandablesProps = {
  profileGuidance: string[];
  strengths: string[];
  cautions: string[];
  workingRules: string[];
};

export function ProfileOverviewExpandables({ profileGuidance, strengths, cautions, workingRules }: ProfileOverviewExpandablesProps) {
  return (
    <>
      <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
        <ProfileSurfaceTile tone="solid">
          <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
            На что опираться
          </p>
          <ul style={{ margin: "0.55rem 0 0", paddingLeft: "1rem", color: "#334155", lineHeight: 1.7 }}>
            {strengths.slice(0, 3).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </ProfileSurfaceTile>
        <ProfileSurfaceTile tone="solid">
          <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
            Где чаще теряешь себя
          </p>
          <ul style={{ margin: "0.55rem 0 0", paddingLeft: "1rem", color: "#334155", lineHeight: 1.7 }}>
            {cautions.slice(0, 3).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </ProfileSurfaceTile>
        <ProfileSurfaceTile tone="solid">
          <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
            Что система учитывает в подсказках
          </p>
          <ul style={{ margin: "0.55rem 0 0", paddingLeft: "1rem", color: "#334155", lineHeight: 1.7 }}>
            {workingRules.slice(0, 3).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </ProfileSurfaceTile>
      </div>

      {profileGuidance.length > 1 ? (
        <ProfileExpandableSection
          id="profile-portrait-more"
          title="Подробнее: как это складывается"
          subtitle="Развёрнутые строки из ядра профиля — если хочешь уйти глубже одного абзаца."
          defaultOpen={false}
        >
          <div style={{ display: "grid", gap: "0.65rem" }}>
            {profileGuidance.map((item) => (
              <ProfileSurfaceTile key={item} tone="outline">
                <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.7 }}>
                  {item}
                </p>
              </ProfileSurfaceTile>
            ))}
          </div>
        </ProfileExpandableSection>
      ) : null}
    </>
  );
}
