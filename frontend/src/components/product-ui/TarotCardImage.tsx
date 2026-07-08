"use client";

import Image from "next/image";
import { useState } from "react";
import {
  TAROT_CARD_ASPECT_RATIO,
  tarotCardBackSrc,
  tarotCardFaceSrc,
} from "@/lib/tarotCardAssets";
import s from "@/components/product-ui/productWebScreens.module.css";

export type TarotCardImageProps = {
  cardId: number;
  cardName: string;
  width?: number;
  className?: string;
  reversed?: boolean;
};

/** Tarot face with graceful fallback when deck PNGs are missing from `public/`. */
export function TarotCardImage({
  cardId,
  cardName,
  width = 220,
  className,
  reversed = false,
}: TarotCardImageProps) {
  const [failed, setFailed] = useState(false);
  const src = tarotCardFaceSrc(cardId) ?? tarotCardBackSrc();

  if (failed) {
    return (
      <div
        className={`${s.tarotWebCardPlaceholder} ${className ?? ""}`.trim()}
        aria-label={cardName}
      >
        <span className={s.tarotWebCardPlaceholderName}>{cardName}</span>
      </div>
    );
  }

  return (
    <div
      className={`${s.tarotWebCardImageWrap} ${className ?? ""}`.trim()}
      style={{
        width: `${width}px`,
        maxWidth: "100%",
        aspectRatio: String(TAROT_CARD_ASPECT_RATIO),
        transform: reversed ? "rotate(180deg)" : undefined,
      }}
    >
      <Image
        src={src}
        alt={cardName}
        fill
        sizes={`${width}px`}
        onError={() => setFailed(true)}
        style={{ objectFit: "contain", borderRadius: "inherit" }}
      />
    </div>
  );
}
