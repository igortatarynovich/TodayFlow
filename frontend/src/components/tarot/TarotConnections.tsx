"use client";

import { t } from "@/lib/i18n";

import Link from "next/link";
import { computePersonalLens } from "@/lib/personal-lens";
import type { LiteReport } from "@/lib/types";
import type { Practice } from "@/lib/dashboardTypes";

interface TarotConnectionsProps {
  liteReport: LiteReport | null;
  dailyPractice: Practice | null;
}

export function TarotConnections({ liteReport, dailyPractice }: TarotConnectionsProps) {
  if (!liteReport?.internal_model) return null;

  const axes = liteReport.internal_model.axes;
  const activeAxis = axes && axes.length > 0 ? axes[0] : null;
  const axisNames: Record<string, string> = {
    "A1": t("patterns.axis.short.A1", "Идентичность"),
    "A2": t("patterns.axis.short.A2", "Эмоции"),
    "A3": t("patterns.axis.short.A3", "Решения"),
    "A4": t("patterns.axis.short.A4", "Стабильность"),
    "A5": t("patterns.axis.short.A5", "Контроль"),
    "A6": t("patterns.axis.short.A6", "Отношения"),
    "A7": t("patterns.axis.short.A7", "Энергия")
  };

  const sun = liteReport?.summary?.sun;
  const moon = liteReport?.summary?.moon;
  const rising = liteReport?.summary?.rising;
  const personalLens = liteReport?.internal_model ? computePersonalLens(liteReport.internal_model, sun, moon, rising) : null;
  const dominantDomain = personalLens?.dominant_domains?.[0];

  return (
    <div style={{ marginTop: "var(--orbit-space-xl)", paddingTop: "var(--orbit-space-xl)", borderTop: "1px solid var(--orbit-color-border)" }}>
      <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-lg)" }}>
        Связи и действие
      </h3>
      
      {/* A) Связь с паттерном */}
      {activeAxis && (
        <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
          <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>
            Эта карта усиливает паттерн: <strong>{axisNames[activeAxis.axis_id] || activeAxis.axis_id}</strong>
          </p>
          <Link href={`/discover/pattern/${activeAxis.axis_id}`} className="orbit-button orbit-button-secondary orbit-button-sm">
            Посмотреть в моей карте →
          </Link>
        </div>
      )}

      {/* B) Связь со сферой жизни */}
      {dominantDomain && (
        <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
          <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>
            Больше всего это затрагивает сферу: <strong>{dominantDomain}</strong>
          </p>
          <Link href={`/discover#${dominantDomain.toLowerCase().replace(/\s+/g, "-")}`} className="orbit-button orbit-button-secondary orbit-button-sm">
            Смотреть в Узнай себя →
          </Link>
        </div>
      )}

      {/* C) Одно действие */}
      {dailyPractice && (
        <div>
          <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>
            Сегодня полезно замедлиться перед принятием решений.
          </p>
          <Link href={`/practices/${dailyPractice.id}`} className="orbit-button orbit-button-primary orbit-button-sm">
            Открыть практику →
          </Link>
        </div>
      )}
    </div>
  );
}

