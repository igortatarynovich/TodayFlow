"use client";

import { CardVisual } from "./CardVisual";
import type { TarotDailyDraw } from "@/lib/types";

interface TarotFavoritesProps {
  history: TarotDailyDraw[];
  favorites: number[];
}

export function TarotFavorites({ history, favorites }: TarotFavoritesProps) {
  const favoriteCards = history
    .filter((draw): draw is TarotDailyDraw & { card: NonNullable<TarotDailyDraw["card"]> } =>
      Boolean(draw.card && favorites.includes(draw.card.id)),
    )
    .reduce((acc, draw) => {
      if (!acc.find((c) => c.card.id === draw.card.id)) {
        acc.push(draw);
      }
      return acc;
    }, [] as Array<TarotDailyDraw & { card: NonNullable<TarotDailyDraw["card"]> }>);

  if (favoriteCards.length === 0) return null;

  return (
    <section className="orbit-hero-content-block">
      <div className="orbit-hero-content-container">
        <div className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)" }}>
          <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
            Избранные карты
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))", gap: "var(--orbit-space-md)" }}>
            {favoriteCards.map((draw, idx) => (
              <div key={idx} style={{ textAlign: "center" }}>
                <CardVisual 
                  card={draw.card} 
                  orientation={draw.orientation as "upright" | "reversed"} 
                  size="md"
                  showName={true}
                />
                <p className="orbit-body-xs" style={{ marginTop: "var(--orbit-space-xs)" }}>
                  {draw.card.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

