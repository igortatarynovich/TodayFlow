"use client";

import type { TarotDailyDraw } from "@/lib/types";

interface DailyTarotCardProps {
  tarotCard: TarotDailyDraw | null;
}

export function DailyTarotCard({ tarotCard }: DailyTarotCardProps) {
  if (!tarotCard?.card) return null;

  return (
    <div className="orbit-card" style={{
      padding: "var(--orbit-space-lg)",
      background: "#ffffff",
      border: "1px solid #e5e0d8"
    }}>
      <div style={{ fontSize: "2rem", marginBottom: "var(--orbit-space-sm)" }}>🃏</div>
      <h3 className="orbit-body" style={{
        fontWeight: 600,
        marginBottom: "var(--orbit-space-xs)",
        color: "#0f172a"
      }}>
        Карта дня
      </h3>
      <p className="orbit-body-sm" style={{ color: "#334155", marginBottom: "var(--orbit-space-xs)" }}>
        {tarotCard.card.name}
      </p>
      {tarotCard.card.keywords && tarotCard.card.keywords.length > 0 && (
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "var(--orbit-space-xs)",
          marginTop: "var(--orbit-space-sm)"
        }}>
          {tarotCard.card.keywords.slice(0, 3).map((keyword, i) => (
            <span
              key={i}
              className="orbit-body-xs"
              style={{
                padding: "4px 8px",
                background: "#f5f5f0",
                borderRadius: "var(--orbit-radius-sm)",
                color: "#334155"
              }}
            >
              {keyword}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

