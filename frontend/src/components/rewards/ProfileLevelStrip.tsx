"use client";

import Link from "next/link";
import { getHighestEarnedRingTier, getTierProgressVisual, REWARD_RINGS_COPY } from "@/lib/rewardRings";

type Props = {
  evolutionIndex: number;
  rewardRingsEarned?: string[] | null;
};

export function ProfileLevelStrip({ evolutionIndex, rewardRingsEarned }: Props) {
  const pct = Math.max(0, Math.min(100, Math.round(evolutionIndex)));
  const tier = getHighestEarnedRingTier(evolutionIndex, rewardRingsEarned);
  const vis = getTierProgressVisual(tier.order);
  const c = REWARD_RINGS_COPY;
  const aria = c.levelStripAria.replace("{rank}", tier.titleRu).replace("{index}", String(pct));

  return (
    <Link
      href="/profile?section=accuracy"
      className="tf-global-level-strip"
      aria-label={aria}
      prefetch={false}
      style={{ textDecoration: "none", display: "block", width: "100%", flexShrink: 0 }}
    >
      <div
        className="tf-global-level-strip__track"
        style={{
          height: "4px",
          width: "100%",
          background: "rgba(15, 23, 42, 0.07)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          className="tf-global-level-strip__fill"
          style={{
            height: "100%",
            width: `${pct}%`,
            minWidth: pct > 0 ? "3px" : 0,
            background: vis.stripGradient,
            boxShadow: "0 0 18px rgba(55, 40, 26, 0.22), inset 0 1px 0 rgba(255,255,255,0.4)",
            transition: "width 0.5s cubic-bezier(0.22, 1, 0.36, 1)",
          }}
        />
      </div>
    </Link>
  );
}
