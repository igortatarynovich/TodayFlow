"use client";

import type { CSSProperties, MouseEvent } from "react";
import Image from "next/image";
import { TarotCard } from "@/lib/types";
import { tarotCardDisplayHeightPx, tarotCardFaceSrc } from "@/lib/tarotCardAssets";

interface CardVisualProps {
  card: TarotCard;
  orientation: "upright" | "reversed";
  size?: "xs" | "sm" | "md" | "lg";
  showName?: boolean;
  className?: string;
  interactive?: boolean;
  onClick?: () => void;
}

// Символы для карт без файла ассета (запасной UI)
const cardSymbols: Record<number, string> = {
  0: "🌱",
  1: "✨",
  2: "🌙",
  3: "🌺",
  4: "👑",
  5: "📜",
  6: "💑",
  7: "🏛️",
  8: "🦁",
  9: "🕯️",
  10: "🎡",
  11: "⚖️",
  12: "🔄",
  13: "🦋",
  14: "⚗️",
  15: "🔗",
  16: "⚡",
  17: "⭐",
  18: "🌊",
  19: "☀️",
  20: "📯",
  21: "🌍",
};

/** Ширины по размеру; высота из пропорций PNG колоды 192×320. */
const sizeClasses = {
  sm: {
    widthPx: 88,
    fontSize: "0.75rem",
    symbolSize: "24px",
    sizesAttr: "88px",
  },
  xs: {
    widthPx: 68,
    fontSize: "0.68rem",
    symbolSize: "18px",
    sizesAttr: "68px",
  },
  md: {
    widthPx: 168,
    fontSize: "0.875rem",
    symbolSize: "52px",
    sizesAttr: "168px",
  },
  lg: {
    widthPx: 192,
    fontSize: "1rem",
    symbolSize: "62px",
    sizesAttr: "192px",
  },
};

