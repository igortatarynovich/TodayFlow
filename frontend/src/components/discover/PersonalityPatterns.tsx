"use client";

import { useState } from "react";
import Link from "next/link";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";
import { FullReportUpsell } from "./FullReportUpsell";
import { t } from "@/lib/i18n";

interface Axis {
  axis_id: string;
  value: number;
  confidence?: string;
}

interface PersonalityPatternsProps {
  axes: Axis[];
  isGuest?: boolean;
  hasFullReport?: boolean;
}

const axisNames: Record<string, string> = {
  A1: "Ориентация идентичности",
  A2: "Выражение эмоций",
  A3: "Принятие решений",
  A4: "Отношение к изменениям",
  A5: "Стиль контроля",
  A6: "Ориентация в отношениях",
  A7: "Управление энергией",
};

const axisPoles: Record<string, { left: string; right: string }> = {
  A1: { left: "Внутренняя ориентация", right: "Внешняя ориентация" },
  A2: { left: "Сдержанный", right: "Экспрессивный" },
  A3: { left: "Интуитивный", right: "Аналитический" },
  A4: { left: "Стабильность", right: "Изменения" },
  A5: { left: "Адаптивный", right: "Директивный" },
  A6: { left: "Независимый", right: "Ориентированный на связи" },
  A7: { left: "Консервативный", right: "Экспансивный" },
};

