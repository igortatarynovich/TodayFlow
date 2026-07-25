"use client";

import { useState } from "react";
import {
  TAROT_CARD_ASPECT_RATIO,
  tarotCardBackPicture,
  tarotCardFacePicture,
} from "@/lib/tarotCardAssets";
import { TarotPicture } from "@/components/tarot/TarotPicture";
import s from "@/components/product-ui/productWebScreens.module.css";

export type TarotCardImageProps = {
  cardId: number;
  cardName: string;
  width?: number;
  className?: string;
  reversed?: boolean;
};

/** Tarot face with deck back fallback — never emoji. */
export function TarotCardImage({
  cardId,
  cardName,
  width = 220,
  className,
  reversed = false,
}: TarotCardImageProps) {
  const [failed, setFailed] = useState(false);
  const face = tarotCardFacePicture(cardId);
  const sources = failed || !face ? tarotCardBackPicture() : face;

  return (
    <div
      className={`${s.tarotWebCardImageWrap} ${className ?? ""}`.trim()}
      style={{
        width: `${width}px`,
        maxWidth: "100%",
        aspectRatio: String(TAROT_CARD_ASPECT_RATIO),
        transform: reversed ? "rotate(180deg)" : undefined,
      }}
      onErrorCapture={() => setFailed(true)}
    >
      <TarotPicture sources={sources} alt={cardName} sizes={`${width}px`} />
    </div>
  );
}
