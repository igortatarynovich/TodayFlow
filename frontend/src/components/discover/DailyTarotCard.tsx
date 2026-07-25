"use client";

import type { TarotDailyDraw } from "@/lib/types";
import { TarotPicture } from "@/components/tarot/TarotPicture";
import { tarotCardFacePicture, tarotCardBackPicture } from "@/lib/tarotCardAssets";

interface DailyTarotCardProps {
  tarotCard: TarotDailyDraw | null;
}

export function DailyTarotCard({ tarotCard }: DailyTarotCardProps) {
  if (!tarotCard?.card) return null;
  const id = typeof tarotCard.card.id === "number" ? tarotCard.card.id : Number(tarotCard.card.id);
  const face = Number.isFinite(id) ? tarotCardFacePicture(id) : null;
  const sources = face ?? tarotCardBackPicture();

  return (
    <div
      className="orbit-card"
      style={{
        padding: "var(--orbit-space-lg)",
        background: "#ffffff",
        border: "1px solid #e5e0d8",
      }}
    >
      <div
        style={{
          width: 72,
          aspectRatio: "3 / 5",
          marginBottom: "var(--orbit-space-sm)",
          borderRadius: 10,
          overflow: "hidden",
          border: "1px solid rgba(154, 132, 104, 0.35)",
          background: "#f4ebe0",
        }}
      >
        <TarotPicture sources={sources} alt={tarotCard.card.name} sizes="72px" />
      </div>
      <h3
        className="orbit-body"
        style={{
          fontWeight: 600,
          marginBottom: "var(--orbit-space-xs)",
          color: "#0f172a",
        }}
      >
        Карта дня
      </h3>
      <p className="orbit-body-sm" style={{ color: "#334155", marginBottom: "var(--orbit-space-xs)" }}>
        {tarotCard.card.name}
      </p>
      {tarotCard.card.keywords && tarotCard.card.keywords.length > 0 && (
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "var(--orbit-space-xs)",
            marginTop: "var(--orbit-space-sm)",
          }}
        >
          {tarotCard.card.keywords.slice(0, 3).map((keyword, i) => (
            <span
              key={i}
              className="orbit-body-xs"
              style={{
                padding: "0.15rem 0.45rem",
                borderRadius: 999,
                background: "rgba(247, 244, 238, 0.95)",
                color: "#5f4930",
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
