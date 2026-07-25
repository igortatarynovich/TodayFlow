"use client";

import { useState } from "react";
import { CardVisual } from "./CardVisual";
import { LoadingSpinner } from "@/components/orbit";
import { MotionFlip, usePrefersReducedMotion } from "@/design-system/motion";
import type { TarotCard } from "@/lib/types";
import {
  tarotCardBackPicture,
  tarotCardDisplayHeightPx,
  TAROT_RITUAL_REVEAL_MAX_WIDTH_PX,
} from "@/lib/tarotCardAssets";
import { TarotPicture } from "@/components/tarot/TarotPicture";

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

  const flipW = TAROT_RITUAL_REVEAL_MAX_WIDTH_PX;
  const flipH = tarotCardDisplayHeightPx(flipW);
  const canFlip = Boolean(card && !isFlipped && !loading);
  const backSources = tarotCardBackPicture();

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
      <TarotPicture sources={backSources} alt="Рубашка карты" sizes={`${flipW}px`} />
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
        reducedMotion={reduceMotion}
        back={back}
        front={front}
        onAnimationComplete={() => {
          if (isFlipped && !reduceMotion) onFlip?.();
        }}
      />
    </div>
  );
}
