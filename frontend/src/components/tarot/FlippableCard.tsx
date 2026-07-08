"use client";

import { useState } from "react";
import Image from "next/image";
import { CardVisual } from "./CardVisual";
import { LoadingSpinner } from "@/components/orbit";
import type { TarotCard } from "@/lib/types";
import { tarotCardBackSrc, tarotCardDisplayHeightPx, TAROT_CARD_PIXEL_WIDTH } from "@/lib/tarotCardAssets";

interface FlippableCardProps {
  card: TarotCard | null;
  orientation: "upright" | "reversed";
  loading?: boolean;
  onFlip?: () => void;
}

export function FlippableCard({ card, orientation, loading = false, onFlip }: FlippableCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleFlip = () => {
    if (isFlipped || loading || !card || isAnimating) return;
    setIsAnimating(true);
    setIsFlipped(true);
    setTimeout(() => {
      setIsAnimating(false);
      onFlip?.();
    }, 600); // Половина времени анимации
  };

  const flipW = TAROT_CARD_PIXEL_WIDTH;
  const flipH = tarotCardDisplayHeightPx(flipW);

  return (
    <div
      style={{
        perspective: "1000px",
        width: `${flipW}px`,
        height: `${flipH}px`,
        margin: "0 auto",
        cursor: card && !isFlipped ? "pointer" : "default",
      }}
      onClick={handleFlip}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          transformStyle: "preserve-3d",
          transition: "transform 0.6s ease",
          transform: isFlipped ? "rotateY(180deg)" : "rotateY(0deg)",
        }}
      >
        {/* Рубашка карты (обратная сторона) */}
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            backfaceVisibility: "hidden",
            WebkitBackfaceVisibility: "hidden",
            transform: "rotateY(0deg)",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              border: "1px solid rgba(214, 142, 122, 0.4)",
              borderRadius: "16px",
              boxShadow: "0 8px 22px rgba(90, 52, 44, 0.12)",
              position: "relative",
              overflow: "hidden",
              background: "#faf6f2",
            }}
          >
            <Image
              src={tarotCardBackSrc()}
              alt="Рубашка карты"
              fill
              sizes={`${flipW}px`}
              style={{ objectFit: "contain" }}
              priority={false}
            />
            {!loading && (
              <div
                style={{
                  position: "absolute",
                  bottom: "12px",
                  left: 8,
                  right: 8,
                  fontSize: "0.7rem",
                  color: "rgba(255, 250, 255, 0.92)",
                  fontWeight: 600,
                  textAlign: "center",
                  zIndex: 1,
                  textShadow: "0 1px 3px rgba(0,0,0,0.55)",
                }}
              >
                Нажми, чтобы открыть
              </div>
            )}
          </div>
        </div>

        {/* Лицевая сторона карты */}
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            backfaceVisibility: "hidden",
            WebkitBackfaceVisibility: "hidden",
            transform: "rotateY(180deg)",
          }}
        >
          {loading ? (
            <div
              style={{
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: "#faf6f2",
                borderRadius: "16px",
              }}
            >
              <LoadingSpinner size="md" />
            </div>
          ) : card ? (
            <CardVisual card={card} orientation={orientation} size="lg" showName={false} />
          ) : (
            <div
              style={{
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: "var(--orbit-color-mist)",
                borderRadius: "var(--orbit-radius-md)",
                padding: "var(--orbit-space-md)",
              }}
            >
              <p className="orbit-body-sm orbit-text-muted" style={{ textAlign: "center" }}>
                Не удалось загрузить карту
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

