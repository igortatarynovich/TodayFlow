"use client";

import Link from "next/link";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";
import { ProfileExpandableSection } from "@/components/profile/ProfileExpandableSection";
import { aspectCategoryLabel } from "@/components/profile/profileAspectLabels";
import type { CombinedPlanetaryProfile } from "@/components/profile/profilePanelTypes";
import { natalBodyLabelRu } from "@/lib/profileAstroLabelsRu";
import type { LifePathEntry } from "@/lib/zodiacKnowledge";
import { ProfileSurfacePanel, profileSurfaceStyles } from "@/components/profile/ProfileSurface";

export type ProfileSynthesisSectionProps = {
  showNumerologyBanner: boolean;
  combinedPlanetaryProfile: CombinedPlanetaryProfile | null;
  lifePathLayer: LifePathEntry | null | undefined;
};

export function ProfileSynthesisSection({
  showNumerologyBanner,
  combinedPlanetaryProfile,
  lifePathLayer,
}: ProfileSynthesisSectionProps) {
  return (
      <>
        {showNumerologyBanner ? (
          <ProfileSurfacePanel variant="warm" eyebrow="Нумерология">
            <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#5f4323" }}>
              Нумерология читается здесь как часть ядра
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7c6242", lineHeight: 1.7 }}>
              Число пути и связанные числа не живут отдельно от профиля. Они уточняют твой жизненный сценарий, ритм решений и способ проявления рядом с натальной базой, а не вместо неё.
            </p>
          </ProfileSurfacePanel>
        ) : null}
    
        <ProfileExpandableSection
      title="Планеты и синтез"
      subtitle="Одна связная линия: не перечень планет, а то, как качества складываются в поведение и выбор."
      defaultOpen
    >
      {combinedPlanetaryProfile ? (
        <div style={{ display: "grid", gap: "0.9rem" }}>
          <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap" }}>
            {combinedPlanetaryProfile.placements.map((item) => (
              <span
                key={item.key}
                className="orbit-body-xs"
                style={{
                  padding: "0.42rem 0.68rem",
                  borderRadius: "999px",
                  border: "1px solid rgba(184, 144, 88, 0.24)",
                  background: "rgba(255,255,255,0.82)",
                  color: "#6b4f2b",
                  fontWeight: 700,
                }}
              >
                {natalBodyLabelRu(item.label)} → {item.signLabel}
              </span>
            ))}
          </div>
    
          <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
            <div className={profileSurfaceStyles.tile}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Узнавание
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                {combinedPlanetaryProfile.recognition}
              </p>
            </div>
            <div className={profileSurfaceStyles.tile}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Синтез
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                {combinedPlanetaryProfile.explanation}
              </p>
            </div>
            <div className={profileSurfaceStyles.tile}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Где внутренний конфликт
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                {combinedPlanetaryProfile.tension}
              </p>
            </div>
            <div className={profileSurfaceStyles.tile}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Где сила
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                {combinedPlanetaryProfile.strength}
              </p>
            </div>
          </div>
    
          <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Как это проявляется в жизни</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.manifestation}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Где риск</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.risk}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Через что ты это живешь</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.lifeVector}
              </p>
              {lifePathLayer?.driver ? (
                <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.7 }}>
                  {lifePathLayer.driver}
                </p>
              ) : null}
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Как это видно снаружи</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.expressionLine}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Как ты думаешь и говоришь</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.mind}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Как ты входишь в мир</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.firstContact}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Где идет рост</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.growthLine}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Что тебя ограничивает</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.constraintLine}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Где твой бунт</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.rebellionLine}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Где магия и туман</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.magicLine}
              </p>
            </div>
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSoft].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>Где идет глубокая трансформация</p>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {combinedPlanetaryProfile.transformationLine}
              </p>
            </div>
          </div>
    
          {lifePathLayer && (lifePathLayer.relationships?.length || lifePathLayer.money_work?.length || lifePathLayer.lesson || lifePathLayer.main_fear) ? (
            <div id="profile-numerology" className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileLg].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                Что число пути добавляет в твой профиль
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#64748b", lineHeight: 1.65 }}>
                Это не отдельная нумерология. Это жизненный сценарий, через который ты проживаешь уже видимые астрологические качества.
              </p>
              <div style={{ display: "grid", gap: "0.75rem", marginTop: "0.85rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
                {lifePathLayer.relationships?.length ? (
                  <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSm, profileSurfaceStyles.tileSolid].join(" ")}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      В отношениях
                    </p>
                    <div style={{ display: "grid", gap: "0.32rem", marginTop: "0.45rem" }}>
                      {lifePathLayer.relationships.slice(0, 3).map((item) => (
                        <p key={item} className="orbit-body-xs" style={{ margin: 0, color: "#334155", lineHeight: 1.65 }}>
                          • {item}
                        </p>
                      ))}
                    </div>
                  </div>
                ) : null}
                {lifePathLayer.money_work?.length ? (
                  <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSm, profileSurfaceStyles.tileSolid].join(" ")}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      В деньгах и работе
                    </p>
                    <div style={{ display: "grid", gap: "0.32rem", marginTop: "0.45rem" }}>
                      {lifePathLayer.money_work.slice(0, 3).map((item) => (
                        <p key={item} className="orbit-body-xs" style={{ margin: 0, color: "#334155", lineHeight: 1.65 }}>
                          • {item}
                        </p>
                      ))}
                    </div>
                  </div>
                ) : null}
                {lifePathLayer.main_fear ? (
                  <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSm, profileSurfaceStyles.tileSolid].join(" ")}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      Главный страх
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.7 }}>
                      {lifePathLayer.main_fear}
                    </p>
                  </div>
                ) : null}
                {lifePathLayer.lesson ? (
                  <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSm, profileSurfaceStyles.tileSolid].join(" ")}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      Главный урок
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.7 }}>
                      {lifePathLayer.lesson}
                    </p>
                  </div>
                ) : null}
              </div>
            </div>
          ) : null}
    
          {combinedPlanetaryProfile.manifestationAreas.length ? (
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileLg].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                Где это проявляется в жизни
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#64748b", lineHeight: 1.65 }}>
                Дома отвечают не на вопрос “какой ты”, а на вопрос “где именно это у тебя происходит”.
              </p>
              <div style={{ display: "grid", gap: "0.7rem", marginTop: "0.85rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
                {combinedPlanetaryProfile.manifestationAreas.map((item) => (
                  <div
                    key={`${item.planet}-${item.house}`}
                    style={{
                      border: "1px solid rgba(184, 144, 88, 0.18)",
                      borderRadius: "16px",
                      padding: "0.85rem",
                      background: "rgba(255,255,255,0.88)",
                    }}
                  >
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      {natalBodyLabelRu(item.planet)} · {item.house} дом
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.32rem 0 0", fontWeight: 700, color: "#0f172a" }}>
                      {item.houseTitle}
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.36rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                      {item.text}
                    </p>
                  </div>
                ))}
              </div>
              {combinedPlanetaryProfile.houseFocus ? (
                <div
                  style={{
                    marginTop: "0.85rem",
                    border: "1px solid rgba(184, 144, 88, 0.18)",
                    borderRadius: "16px",
                    padding: "0.9rem",
                    background: "rgba(250, 244, 234, 0.82)",
                  }}
                >
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    Где у тебя многое происходит
                  </p>
                  <p className="orbit-body-sm" style={{ margin: "0.34rem 0 0", fontWeight: 700, color: "#0f172a" }}>
                    {combinedPlanetaryProfile.houseFocus.title}
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.36rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                    {combinedPlanetaryProfile.houseFocus.text}
                  </p>
                </div>
              ) : null}
            </div>
          ) : null}
    
          {combinedPlanetaryProfile.scenarios.length ? (
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileLg].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                Почему это у тебя повторяется
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#64748b", lineHeight: 1.65 }}>
                Это не общий список проблем. Это сценарии, которые могут удерживаться именно твоей комбинацией планет, аспектов и домов.
              </p>
              <div style={{ display: "grid", gap: "0.75rem", marginTop: "0.85rem" }}>
                {combinedPlanetaryProfile.scenarios.map((scenario) => (
                  <div
                    key={scenario.id}
                    style={{
                      border: "1px solid rgba(184, 144, 88, 0.18)",
                      borderRadius: "18px",
                      padding: "0.95rem",
                      background: "rgba(255,255,255,0.9)",
                    }}
                  >
                    <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                      {scenario.title}
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.38rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                      {scenario.summary}
                    </p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem", marginTop: "0.7rem" }}>
                      {scenario.evidence.slice(0, 3).map((item) => (
                        <span
                          key={item}
                          className="orbit-body-xs"
                          style={{
                            padding: "0.38rem 0.62rem",
                            borderRadius: "999px",
                            background: "rgba(250, 244, 234, 0.95)",
                            border: "1px solid rgba(184, 144, 88, 0.16)",
                            color: "#7b6140",
                          }}
                        >
                          {item}
                        </span>
                      ))}
                    </div>
                    <div style={{ display: "grid", gap: "0.35rem", marginTop: "0.75rem" }}>
                      {scenario.bullets.map((bullet) => (
                        <p key={bullet} className="orbit-body-xs" style={{ margin: 0, color: "#334155", lineHeight: 1.65 }}>
                          • {bullet}
                        </p>
                      ))}
                    </div>
                    {scenario.reading.length ? (
                      <div
                        style={{
                          marginTop: "0.8rem",
                          padding: "0.8rem",
                          borderRadius: "16px",
                          background: "rgba(250, 244, 234, 0.85)",
                          border: "1px solid rgba(184, 144, 88, 0.16)",
                        }}
                      >
                        <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                          Как это читается
                        </p>
                        <div style={{ display: "grid", gap: "0.35rem", marginTop: "0.45rem" }}>
                          {scenario.reading.map((line) => (
                            <p key={line} className="orbit-body-xs" style={{ margin: 0, color: "#334155", lineHeight: 1.7 }}>
                              {line}
                            </p>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {scenario.layers.length ? (
                      <div style={{ display: "grid", gap: "0.55rem", marginTop: "0.8rem" }}>
                        {scenario.layers.map((layer) => (
                          <div
                            key={`${scenario.id}-${layer.label}`}
                            style={{
                              border: "1px solid rgba(184, 144, 88, 0.14)",
                              borderRadius: "14px",
                              padding: "0.75rem",
                              background: "rgba(255,255,255,0.82)",
                            }}
                          >
                            <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                              {layer.label}
                            </p>
                            <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                              {layer.reason}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
    
          {combinedPlanetaryProfile.aspectInsights.length ? (
            <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileLg].join(" ")}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                Где ты цельный, а где споришь с собой
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#64748b", lineHeight: 1.65 }}>
                Аспекты показывают, где части тебя сливаются в одно поведение, где дают напряжение, а где создают врожденную силу.
              </p>
              {combinedPlanetaryProfile.aspectSummary ? (
                <div style={{ display: "grid", gap: "0.75rem", marginTop: "0.85rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
                  <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSolid].join(" ")}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      Где ты цельный
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                      {combinedPlanetaryProfile.aspectSummary.coherence}
                    </p>
                  </div>
                  <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSolid].join(" ")}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      Где внутренний конфликт
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                      {combinedPlanetaryProfile.aspectSummary.conflict}
                    </p>
                  </div>
                  <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSolid].join(" ")}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      Где врожденная сила
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                      {combinedPlanetaryProfile.aspectSummary.advantage}
                    </p>
                  </div>
                  <div className={[profileSurfaceStyles.tile, profileSurfaceStyles.tileSolid].join(" ")}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      Где ты сам себе мешаешь
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                      {combinedPlanetaryProfile.aspectSummary.selfBlock}
                    </p>
                  </div>
                </div>
              ) : null}
              <div style={{ display: "grid", gap: "0.7rem", marginTop: "0.85rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
                {combinedPlanetaryProfile.aspectInsights.map((item) => (
                  <div
                    key={item.key}
                    style={{
                      border: "1px solid rgba(184, 144, 88, 0.18)",
                      borderRadius: "16px",
                      padding: "0.85rem",
                      background: "rgba(255,255,255,0.88)",
                    }}
                  >
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      {aspectCategoryLabel(item.category)}
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.32rem 0 0", fontWeight: 700, color: "#0f172a" }}>
                      {item.title}
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#8f7756", lineHeight: 1.55 }}>
                      {item.bodies}
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.36rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                      {item.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      ) : (
        <div
          style={{
            border: "1px dashed rgba(143,119,86,0.3)",
            borderRadius: "18px",
            padding: "1rem",
            background: "rgba(255,255,255,0.7)",
          }}
        >
          <p className="orbit-body-sm" style={{ margin: 0, color: "#475569", lineHeight: 1.7 }}>
            Здесь собирается связный рассказ из четырёх опор: Солнце, Луна, Венера и Марс в знаках. Если блок пустой,
            в ответе карты ещё нет всех четырёх тел (часто так бывает при неизвестном времени рождения — без него Луна не
            строится). Уточни время в{" "}
            <Link href="/onboarding/core" style={{ color: "#a67c3a", fontWeight: 700 }}>
              настройках профиля
            </Link>{" "}
            или открой{" "}
            <Link href={PROFILE_CHART_DEEP_PATH} style={{ color: "#a67c3a", fontWeight: 700 }}>
              полную натальную карту
            </Link>
            .
          </p>
        </div>
      )}
    </ProfileExpandableSection>
      </>

  );
}