export function CardVisual({
  card,
  orientation,
  size = "md",
  showName = true,
  className = "",
  interactive = false,
  onClick,
}: CardVisualProps) {
  const dimensions = sizeClasses[size];
  const cardWidthPx = dimensions.widthPx;
  const cardHeightPx = tarotCardDisplayHeightPx(cardWidthPx);
  const isReversed = orientation === "reversed";
  const symbol = cardSymbols[card.id] || "🃏";
  const faceSrc = tarotCardFaceSrc(card.id);

  const elementColors: Record<string, { bg: string; border: string; text: string; accent: string }> = {
    fire: {
      bg: "rgba(255, 200, 150, 0.2)",
      border: "rgba(255, 150, 100, 0.4)",
      text: "rgba(200, 80, 50, 0.9)",
      accent: "rgba(255, 150, 100, 0.6)",
    },
    water: {
      bg: "rgba(150, 200, 255, 0.2)",
      border: "rgba(100, 150, 255, 0.4)",
      text: "rgba(50, 100, 200, 0.9)",
      accent: "rgba(100, 150, 255, 0.6)",
    },
    earth: {
      bg: "rgba(200, 220, 180, 0.2)",
      border: "rgba(150, 180, 120, 0.4)",
      text: "rgba(100, 130, 80, 0.9)",
      accent: "rgba(150, 180, 120, 0.6)",
    },
    air: {
      bg: "rgba(220, 220, 240, 0.2)",
      border: "rgba(180, 180, 220, 0.4)",
      text: "rgba(120, 120, 180, 0.9)",
      accent: "rgba(180, 180, 220, 0.6)",
    },
  };

  const element = (card.correspondences as { element?: string })?.element || "air";
  const colors = elementColors[element] || elementColors.air;

  const outerBase: CSSProperties = {
    width: `${cardWidthPx}px`,
    height: `${cardHeightPx}px`,
    borderRadius: "16px",
    position: "relative",
    transform: isReversed ? "rotate(180deg)" : "none",
    transition: "transform 0.3s ease, box-shadow 0.3s ease",
    boxShadow: interactive ? "0 6px 16px rgba(90, 52, 44, 0.12)" : "0 4px 12px rgba(90, 52, 44, 0.08)",
    cursor: interactive ? "pointer" : "default",
    overflow: "hidden",
    border: faceSrc ? "1px solid rgba(214, 142, 122, 0.38)" : `2px solid ${colors.border}`,
    background: faceSrc ? "#faf6f2" : `linear-gradient(135deg, ${colors.bg}, rgba(255, 255, 255, 0.1))`,
    ...(faceSrc
      ? {}
      : {
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "var(--orbit-space-sm)",
        }),
  };

  const hoverEnter = (e: MouseEvent<HTMLDivElement>) => {
    if (!interactive) return;
    const el = e.currentTarget.querySelector(".tarot-card-visual__frame") as HTMLElement | null;
    if (!el) return;
    el.style.transform = isReversed ? "rotate(180deg) translateY(-4px)" : "translateY(-4px)";
    el.style.boxShadow = "0 8px 18px rgba(90, 52, 44, 0.14)";
  };
  const hoverLeave = (e: MouseEvent<HTMLDivElement>) => {
    if (!interactive) return;
    const el = e.currentTarget.querySelector(".tarot-card-visual__frame") as HTMLElement | null;
    if (!el) return;
    el.style.transform = isReversed ? "rotate(180deg)" : "none";
    el.style.boxShadow = interactive ? "0 6px 16px rgba(90, 52, 44, 0.12)" : "0 4px 12px rgba(90, 52, 44, 0.08)";
  };

  const cardFrame = (
    <div
      className={`tarot-card-visual__frame tarot-card-visual ${className}`}
      onClick={interactive && onClick ? onClick : undefined}
      style={outerBase}
    >
      {faceSrc ? (
        <>
          <Image
            src={faceSrc}
            alt={card.name}
            fill
            sizes={dimensions.sizesAttr}
            style={{ objectFit: "contain" }}
            priority={false}
          />
          <div
            style={{
              position: "absolute",
              bottom: "8px",
              right: "8px",
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: isReversed ? "rgba(255, 160, 120, 0.95)" : "rgba(80, 200, 120, 0.9)",
              border: "1px solid rgba(255,255,255,0.5)",
              zIndex: 3,
              pointerEvents: "none",
            }}
          />
        </>
      ) : (
        <>
          <div
            className="card-number"
            style={{
              position: "absolute",
              top: "8px",
              left: "8px",
              fontSize: `calc(${dimensions.fontSize} * 0.8)`,
              fontWeight: 600,
              color: colors.text,
              opacity: 0.7,
              zIndex: 2,
            }}
          >
            {card.id}
          </div>

          <div
            className="card-symbol"
            style={{
              fontSize: dimensions.symbolSize,
              marginBottom: showName ? "var(--orbit-space-xs)" : 0,
              filter: isReversed ? "hue-rotate(180deg)" : "none",
              transition: "filter 0.3s ease",
            }}
          >
            {symbol}
          </div>

          {showName && (
            <div
              className="card-name"
              style={{
                fontSize: dimensions.fontSize,
                fontWeight: 600,
                color: colors.text,
                textAlign: "center",
                lineHeight: 1.2,
                marginTop: "auto",
                marginBottom: "auto",
                padding: "0 var(--orbit-space-sm)",
              }}
            >
              {card.name}
            </div>
          )}

          <div
            style={{
              position: "absolute",
              bottom: "8px",
              right: "8px",
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: isReversed ? colors.accent : "rgba(50, 200, 50, 0.6)",
              border: `1px solid ${colors.border}`,
              zIndex: 2,
            }}
          />

          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              width: "60%",
              height: "2px",
              background: `linear-gradient(90deg, transparent, ${colors.accent}, transparent)`,
              opacity: 0.3,
            }}
          />
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%) rotate(90deg)",
              width: "60%",
              height: "2px",
              background: `linear-gradient(90deg, transparent, ${colors.accent}, transparent)`,
              opacity: 0.3,
            }}
          />

          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background:
                "url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48ZmlsdGVyIGlkPSJncmFpbiI+PGZlVHVyYnVsZW5jZSB0eXBlPSJmcmFjdGFsTm9pc2UiIGJhc2VGcmVxdWVuY3k9IjAuOSIgbnVtT2N0YXZlcz0iNCIvPjwvZmlsdGVyPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsdGVyPSJ1cmwoI2dyYWluKSIgb3BhY2l0eT0iMC4wMyIvPjwvc3ZnPg==')",
              opacity: 0.3,
              pointerEvents: "none",
              borderRadius: "var(--orbit-radius-md)",
            }}
          />
        </>
      )}
    </div>
  );

  if (faceSrc) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "0.45rem",
          cursor: interactive ? "pointer" : "default",
        }}
        onMouseEnter={hoverEnter}
        onMouseLeave={hoverLeave}
      >
        {cardFrame}
        {showName ? (
          <div
            style={{
              fontSize: dimensions.fontSize,
              fontWeight: 600,
              color: "#2d241c",
              textAlign: "center",
              lineHeight: 1.3,
              maxWidth: `${cardWidthPx}px`,
            }}
          >
            {card.name}
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div onMouseEnter={hoverEnter} onMouseLeave={hoverLeave} style={{ display: "inline-block" }}>
      {cardFrame}
    </div>
  );
}