export function PersonalityPatterns({ axes, isGuest = false, hasFullReport = false }: PersonalityPatternsProps) {
  const [expandedAxis, setExpandedAxis] = useState<string | null>(null);

  if (!axes || axes.length === 0) {
    return null;
  }

  // Сортируем оси по выраженности (абсолютное значение)
  const sortedAxes = [...axes]
    .map((axis) => ({ ...axis, absValue: Math.abs(axis.value) }))
    .sort((a, b) => b.absValue - a.absValue);

  // Топ 2-3 доминирующие
  const dominantAxes = sortedAxes.slice(0, 3);
  const secondaryAxes = sortedAxes.slice(3);

  const getPole = (axis: Axis): string => {
    const poles = axisPoles[axis.axis_id];
    if (!poles) return "";
    return axis.value > 0 ? poles.right : poles.left;
  };

  const getPosition = (value: number): number => {
    // Нормализуем от -100/+100 к 0-100 для позиции на оси
    return ((value + 100) / 200) * 100;
  };

  const renderAxisCard = (axis: Axis, isDominant: boolean) => {
    const isExpanded = expandedAxis === axis.axis_id;
    const pole = getPole(axis);
    const position = getPosition(axis.value);

    return (
      <div
        key={axis.axis_id}
        className="orbit-card"
        style={{
          padding: isDominant ? "var(--orbit-space-xl)" : "var(--orbit-space-lg)",
          background: "#ffffff",
          border: isExpanded ? "2px solid #b87333" : "1px solid #e5e0d8",
          borderRadius: "var(--orbit-radius-md)",
          marginBottom: "var(--orbit-space-md)",
          cursor: isGuest ? "default" : "pointer",
          transition: "all 0.2s ease",
        }}
        onClick={() => !isGuest && setExpandedAxis(isExpanded ? null : axis.axis_id)}
      >
        {/* Название оси */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: "var(--orbit-space-md)",
          }}
        >
          <h3
            className={isDominant ? "orbit-body" : "orbit-body-sm"}
            style={{
              fontWeight: isDominant ? 600 : 500,
              color: "#0f172a",
            }}
          >
            {axisNames[axis.axis_id] || axis.axis_id}
          </h3>
        </div>

        {/* Визуальная ось */}
        {!isGuest ? (
          <div style={{ marginBottom: "var(--orbit-space-md)" }}>
            <div
              style={{
                position: "relative",
                height: "8px",
                background: "#e5e0d8",
                borderRadius: "4px",
                marginBottom: "var(--orbit-space-sm)",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  left: `${position}%`,
                  top: "50%",
                  transform: "translate(-50%, -50%)",
                  width: "16px",
                  height: "16px",
                  background: "#b87333",
                  borderRadius: "50%",
                  border: "2px solid #ffffff",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                }}
              />
            </div>
            <p
              className="orbit-body-xs orbit-text-muted"
              style={{ textAlign: "center" }}
            >
              Сейчас ты ближе к: <strong>{pole}</strong>
            </p>
          </div>
        ) : (
          <p
            className="orbit-body-xs orbit-text-muted"
            style={{
              padding: "var(--orbit-space-md)",
              background: "#f5f5f0",
              borderRadius: "var(--orbit-radius-sm)",
              textAlign: "center",
            }}
          >
            {t("personalityPatterns.calculatedAfter", "Рассчитывается после ввода данных")}
          </p>
        )}

        {/* Короткая интерпретация */}
        {!isGuest && (
          <p
            className="orbit-body-sm"
            style={{
              color: "#334155",
              lineHeight: 1.6,
              marginBottom: isExpanded ? "var(--orbit-space-lg)" : 0,
            }}
          >
            {axis.value > 0.5
              ? `Ты склонен определять себя через обратную связь и реакции других.`
              : axis.value < -0.5
              ? `Ты склонен опираться на внутренние ориентиры и собственные ценности.`
              : `Ты балансируешь между внутренними и внешними ориентирами.`}
          </p>
        )}

        {/* Раскрытие с деталями */}
        {isExpanded && !isGuest && (
          <div
            style={{
              marginTop: "var(--orbit-space-lg)",
              paddingTop: "var(--orbit-space-lg)",
              borderTop: "1px solid #e5e0d8",
            }}
          >
            {/* Что это значит для тебя */}
            <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
              <h4
                className="orbit-body-sm"
                style={{
                  fontWeight: 600,
                  marginBottom: "var(--orbit-space-sm)",
                  color: "#0f172a",
                }}
              >
                Что это значит для тебя
              </h4>
              <p
                className="orbit-body-sm"
                style={{
                  color: "#334155",
                  lineHeight: 1.6,
                }}
              >
                {axis.value > 0.5
                  ? `Ты определяешь себя через взаимодействие с миром и обратную связь от других. Это даёт тебе гибкость и адаптивность, но может создавать зависимость от внешних оценок.`
                  : axis.value < -0.5
                  ? `Ты опираешься на внутренние ориентиры и собственные ценности. Это даёт тебе стабильность и независимость, но может создавать сложности в адаптации к изменениям.`
                  : `Ты балансируешь между внутренними и внешними ориентирами, что даёт тебе гибкость, но может создавать внутренние противоречия.`}
              </p>
            </div>

            {/* Как это проявляется в жизни */}
            <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
              <h4
                className="orbit-body-sm"
                style={{
                  fontWeight: 600,
                  marginBottom: "var(--orbit-space-sm)",
                  color: "#0f172a",
                }}
              >
                {t("personalityPatterns.howItManifests", "Как это проявляется в жизни")}
              </h4>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  margin: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: "var(--orbit-space-xs)",
                }}
              >
                <li
                  className="orbit-body-sm"
                  style={{
                    color: "#334155",
                    paddingLeft: "var(--orbit-space-md)",
                    position: "relative",
                  }}
                >
                  <span
                    style={{
                      position: "absolute",
                      left: 0,
                      top: "0.5em",
                      width: "4px",
                      height: "4px",
                      borderRadius: "50%",
                      background: "#b87333",
                    }}
                  />
                  {t("personalityPatterns.inReactions", "В реакциях:")} {axis.value > 0 ? t("personalityPatterns.quicklyAdapt", "быстро адаптируешься к внешним сигналам") : t("personalityPatterns.relyOnInternal", "опираешься на внутренние ощущения")}
                </li>
                <li
                  className="orbit-body-sm"
                  style={{
                    color: "#334155",
                    paddingLeft: "var(--orbit-space-md)",
                    position: "relative",
                  }}
                >
                  <span
                    style={{
                      position: "absolute",
                      left: 0,
                      top: "0.5em",
                      width: "4px",
                      height: "4px",
                      borderRadius: "50%",
                      background: "#b87333",
                    }}
                  />
                  {t("personalityPatterns.inRelationships", "В отношениях:")} {axis.value > 0 ? t("personalityPatterns.valueFeedback", "ценишь обратную связь и взаимодействие") : t("personalityPatterns.needAutonomy", "нужна автономия и пространство")}
                </li>
                <li
                  className="orbit-body-sm"
                  style={{
                    color: "#334155",
                    paddingLeft: "var(--orbit-space-md)",
                    position: "relative",
                  }}
                >
                  <span
                    style={{
                      position: "absolute",
                      left: 0,
                      top: "0.5em",
                      width: "4px",
                      height: "4px",
                      borderRadius: "50%",
                      background: "#b87333",
                    }}
                  />
                  {t("personalityPatterns.inDecisions", "В решениях:")} {axis.value > 0 ? t("personalityPatterns.considerExternal", "учитываешь внешние факторы") : t("personalityPatterns.relyOnInternalCriteria", "опираешься на внутренние критерии")}
                </li>
              </ul>
            </div>

            {/* Где это проявляется сильнее */}
            <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
              <h4
                className="orbit-body-sm"
                style={{
                  fontWeight: 600,
                  marginBottom: "var(--orbit-space-sm)",
                  color: "#0f172a",
                }}
              >
                Где это проявляется сильнее
              </h4>
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "var(--orbit-space-sm)",
                }}
              >
                {["Любовь", "Карьера", "Деньги", "Семья", "Жизненные темы"].map((domain) => (
                  <a
                    key={domain}
                    href={`#domains`}
                    className="orbit-body-xs"
                    style={{
                      padding: "var(--orbit-space-xs) var(--orbit-space-sm)",
                      background: "#f5f5f0",
                      borderRadius: "var(--orbit-radius-sm)",
                      color: "#334155",
                      textDecoration: "none",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "#fefcf9";
                      e.currentTarget.style.border = "1px solid #b87333";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "#f5f5f0";
                      e.currentTarget.style.border = "none";
                    }}
                  >
                    {domain}
                  </a>
                ))}
              </div>
            </div>

            {/* Что с этим делать */}
            <div>
              <h4
                className="orbit-body-sm"
                style={{
                  fontWeight: 600,
                  marginBottom: "var(--orbit-space-sm)",
                  color: "#0f172a",
                }}
              >
                {t("personalityPatterns.whatToDo", "Что с этим делать")}
              </h4>
              <Link
                href={`/practices?axis=${axis.axis_id}`}
                className="orbit-button orbit-button-primary orbit-button-sm"
                style={{
                  textDecoration: "none",
                  display: "inline-block",
                }}
              >
                {t("personalityPatterns.practicesForPattern", "Практики под этот паттерн →")}
              </Link>
            </div>

            {/* МОНЕТИЗАЦИЯ: Апселл Full Report после раскрытия паттерна */}
            {isExpanded && !isGuest && (
              <FullReportUpsell
                context="pattern"
                patternName={axisNames[axis.axis_id]}
                hasFullReport={hasFullReport}
              />
            )}
          </div>
        )}

        {/* CTA для guest */}
        {isGuest && (
          <div style={{ marginTop: "var(--orbit-space-md)" }}>
            <Link
              href={PROFILE_CHART_DEEP_PATH}
              className="orbit-button orbit-button-secondary orbit-button-sm"
              style={{
                textDecoration: "none",
                display: "inline-block",
              }}
            >
              {t("personalityPatterns.calculateMyChart", "Рассчитать мою карту →")}
            </Link>
          </div>
        )}
      </div>
    );
  };

  return (
    <section
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
          {t("personalityPatterns.title", "How You Are Structured")}
        </h2>
        <p
          className="orbit-body"
          style={{
            color: "#334155",
            lineHeight: 1.6,
          }}
        >
          {t("personalityPatterns.description", "These patterns determine your reactions, decisions, and lifestyle.")}
        </p>
      </div>

      {/* Доминирующие оси */}
      {dominantAxes.length > 0 && (
        <div style={{ marginBottom: "var(--orbit-space-2xl)" }}>
          {dominantAxes.map((axis) => renderAxisCard(axis, true))}
        </div>
      )}

      {/* Вторичные оси */}
      {secondaryAxes.length > 0 && (
        <details
          style={{
            cursor: "pointer",
          }}
        >
          <summary
            className="orbit-body-sm"
            style={{
              color: "#334155",
              fontWeight: 500,
              marginBottom: "var(--orbit-space-md)",
              cursor: "pointer",
              listStyle: "none",
            }}
          >
            {t("personalityPatterns.otherPatterns", "Остальные паттерны")} ({secondaryAxes.length})
          </summary>
          <div>
            {secondaryAxes.map((axis) => renderAxisCard(axis, false))}
          </div>
        </details>
      )}
    </section>
  );
}
