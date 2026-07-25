"use client";

import {
  tarotCardBackPicture,
  TAROT_CARD_ASPECT_RATIO,
  tarotCardDisplayHeightPx,
} from "@/lib/tarotCardAssets";
import { TarotPicture } from "@/components/tarot/TarotPicture";

type TarotCardBackProps = {
  /** CSS width; height from 3:5 aspect. */
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
  const sources = tarotCardBackPicture();
  const frameStyle = {
    display: "block" as const,
    width: `${widthPx}px`,
    maxWidth: "100%",
    height: `${heightPx}px`,
    margin: "0 auto",
    padding: 0,
    border: selected
      ? "2px solid rgba(210, 180, 120, 0.65)"
      : "1px solid rgba(214, 142, 122, 0.38)",
    borderRadius: "14px",
    overflow: "hidden" as const,
    position: "relative" as const,
    background: "#faf6f2",
    boxShadow: selected
      ? "0 10px 22px rgba(90, 52, 44, 0.18)"
      : "0 6px 16px rgba(90, 52, 44, 0.1)",
    opacity: dimmed ? 0.42 : 1,
  };

  if (!interactive) {
    return (
      <div className={className} style={frameStyle}>
        <TarotPicture sources={sources} sizes={`${widthPx}px`} />
      </div>
    );
  }

  return (
    <button
      type="button"
      className={className}
      onClick={onClick}
      aria-hidden={false}
      style={{
        ...frameStyle,
        cursor: "pointer",
        transition: "transform 180ms ease, box-shadow 180ms ease, opacity 180ms ease",
        transform: selected ? "translateY(-2px) scale(1.03)" : "none",
      }}
    >
      <TarotPicture sources={sources} sizes={`${widthPx}px`} />
    </button>
  );
}

export { TAROT_CARD_ASPECT_RATIO };
