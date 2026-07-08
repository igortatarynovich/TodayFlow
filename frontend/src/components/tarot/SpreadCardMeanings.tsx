"use client";

import Link from "next/link";
import type { TarotSpreadResult, LiteReport } from "@/lib/types";
import type { Practice } from "@/lib/dashboardTypes";

interface SpreadCardMeaningsProps {
  spread: TarotSpreadResult;
  isAuthenticated: boolean;
  liteReport: LiteReport | null;
  dailyPractice: Practice | null;
}

export function SpreadCardMeanings({ spread, isAuthenticated, liteReport, dailyPractice }: SpreadCardMeaningsProps) {
  if (!spread.cards || spread.cards.length === 0) return null;

  return (
    <div style={{ marginTop: "var(--orbit-space-xl)", paddingTop: "var(--orbit-space-xl)", borderTop: "1px solid var(--orbit-color-border)" }}>
      <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-lg)" }}>
        По картам
      </h3>
      {spread.cards.map((cardResult, idx) => (
        <div key={idx} style={{ marginBottom: "var(--orbit-space-xl)" }}>
          <h4 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
            {cardResult.card.name}
            {cardResult.orientation === "reversed" ? " · перевёрнута" : ""}
          </h4>
          {isAuthenticated && liteReport?.internal_model ? (
            <div style={{ 
              padding: "var(--orbit-space-lg)",
              background: "var(--orbit-color-mist)",
              borderRadius: "var(--orbit-radius-md)"
            }}>
              <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
                <strong>Суть.</strong> {cardResult.orientation === "upright" ? cardResult.card.upright : cardResult.card.reversed}
              </p>
              <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)", filter: "none" }}>
                <strong>Сегодня.</strong> Совпадает с активным паттерном — смотри реакции и темп, без форса.
              </p>
              <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-md)" }}>
                Слой по карте личности.{" "}
                <Link href="/discover" className="orbit-link">Узнать себя →</Link>
              </p>
            </div>
          ) : (
            <div style={{ 
              padding: "var(--orbit-space-lg)",
              background: "var(--orbit-color-mist)",
              borderRadius: "var(--orbit-radius-md)",
              position: "relative",
              overflow: "hidden"
            }}>
              <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>
                <strong>Суть.</strong> {cardResult.orientation === "upright" ? cardResult.card.upright : cardResult.card.reversed}
              </p>
              <div style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: "rgba(255,255,255,0.8)",
                backdropFilter: "blur(4px)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 10,
                textAlign: "center",
                padding: "var(--orbit-space-xl)",
              }}>
                <div>
                  <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)" }}>
                    С датой рождения — точнее.
                  </p>
                  <Link href="/onboarding/core" className="orbit-button orbit-button-primary">
                    Персонализировать →
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
