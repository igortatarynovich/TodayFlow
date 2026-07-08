"use client";

import { useState } from "react";
import { t } from "@/lib/i18n";
import Link from "next/link";
import { FullReportUpsell } from "./FullReportUpsell";

interface SystemItem {
  title: string;
  description: string;
  explanation?: string; // Что это значит для пользователя
}

interface SystemContent {
  items?: SystemItem[];
  text?: string;
}

interface System {
  id: string;
  name: string;
  description: string;
  content?: SystemContent;
  cta?: {
    text: string;
    href: string;
  };
}

interface SystemsProps {
  houses?: Record<string, any>;
  houseReferences?: Array<{ id: string; name: string; number?: number }>;
  aspects?: Array<{ planet1: string; planet2: string; type: string; meaning: string }>;
  weeklyInsight?: any;
  zodiacReferences?: Array<{ id: string; stones?: string[] }>;
  sun?: string;
  moon?: string;
  rising?: string;
  isGuest?: boolean;
  hasFullReport?: boolean;
}

export function Systems({
  houses,
  houseReferences,
  aspects,
  weeklyInsight,
  zodiacReferences,
  sun,
  moon,
  rising,
  isGuest = false,
  hasFullReport = false,
}: SystemsProps) {
  const [openSystem, setOpenSystem] = useState<string | null>(null);

  // Собираем ключевые аспекты (3-5)
  const keyAspects: SystemItem[] = [];
  if (aspects && aspects.length > 0) {
    aspects.slice(0, 5).forEach((aspect) => {
      keyAspects.push({
        title: `${aspect.planet1} — ${aspect.planet2}`,
        description: `${aspect.type}: ${aspect.meaning}`,
      });
    });
  }

  // Камни для знаков
  const stones: SystemItem[] = [];
  if (zodiacReferences && (sun || moon || rising)) {
    const signs = [sun, moon, rising].filter(Boolean);
    signs.forEach((sign) => {
      const zodiac = zodiacReferences.find((z) => z?.id && sign && z.id.toLowerCase() === sign.toLowerCase());
      if (zodiac?.stones && zodiac.stones.length > 0 && stones.length < 3) {
        stones.push({
          title: zodiac.stones[0],
          description: t("systems.stones.forSign", "Для") + ` ${sign}`,
        });
      }
    });
  }

  const systems: System[] = [
    {
      id: "aspects",
      name: t("systems.aspects.name", "Взаимодействие энергий"),
      description: t("systems.aspects.description", "Связи между планетами, усиливающие или смягчающие проявления."),
      content: {
        items: keyAspects,
      },
    },
    {
      id: "cycles",
      name: t("systems.cycles.name", "Текущие циклы"),
      description: t("systems.cycles.description", "В какие периоды ты входишь сейчас и почему это ощущается именно так."),
      content: weeklyInsight ? {
        text: weeklyInsight.insight?.summary || weeklyInsight.insight?.title || t("systems.cycles.defaultText", "Текущий период активности"),
      } : undefined,
      cta: weeklyInsight ? {
        text: t("systems.cycles.cta", "Посмотреть, как это влияет сегодня"),
        href: "/today",
      } : undefined,
    },
    {
      id: "stones",
      name: t("systems.stones.name", "Поддерживающие ресурсы"),
      description: t("systems.stones.description", "Символические опоры для стабилизации и фокуса."),
      content: {
        items: stones,
      },
    },
  ].filter((system) => {
    // Показываем только системы с контентом
    if (isGuest) return true; // Для гостей показываем все, но с blur
    if (!system.content) return false;
    return (system.content.items && system.content.items.length > 0) || !!system.content.text;
  });

  if (systems.length === 0) {
    return null;
  }

  return (
    <section
      id="systems"
      style={{
        marginBottom: "var(--orbit-space-3xl)",
        paddingTop: "var(--orbit-space-2xl)",
      }}
    >
      <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
        <h2
          className="orbit-display-sm"
          style={{
            fontSize: "clamp(1.5rem, 3vw, 2rem)",
            marginBottom: "var(--orbit-space-sm)",
            color: "#0f172a",
            fontWeight: 500,
          }}
        >
          {t("systems.title", "Системы и расчёты")}
        </h2>
        <p
          className="orbit-body"
          style={{
            color: "#334155",
            lineHeight: 1.6,
          }}
        >
          {t("systems.subtitle", "Здесь — то, на чём строится твоя персональная карта.")}
        </p>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "var(--orbit-space-sm)",
        }}
      >
        {systems.map((system) => {
          const isOpen = openSystem === system.id;
          const hasContent = system.content && ((system.content.items && system.content.items.length > 0) || !!system.content.text);

          return (
            <details
              key={system.id}
              open={isOpen}
              onToggle={(e) => {
                const target = e.currentTarget;
                setOpenSystem(target.open ? system.id : null);
              }}
              style={{
                border: "1px solid #e5e0d8",
                borderRadius: "var(--orbit-radius-md)",
                background: "#ffffff",
                overflow: "hidden",
              }}
            >
              <summary
                style={{
                  padding: "var(--orbit-space-lg)",
                  cursor: "pointer",
                  listStyle: "none",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  transition: "background 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "#f5f5f0";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "#ffffff";
                }}
              >
                <div>
                  <h3
                    className="orbit-body"
                    style={{
                      fontWeight: 600,
                      color: "#0f172a",
                      marginBottom: "var(--orbit-space-xs)",
                    }}
                  >
                    {system.name}
                  </h3>
                  <p
                    className="orbit-body-sm orbit-text-muted"
                    style={{
                      lineHeight: 1.6,
                    }}
                  >
                    {system.description}
                  </p>
                </div>
                <span
                  style={{
                    fontSize: "1.5rem",
                    color: "#6b7280",
                    transition: "transform 0.2s ease",
                    transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
                  }}
                >
                  ▼
                </span>
              </summary>

              {isOpen && (
                <div
                  style={{
                    padding: "var(--orbit-space-lg)",
                    paddingTop: 0,
                    borderTop: "1px solid #e5e0d8",
                  }}
                >
                  {isGuest ? (
                    <div
                      style={{
                        padding: "var(--orbit-space-lg)",
                        background: "#f5f5f0",
                        borderRadius: "var(--orbit-radius-sm)",
                        position: "relative",
                        filter: "blur(4px)",
                        pointerEvents: "none",
                      }}
                    >
                      <p className="orbit-body-sm orbit-text-muted">
                        {t("systems.guest.message", "Это станет точнее, если ты введёшь данные рождения.")}
                      </p>
                    </div>
                  ) : hasContent ? (
                    <>
                      {system.content?.items && system.content.items.length > 0 && (
                        <div
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "var(--orbit-space-lg)",
                            marginBottom: system.cta ? "var(--orbit-space-lg)" : 0,
                          }}
                        >
                          {system.content.items.map((item, i) => (
                            <div 
                              key={i}
                              style={{
                                padding: "var(--orbit-space-md)",
                                background: "#f5f5f0",
                                borderRadius: "var(--orbit-radius-sm)",
                              }}
                            >
                              <h4
                                className="orbit-body-sm"
                                style={{
                                  fontWeight: 600,
                                  color: "#0f172a",
                                  marginBottom: "var(--orbit-space-xs)",
                                }}
                              >
                                {item.title}
                              </h4>
                              <p
                                className="orbit-body-xs orbit-text-muted"
                                style={{
                                  lineHeight: 1.6,
                                  marginBottom: item.explanation ? "var(--orbit-space-sm)" : 0,
                                }}
                              >
                                {item.description}
                              </p>
                              {item.explanation && (
                                <div
                                  style={{
                                    marginTop: "var(--orbit-space-sm)",
                                    paddingTop: "var(--orbit-space-sm)",
                                    borderTop: "1px solid #e5e0d8",
                                  }}
                                >
                                  <p
                                    className="orbit-body-xs"
                                    style={{
                                      color: "#334155",
                                      lineHeight: 1.6,
                                      fontStyle: "italic",
                                    }}
                                  >
                                    {item.explanation}
                                  </p>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                      {system.content?.text && (
                        <p
                          className="orbit-body-sm"
                          style={{
                            color: "#334155",
                            lineHeight: 1.6,
                            marginBottom: system.cta ? "var(--orbit-space-lg)" : 0,
                          }}
                        >
                          {system.content.text}
                        </p>
                      )}
                      {system.cta && (
                        <Link
                          href={system.cta.href}
                          className="orbit-button orbit-button-primary orbit-button-sm"
                          style={{
                            textDecoration: "none",
                            display: "inline-block",
                          }}
                        >
                          {system.cta.text} →
                        </Link>
                      )}
                      {/* МОНЕТИЗАЦИЯ: Апселл Full Report после раскрытия accordion */}
                      {!isGuest && (
                        <FullReportUpsell
                          context="system"
                          hasFullReport={hasFullReport}
                        />
                      )}
                    </>
                  ) : (
                    <p className="orbit-body-sm orbit-text-muted">
                      {t("systems.noData", "Данные для этой системы пока не доступны.")}
                    </p>
                  )}

                  {isGuest && (
                    <div style={{ marginTop: "var(--orbit-space-md)" }}>
                      <Link
                        href="/onboarding/core"
                        className="orbit-button orbit-button-secondary orbit-button-sm"
                        style={{
                          textDecoration: "none",
                          display: "inline-block",
                        }}
                      >
                        {t("systems.guest.cta", "Рассчитать мою карту →")}
                      </Link>
                    </div>
                  )}
                </div>
              )}
            </details>
          );
        })}
      </div>
    </section>
  );
}
