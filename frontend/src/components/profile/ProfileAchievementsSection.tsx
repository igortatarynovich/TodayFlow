"use client";

import type { CSSProperties } from "react";
import Link from "next/link";
import type { RewardMilestone, RewardsSnapshot } from "@/lib/rewards";
import type { ProfileAccuracySummary } from "@/lib/computeProfileAccuracy";
import { ProfileGrowthMeter } from "@/components/rewards/ProfileGrowthMeter";
import { RewardRingsLadder } from "@/components/rewards/RewardRingsLadder";
import { RewardsContourCard } from "@/components/rewards/RewardsContourCard";
import { getRewardRingStates, REWARD_RINGS_COPY } from "@/lib/rewardRings";
import { SurfaceInsight } from "@/components/foundation/SurfaceInsight";

type Props = {
  rewards: RewardsSnapshot;
  milestones: RewardMilestone[];
  accuracySummary?: ProfileAccuracySummary | null;
};

const chip: CSSProperties = {
  borderRadius: "999px",
  border: "1px solid rgba(148,163,184,0.45)",
  padding: "0.25rem 0.65rem",
  background: "rgba(248,250,252,0.92)",
  color: "#1f2937",
  fontWeight: 700,
  fontSize: "0.78rem",
};

export function ProfileAchievementsSection({ rewards, milestones, accuracySummary }: Props) {
  const c = REWARD_RINGS_COPY;
  const ringStates = getRewardRingStates(rewards.evolution_index, rewards.reward_rings_earned);
  const ringsEarned = ringStates.filter((s) => s.earned).length;
  const ringsTotal = ringStates.length;
  const streaks = [
    [c.streakDailyLabel, rewards.streaks.daily_current] as const,
    [c.streakWeeklyLabel, rewards.streaks.weekly_current] as const,
    [c.streakHabitLabel, rewards.streaks.habit_best] as const,
    [c.streakAsceticLabel, rewards.streaks.ascetic_best] as const,
    [c.streakTarotLabel, rewards.streaks.tarot_current] as const,
  ];

  return (
    <div style={{ display: "grid", gap: "1.35rem" }}>
      <p className="orbit-body" style={{ margin: 0, color: "#44403c", lineHeight: 1.7 }}>
        {c.achievementsPageIntro}
      </p>

      {accuracySummary ? (
        <SurfaceInsight variant="warm" eyebrow="Точность профиля">
          <p className="orbit-display-sm" style={{ margin: "0.15rem 0 0", color: "#37281a" }}>
            {accuracySummary.percent}%
          </p>
          <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#57534e", lineHeight: 1.65 }}>
            Это не «ранг ради ранга», а насколько полно система может опираться на твои данные рождения и живые сигналы.
          </p>
          {accuracySummary.hints.length ? (
            <ul className="orbit-body-sm" style={{ margin: "0.65rem 0 0", paddingLeft: "1.1rem", color: "#44403c", lineHeight: 1.65 }}>
              {accuracySummary.hints.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>
          ) : (
            <p className="orbit-body-sm" style={{ margin: "0.65rem 0 0", color: "#57534e" }}>
              Продолжай в том же духе: профиль уже достаточно плотный для уверенных подсказок.
            </p>
          )}
        </SurfaceInsight>
      ) : null}

      <SurfaceInsight variant="warm" eyebrow={c.achievementsHintTitle}>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#44403c", lineHeight: 1.65 }}>
          {c.achievementsHintP1}
        </p>
        <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "#5b4630", lineHeight: 1.6 }}>
          <span style={{ fontWeight: 700 }}>{c.achievementsHintRingsProgress}</span>{" "}
          <span style={{ color: "#57534e" }}>
            {ringsEarned}/{ringsTotal} ({c.todayStripProgressWord})
          </span>
          .{" "}
          <Link href="/help/progress" style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "underline", textUnderlineOffset: "2px" }}>
            {c.howIndexWorksLink}
          </Link>
        </p>
      </SurfaceInsight>

      <SurfaceInsight eyebrow={c.achievementsSectionContour}>
        <RewardsContourCard rewards={rewards} milestones={milestones} />
      </SurfaceInsight>

      <SurfaceInsight eyebrow={c.achievementsSectionIndex}>
        <ProfileGrowthMeter
          evolutionIndex={rewards.evolution_index}
          rewardRingsEarned={rewards.reward_rings_earned}
          archetypeLevel={rewards.archetype_level}
          scores={rewards.scores}
          indexPeak={rewards.reward_evolution_index_peak}
          variant="full"
        />
        <div style={{ marginTop: "1rem", height: "1px", background: "linear-gradient(90deg, transparent, rgba(201, 168, 115, 0.28), transparent)" }} />
        <div style={{ marginTop: "1rem" }}>
          <RewardRingsLadder evolutionIndex={rewards.evolution_index} rewardRingsEarned={rewards.reward_rings_earned} />
        </div>
      </SurfaceInsight>

      <SurfaceInsight eyebrow={c.achievementsSectionStreaks}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
          {streaks.map(([label, value]) => (
            <span key={label} className="orbit-body-xs" style={chip}>
              {label}: {value}
            </span>
          ))}
        </div>
      </SurfaceInsight>

      {rewards.seals.length > 0 ? (
        <SurfaceInsight eyebrow={c.achievementsSectionSeals}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
            {rewards.seals.map((seal) => (
              <span key={seal.code} className="orbit-body-xs" style={{ ...chip, background: "#fffaf0" }}>
                {seal.title} · {seal.strength}%
              </span>
            ))}
          </div>
        </SurfaceInsight>
      ) : null}

      <p className="orbit-body-xs" style={{ margin: 0, color: "#64748b" }}>
        <Link href="/help/rings" style={{ color: "#a67c3a", fontWeight: 700 }}>
          {c.achievementsFooterRingsLink}
        </Link>
        {" · "}
        <Link href="/help/progress" style={{ color: "#a67c3a", fontWeight: 700 }}>
          {c.howIndexWorksLink}
        </Link>
      </p>
    </div>
  );
}
