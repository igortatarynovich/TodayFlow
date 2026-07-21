"use client";

import Link from "next/link";

interface TarotFavoritesCardProps {
  count: number;
}

export function TarotFavoritesCard({ count }: TarotFavoritesCardProps) {
  if (count === 0) return null;

  const getCountText = (count: number) => {
    if (count === 1) return "карта";
    if (count < 5) return "карты";
    return "карт";
  };

  return (
    <div className="orbit-card" style={{
      padding: "var(--orbit-space-lg)",
      background: "#ffffff",
      border: "1px solid #e5e0d8"
    }}>
      <div style={{ fontSize: "2rem", marginBottom: "var(--orbit-space-sm)" }}>⭐</div>
      <h3 className="orbit-body" style={{
        fontWeight: 600,
        marginBottom: "var(--orbit-space-xs)",
        color: "#0f172a"
      }}>
        Избранные карты
      </h3>
      <p className="orbit-body-sm" style={{ color: "#334155", marginBottom: "var(--orbit-space-xs)", fontWeight: 500 }}>
        {count} {getCountText(count)}
      </p>
      <p className="orbit-body-xs orbit-text-muted" style={{ lineHeight: 1.5 }}>
        Карты, которые резонируют с тобой
      </p>
      <Link
        href="/tarot"
        className="orbit-button orbit-button-secondary orbit-button-xs"
        style={{
          display: "inline-block",
          marginTop: "var(--orbit-space-sm)",
          textDecoration: "none"
        }}
      >
        Смотреть все →
      </Link>
    </div>
  );
}

