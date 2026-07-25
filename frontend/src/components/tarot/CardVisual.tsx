"use client";

import type { CSSProperties, MouseEvent } from "react";
import { TarotCard } from "@/lib/types";
import {
  tarotCardBackPicture,
  tarotCardDisplayHeightPx,
  tarotCardFacePicture,
} from "@/lib/tarotCardAssets";
import { TarotPicture } from "@/components/tarot/TarotPicture";

interface CardVisualProps {
  card: TarotCard;
  orientation: "upright" | "reversed";
  size?: "xs" | "sm" | "md" | "lg" | "hero";
  showName?: boolean;
  className?: string;
  interactive?: boolean;
  onClick?: () => void;
  /** `bare` = art only (no UI border/cream plate). */
  chrome?: "frame" | "bare";
  /** Override pixel width when size token is not enough. */
  widthPx?: number;
}

/** Widths by size; height from 3:5 aspect. */
const sizeClasses = {
  sm: { widthPx: 88, fontSize: "0.75rem", sizesAttr: "88px" },
  xs: { widthPx: 72, fontSize: "0.68rem", sizesAttr: "72px" },
  md: { widthPx: 168, fontSize: "0.875rem", sizesAttr: "168px" },
  lg: { widthPx: 280, fontSize: "1rem", sizesAttr: "(max-width: 40rem) 62vw, 280px" },
  hero: { widthPx: 320, fontSize: "1.05rem", sizesAttr: "(max-width: 40rem) 70vw, 320px" },
};

export function CardVisual({
  card,
  orientation,
  size = "md",
  showName = true,
  className = "",
  interactive = false,
  onClick,
  chrome = "frame",
  widthPx,
}: CardVisualProps) {
  const dimensions = sizeClasses[size];
  const cardWidthPx = widthPx ?? dimensions.widthPx;
  const cardHeightPx = tarotCardDisplayHeightPx(cardWidthPx);
  const isReversed = orientation === "reversed";
  const face = tarotCardFacePicture(card.id);
  const sources = face ?? tarotCardBackPicture();
  const usingBackFallback = !face;
  const bare = chrome === "bare";

  const outerBase: CSSProperties = bare
    ? {
        width: `${cardWidthPx}px`,
        height: `${cardHeightPx}px`,
        maxWidth: "100%",
        borderRadius: "10px",
        position: "relative",
        transform: isReversed ? "rotate(180deg)" : "none",
        transition: "transform 0.3s ease, box-shadow 0.3s ease",
        boxShadow: "0 18px 40px rgba(0, 0, 0, 0.35)",
        cursor: interactive ? "pointer" : "default",
        overflow: "hidden",
        border: "none",
        background: "transparent",
      }
    : {
        width: `${cardWidthPx}px`,
        height: `${cardHeightPx}px`,
        borderRadius: "16px",
        position: "relative",
        transform: isReversed ? "rotate(180deg)" : "none",
        transition: "transform 0.3s ease, box-shadow 0.3s ease",
        boxShadow: interactive ? "0 6px 16px rgba(90, 52, 44, 0.12)" : "0 4px 12px rgba(90, 52, 44, 0.08)",
        cursor: interactive ? "pointer" : "default",
        overflow: "hidden",
        border: "1px solid rgba(214, 142, 122, 0.38)",
        background: "#faf6f2",
      };

  const hoverEnter = (e: MouseEvent<HTMLDivElement>) => {
    if (!interactive) return;
    const el = e.currentTarget.querySelector(".tarot-card-visual__frame") as HTMLElement | null;
    if (!el) return;
    el.style.transform = isReversed ? "rotate(180deg) translateY(-4px)" : "translateY(-4px)";
    el.style.boxShadow = bare ? "0 22px 48px rgba(0, 0, 0, 0.42)" : "0 8px 18px rgba(90, 52, 44, 0.14)";
  };
  const hoverLeave = (e: MouseEvent<HTMLDivElement>) => {
    if (!interactive) return;
    const el = e.currentTarget.querySelector(".tarot-card-visual__frame") as HTMLElement | null;
    if (!el) return;
    el.style.transform = isReversed ? "rotate(180deg)" : "none";
    el.style.boxShadow = bare
      ? "0 18px 40px rgba(0, 0, 0, 0.35)"
      : interactive
        ? "0 6px 16px rgba(90, 52, 44, 0.12)"
        : "0 4px 12px rgba(90, 52, 44, 0.08)";
  };

  const sizesAttr = widthPx ? `${widthPx}px` : dimensions.sizesAttr;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "0.4rem",
        cursor: interactive ? "pointer" : "default",
      }}
      onMouseEnter={hoverEnter}
      onMouseLeave={hoverLeave}
      onClick={interactive && onClick ? onClick : undefined}
    >
      <div className={`tarot-card-visual__frame tarot-card-visual ${className}`} style={outerBase}>
        <TarotPicture
          sources={sources}
          alt={usingBackFallback ? "" : card.name}
          sizes={sizesAttr}
        />
      </div>
      {showName ? (
        <div style={{ textAlign: "center", maxWidth: `${cardWidthPx}px` }}>
          <div
            style={{
              fontSize: dimensions.fontSize,
              fontWeight: 600,
              color: "#2d241c",
              lineHeight: 1.3,
            }}
          >
            {card.name}
          </div>
          <div
            style={{
              marginTop: "0.15rem",
              fontSize: "0.68rem",
              fontWeight: 600,
              letterSpacing: "0.04em",
              textTransform: "uppercase",
              color: "#8a7355",
            }}
          >
            {isReversed ? "Перевёрнутое положение" : "Прямое положение"}
          </div>
        </div>
      ) : null}
    </div>
  );
}
