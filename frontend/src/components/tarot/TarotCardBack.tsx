"use client";

import type { CSSProperties } from "react";
import Image from "next/image";
import {
  tarotCardBackSrc,
  TAROT_CARD_ASPECT_RATIO,
  tarotCardDisplayHeightPx,
} from "@/lib/tarotCardAssets";

type TarotCardBackProps = {
  /** Ширина карты в px; высота из пропорций колоды 192×320. */
  widthPx?: number;
  className?: string;
  interactive?: boolean;
  onClick?: () => void;
  dimmed?: boolean;
  selected?: boolean;
};

export function TarotCardBack({
  widthPx = 88,
  className = "",
  interactive = false,
  onClick,
  dimmed = false,
  selected = false,
}: TarotCardBackProps) {
  const heightPx = tarotCardDisplayHeightPx(widthPx);

  if (!interactive) {
    return (
      <div
        className={className}
        style={{
          display: "block",
          width: `${widthPx}px`,
          maxWidth: "100%",
          height: `${heightPx}px`,
          margin: "0 auto",
          padding: 0,
          border: selected
            ? "2px solid rgba(210, 180, 120, 0.65)"
            : "1px solid rgba(214, 142, 122, 0.38)",
          borderRadius: "14px",
          overflow: "hidden",
          position: "relative",
          background: "#faf6f2",
          boxShadow: selected
            ? "0 10px 22px rgba(90, 52, 44, 0.18)"
            : "0 6px 16px rgba(90, 52, 44, 0.1)",
          opacity: dimmed ? 0.42 : 1,
        }}
      >
        <Image src={tarotCardBackSrc()} alt="" fill sizes={`${widthPx}px`} style={{ objectFit: "contain" }} />
      </div>
    );
  }

  return (
    <button
      type="button"
      className={className}
      onClick={interactive ? onClick : undefined}
      disabled={!interactive}
      aria-hidden={!interactive}
      style={{
        display: "block",
        width: `${widthPx}px`,
        maxWidth: "100%",
        height: `${heightPx}px`,
        margin: "0 auto",
        padding: 0,
        border: selected
          ? "2px solid rgba(210, 180, 120, 0.65)"
          : "1px solid rgba(214, 142, 122, 0.38)",
        borderRadius: "14px",
        overflow: "hidden",
        position: "relative",
        background: "#faf6f2",
        boxShadow: selected
          ? "0 10px 22px rgba(90, 52, 44, 0.18)"
          : "0 6px 16px rgba(90, 52, 44, 0.1)",
        cursor: interactive ? "pointer" : "default",
        opacity: dimmed ? 0.42 : 1,
        transition: "transform 180ms ease, box-shadow 180ms ease, opacity 180ms ease",
        transform: selected ? "translateY(-2px) scale(1.03)" : "none",
      }}
    >
      <Image
        src={tarotCardBackSrc()}
        alt=""
        fill
        sizes={`${widthPx}px`}
        style={{ objectFit: "contain" }}
        priority={false}
      />
    </button>
  );
}

/** Утилита для контейнеров с `width: 100%` и фиксированным aspect-ratio. */
export function tarotCardBackAspectStyle(): CSSProperties {
  return { aspectRatio: String(TAROT_CARD_ASPECT_RATIO), width: "100%" };
}
