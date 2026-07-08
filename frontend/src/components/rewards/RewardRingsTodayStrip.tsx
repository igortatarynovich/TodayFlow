"use client";

import Link from "next/link";
import { getRewardRingStates, REWARD_RINGS_COPY } from "@/lib/rewardRings";

type Props = {
  evolutionIndex: number;
  rewardRingsEarned?: string[] | null;
  archetypeLevel?: string | null;
  indexPeak?: number | null;
};

/**
 * Раньше использовалась на «Сегодня». Сейчас там свой UI; в профиле — отдельный блок
 * `ProfileAchievementsSection` (тексты `achievementsHint*`). Компонент оставлен на случай
 * повторного подключения или A/B.
 */
export function RewardRingsTodayStrip({ evolutionIndex, rewardRingsEarned }: Props) {
  const states = getRewardRingStates(evolutionIndex, rewardRingsEarned);
  const earnedCount = states.filter((s) => s.earned).length;
  const c = REWARD_RINGS_COPY;

  return (
    <section
      className="orbit-card todayflow-panel"
      style={{
        marginBottom: "0.85rem",
        padding: "0.65rem 0.85rem",
        borderRadius: "18px",
        background: "linear-gradient(135deg, rgba(255,253,249,0.96) 0%, rgba(252,246,236,0.9) 100%)",
        border: "1px solid rgba(201, 168, 115, 0.26)",
        boxShadow: "0 10px 24px -18px rgba(55, 40, 26, 0.32)",
      }}
    >
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "0.5rem 0.75rem" }}>
        <p className="orbit-body-xs" style={{ margin: 0, color: "#5b4630", lineHeight: 1.55, maxWidth: "min(100%, 36rem)" }}>
          <span style={{ color: "#a67c3a", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em" }}>{c.todayStripTitle}</span>
          {" — "}
          {c.todayStripSubtitle}{" "}
          <span style={{ color: "#78716c", fontWeight: 600 }}>
            ({c.todayStripProgressWord}: {earnedCount}/{states.length})
          </span>{" "}
          <Link href="/help/progress" style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "underline", textUnderlineOffset: "2px" }}>
            {c.howIndexWorksLink}
          </Link>
        </p>
        <Link
          href="/profile?section=accuracy"
          className="orbit-button orbit-button-secondary orbit-button-sm"
          style={{ textDecoration: "none", flexShrink: 0 }}
        >
          {c.todayStripCta}
        </Link>
      </div>
    </section>
  );
}
