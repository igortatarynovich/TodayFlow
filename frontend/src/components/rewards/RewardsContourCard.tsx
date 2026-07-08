"use client";

import type { CSSProperties } from "react";
import type { RewardMilestone, RewardsSnapshot } from "@/lib/rewards";
import { getEvolutionProgress, getStreakProgress } from "@/lib/rewardsProgress";

type Props = {
  rewards: RewardsSnapshot;
  milestones?: RewardMilestone[];
  compact?: boolean;
};

export function RewardsContourCard({ rewards, milestones = [], compact = false }: Props) {
  const evolution = getEvolutionProgress(rewards.evolution_index);
  const streak = getStreakProgress(rewards.streaks.daily_current);
  const currentArchetype = rewards.archetype_progress?.current || evolution.currentTier.title;
  const nextArchetype = rewards.archetype_progress?.next || evolution.nextTier?.title || null;
  const archetypeProgressPct = rewards.archetype_progress?.progress_pct ?? evolution.progressPct;

  return (
    <div
      style={{
        background: "var(--orbit-reward-bg)",
        border: "1px solid var(--orbit-reward-border)",
        borderRadius: "14px",
        padding: compact ? "0.75rem" : "var(--orbit-space-lg)",
        boxShadow: "var(--orbit-reward-shadow)",
      }}
    >
      <p className="orbit-body" style={{ margin: 0, color: "#334155", lineHeight: 1.6 }}>
        {rewards.message}
      </p>

      <div style={{ marginTop: "0.55rem", display: "grid", gap: "0.45rem", gridTemplateColumns: "repeat(2, minmax(0, 1fr))" }}>
        <span className="orbit-body-xs" style={chipStyle}>Архетип: {currentArchetype}</span>
        <span className="orbit-body-xs" style={chipStyle}>Стрик: {streak.currentTier.title}</span>
        <span className="orbit-body-xs" style={chipStyle}>Daily: {rewards.streaks.daily_current}</span>
        <span className="orbit-body-xs" style={chipStyle}>Weekly: {rewards.streaks.weekly_current}</span>
      </div>

      <div style={{ marginTop: "0.5rem", display: "grid", gap: "0.4rem" }}>
        <div style={{ height: "6px", borderRadius: "999px", background: "rgba(148,163,184,0.22)", overflow: "hidden" }}>
          <div style={{ width: `${archetypeProgressPct}%`, height: "100%", background: "linear-gradient(120deg,#d3b178,#bf975f)" }} />
        </div>
        <p className="orbit-body-xs" style={{ margin: 0, color: "#475569" }}>
          {nextArchetype
            ? `До ${nextArchetype}: ${Math.max(0, evolution.nextXp - evolution.totalXp)} XP`
            : "Максимальный архетипический уровень"}
        </p>
      </div>

      {rewards.seals.length > 0 && (
        <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
          {rewards.seals.map((seal) => (
            <span key={seal.code} className="orbit-body-xs" style={{ ...chipStyle, background: "#fffaf0" }}>
              {seal.title} · {seal.strength}%
            </span>
          ))}
        </div>
      )}

      {milestones.length > 0 && (
        <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
          {milestones.slice(0, compact ? 2 : 3).map((m) => (
            <span key={m.name} className="orbit-body-xs" style={{ ...chipStyle, background: m.status === "done" ? "var(--orbit-reward-done)" : "var(--orbit-reward-next)" }}>
              {m.name}: {m.status === "done" ? "готово" : `${m.days_left} дн.`}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

const chipStyle: CSSProperties = {
  borderRadius: "999px",
  border: "1px solid rgba(148,163,184,0.45)",
  padding: "0.1rem 0.55rem",
  background: "rgba(248,250,252,0.92)",
  color: "#1f2937",
  fontWeight: 700,
};
