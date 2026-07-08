"use client";

import type { CSSProperties } from "react";

type GlyphType = "morning" | "day" | "evening" | "tarot" | "numerology" | "lunar";

type Props = {
  type: GlyphType;
  size?: "sm" | "md" | "lg";
};

const glyphMap: Record<GlyphType, string> = {
  morning: "☉",
  day: "◐",
  evening: "☽",
  tarot: "✶",
  numerology: "9",
  lunar: "☾",
};

const sizeMap: Record<NonNullable<Props["size"]>, number> = {
  sm: 28,
  md: 40,
  lg: 52,
};

export function SectionGlyph({ type, size = "md" }: Props) {
  const px = sizeMap[size];
  return (
    <span
      aria-hidden="true"
      style={{
        width: `${px}px`,
        height: `${px}px`,
        borderRadius: "999px",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        border: "1px solid rgba(148,163,184,0.5)",
        color: "#0f172a",
        background: "linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)",
        fontSize: `${Math.round(px * 0.48)}px`,
        fontWeight: 600,
        lineHeight: 1,
      }}
    >
      {glyphMap[type]}
    </span>
  );
}

export const sectionGlyphMutedStyle: CSSProperties = {
  color: "#64748b",
  fontWeight: 600,
};
