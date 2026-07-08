"use client";

import type { CSSProperties } from "react";

type Props = {
  title?: string;
  subtitle?: string;
  symbol?: string;
  compact?: boolean;
};

export function TarotCover({ title = "Tarot", subtitle, symbol = "✶", compact = false }: Props) {
  return (
    <div
      style={{
        borderRadius: compact ? "12px" : "16px",
        border: "1px solid rgba(200,169,90,0.45)",
        background: "linear-gradient(180deg, #1e1b3a 0%, #111827 100%)",
        color: "#f8f5ee",
        padding: compact ? "0.7rem" : "1rem",
        boxShadow: "0 8px 20px rgba(15, 23, 42, 0.22)",
      }}
    >
      <div style={{ textAlign: "center" }}>
        <div style={symbolStyle}>{symbol}</div>
        <p className="orbit-body-sm" style={{ margin: "0.2rem 0 0", color: "#f8f5ee", fontWeight: 700 }}>
          {title}
        </p>
        {subtitle && (
          <p className="orbit-body-xs" style={{ margin: "0.15rem 0 0", color: "rgba(248,245,238,0.8)" }}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}

const symbolStyle: CSSProperties = {
  fontSize: "2rem",
  lineHeight: 1,
  color: "#c8a95a",
  textShadow: "0 0 16px rgba(200,169,90,0.28)",
};
