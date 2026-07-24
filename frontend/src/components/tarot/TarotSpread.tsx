"use client";

import { useState, useEffect } from "react";
import { TarotSpreadResult, TarotSpreadCard } from "@/lib/types";
import { CardVisual } from "./CardVisual";
import { TarotCardBack } from "./TarotCardBack";
import { MotionFlip } from "@/design-system/motion";
import { MeaningCard } from "@/components/orbit";
import { tarotCardDisplayHeightPx } from "@/lib/tarotCardAssets";

interface TarotSpreadProps {
  spread: TarotSpreadResult;
  onClose?: () => void;
}

const SPREAD_CARD_WIDTH = 168;

export function TarotSpread({ spread, onClose }: TarotSpreadProps) {
  const [selectedCard, setSelectedCard] = useState<TarotSpreadCard | null>(null);
  const [revealedCards, setRevealedCards] = useState<number[]>([]);
  const cardHeight = tarotCardDisplayHeightPx(SPREAD_CARD_WIDTH);

  useEffect(() => {
    // Анимация раскрытия карт по очереди
    spread.cards.forEach((_, index) => {
      setTimeout(() => {
        setRevealedCards((prev) => {
          if (prev.includes(index)) return prev;
          return [...prev, index];
        });
      }, index * 200);
    });
  }, [spread.cards]);

  return (
    <div className="tarot-spread-container" style={{ padding: "var(--orbit-space-lg)" }}>
      <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
        <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-xs)" }}>
          {spread.title}
        </h2>
        {spread.description && (
          <p className="orbit-body-sm orbit-text-muted">{spread.description}</p>
        )}
      </div>

      {/* Расклад карт */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "var(--orbit-space-md)",
          justifyContent: "center",
          marginBottom: "var(--orbit-space-xl)",
          padding: "var(--orbit-space-lg)",
          background: "var(--orbit-color-mist)",
          borderRadius: "var(--orbit-radius-md)",
          minHeight: "300px",
        }}
      >
        {spread.cards.map((spreadCard, idx) => {
          const isRevealed = revealedCards.includes(idx);
          return (
            <div
              key={idx}
              onClick={() => isRevealed && setSelectedCard(spreadCard)}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "var(--orbit-space-xs)",
                cursor: isRevealed ? "pointer" : "default",
              }}
            >
              <div style={{ width: SPREAD_CARD_WIDTH, height: cardHeight }}>
                <MotionFlip
                  testId={`tarot-spread-motion-flip-${idx}`}
                  flipped={isRevealed}
                  back={<TarotCardBack widthPx={SPREAD_CARD_WIDTH} />}
                  front={
                    <CardVisual
                      card={spreadCard.card}
                      orientation={spreadCard.orientation as "upright" | "reversed"}
                      size="md"
                      showName={false}
                      interactive={isRevealed}
                      onClick={() => isRevealed && setSelectedCard(spreadCard)}
                    />
                  }
                />
              </div>
              <div style={{ textAlign: "center", maxWidth: "120px" }}>
                <p className="orbit-body-xs" style={{ fontWeight: 600, marginBottom: "2px" }}>
                  {spreadCard.position.title}
                </p>
                <p className="orbit-body-xs orbit-text-muted" style={{ fontSize: "0.7rem" }}>
                  {spreadCard.position.prompt}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Интерпретация выбранной карты */}
      {selectedCard && (
        <div style={{ marginTop: "var(--orbit-space-xl)" }}>
          <MeaningCard
            layer="observation"
            label={selectedCard.position.title}
            heading={selectedCard.card.name}
            body={
              <div>
                <p className="orbit-body" style={{ marginBottom: "var(--orbit-space-md)" }}>
                  {selectedCard.orientation === "upright"
                    ? selectedCard.card.upright
                    : selectedCard.card.reversed}
                </p>
                {selectedCard.meaning && (
                  <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-sm)" }}>
                    {selectedCard.meaning}
                  </p>
                )}
                {selectedCard.card.keywords && selectedCard.card.keywords.length > 0 && (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)" }}>
                    {selectedCard.card.keywords.map((keyword, idx) => (
                      <span key={idx} className="orbit-badge-xs">
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            }
          />
        </div>
      )}

      {/* Кнопка закрытия */}
      {onClose && (
        <div style={{ marginTop: "var(--orbit-space-lg)", textAlign: "center" }}>
          <button onClick={onClose} className="orbit-button orbit-button-secondary">
            Закрыть
          </button>
        </div>
      )}
    </div>
  );
}
