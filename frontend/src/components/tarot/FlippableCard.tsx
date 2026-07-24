"use client";

import { useState } from "react";
import Image from "next/image";
import { CardVisual } from "./CardVisual";
import { LoadingSpinner } from "@/components/orbit";
import { MotionFlip, usePrefersReducedMotion } from "@/design-system/motion";
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
  const reduceMotion = usePrefersReducedMotion();

  const handleFlip = () => {
    if (isFlipped || loading || !card) return;
    setIsFlipped(true);
    if (reduceMotion) {
      onFlip?.();
    }
  };

  const flipW = TAROT_CARD_PIXEL_WIDTH;
  const flipH = tarotCardDisplayHeightPx(flipW);
  const canFlip = Boolean(card && !isFlipped && !loading);

  const back = (
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
      {!loading ? (
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
            textShadow: "0 1px 3px rgba(0, 0, 0, 0.55)",
          }}
        >
          Нажми, чтобы открыть
        </div>
      ) : null}
    </div>
  );

  const front = loading ? (
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
  );

  return (
    <div
      style={{
        width: `${flipW}px`,
        height: `${flipH}px`,
        margin: "0 auto",
        cursor: canFlip ? "pointer" : "default",
      }}
      onClick={handleFlip}
      role={canFlip ? "button" : undefined}
      tabIndex={canFlip ? 0 : undefined}
      onKeyDown={
        canFlip
          ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                handleFlip();
              }
            }
          : undefined
      }
      aria-label={canFlip ? "Открыть карту" : undefined}
    >
      <MotionFlip
        testId="tarot-flippable-motion-flip"
        flipped={isFlipped}
        back={back}
        front={front}
        onAnimationComplete={() => {
          if (isFlipped && !reduceMotion) onFlip?.();
        }}
      />
    </div>
  );
}
