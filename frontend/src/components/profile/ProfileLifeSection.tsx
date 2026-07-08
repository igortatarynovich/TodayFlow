"use client";

import { ProfileExpandableSection } from "@/components/profile/ProfileExpandableSection";
import { profileSurfaceStyles } from "@/components/profile/ProfileSurface";

export type ProfileLifeSphere = {
  id: string;
  title: string;
  accent: string;
  how: string;
  need: string;
  risk: string;
  turnsOn: string;
  turnsOff: string;
  helps: string;
  practicalTips?: string[];
  inSystem: string;
};

export type ProfileLifeSectionProps = {
  spheres: ProfileLifeSphere[];
};

export function ProfileLifeSection({ spheres }: ProfileLifeSectionProps) {
  return (
    <ProfileExpandableSection
      id="profile-life-spheres"
      title="Сферы жизни"
      subtitle="Постоянные паттерны: как ты устроен, что нужно, где риск. Текст «как» для сферы при наличии карты может собираться из нескольких домов и планет — не дубль Personal Map. В Today, Guidance и Compatibility учитываются те же темы."
      defaultOpen
    >
      <div style={{ display: "grid", gap: "0.85rem" }}>
        {spheres.map((s) => (
          <details key={s.id} className={profileSurfaceStyles.nested}>
            <summary className={profileSurfaceStyles.nestedSummary}>
              <div>
                <p className="orbit-body-xs" style={{ margin: 0, color: s.accent, textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
                  {s.title}
                </p>
                <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#0f172a", fontWeight: 700, lineHeight: 1.5 }}>
                  {s.how}
                </p>
              </div>
              <span className={`orbit-body-xs ${profileSurfaceStyles.nestedToggle}`}>Подробнее</span>
            </summary>
            <div style={{ marginTop: "0.85rem", display: "grid", gap: "0.65rem" }}>
              <div>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                  Что тебе нужно
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                  {s.need}
                </p>
              </div>
              <div>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                  Где твой риск
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                  {s.risk}
                </p>
              </div>
              <div style={{ display: "grid", gap: "0.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
                <div>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                    Что тебя включает
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                    {s.turnsOn}
                  </p>
                </div>
                <div>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                    Что тебя выключает
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                    {s.turnsOff}
                  </p>
                </div>
              </div>
              <div>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                  Что помогает
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                  {s.helps}
                </p>
              </div>
              {s.practicalTips && s.practicalTips.length > 0 ? (
                <div>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                    Практические подсказки
                  </p>
                  <ul className="orbit-body-xs" style={{ margin: "0.35rem 0 0", paddingLeft: "1.1rem", color: "#475569", lineHeight: 1.65 }}>
                    {s.practicalTips.map((tip) => (
                      <li key={tip}>{tip}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              <div
                style={{
                  padding: "0.75rem",
                  borderRadius: "14px",
                  background: "rgba(250, 244, 234, 0.85)",
                  border: "1px solid rgba(184, 144, 88, 0.14)",
                }}
              >
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                  Что учтём в Today / Guidance / Compatibility
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                  {s.inSystem}
                </p>
              </div>
            </div>
          </details>
        ))}
      </div>
    </ProfileExpandableSection>
  );
}
