"use client";

import { useId } from "react";

type ContourLevel = "bronze" | "silver" | "gold";

const PALETTE: Record<ContourLevel, { a: string; b: string; glow: string }> = {
  bronze: { a: "#7c4a21", b: "#e8c18a", glow: "rgba(184, 120, 52, 0.42)" },
  silver: { a: "#4b5563", b: "#e5e7eb", glow: "rgba(148, 163, 184, 0.4)" },
  gold: { a: "#854d0e", b: "#fde68a", glow: "rgba(217, 119, 6, 0.38)" },
};

/** Двойной скруглённый контур для подписи «бронзовый / серебряный / золотой контур дня». */
export function RewardContourBadge({ level, className }: { level: ContourLevel; className?: string }) {
  const uid = useId().replace(/:/g, "");
  const p = PALETTE[level];
  const gid = `contour-grad-${level}-${uid}`;
  const fid = `contour-filt-${level}-${uid}`;

  return (
    <svg
      className={className}
      width="112"
      height="44"
      viewBox="0 0 112 44"
      aria-hidden
      style={{ flexShrink: 0 }}
    >
      <defs>
        <linearGradient id={gid} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={p.b} />
          <stop offset="55%" stopColor={p.a} />
          <stop offset="100%" stopColor={p.b} />
        </linearGradient>
        <filter id={fid} x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="1" stdDeviation="2" floodColor={p.glow} floodOpacity="0.9" />
        </filter>
      </defs>
      <rect
        x="2"
        y="2"
        width="108"
        height="40"
        rx="12"
        fill="rgba(255,252,247,0.35)"
        stroke={`url(#${gid})`}
        strokeWidth="2.25"
        filter={`url(#${fid})`}
      />
      <rect x="9" y="9" width="94" height="26" rx="8" fill="none" stroke={p.a} strokeWidth="1" opacity="0.45" />
    </svg>
  );
}
