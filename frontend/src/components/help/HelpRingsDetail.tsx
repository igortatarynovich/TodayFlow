"use client";

import Link from "next/link";
import { LoadingSpinner } from "@/components/orbit";
import { ProfileGrowthMeter } from "@/components/rewards/ProfileGrowthMeter";
import { RewardRingsLadder } from "@/components/rewards/RewardRingsLadder";
import { useTodayCycle } from "@/components/providers/TodayCycleProvider";
import type { RewardsSnapshot } from "@/lib/rewards";
import { REWARD_RING_TIERS, REWARD_RINGS_COPY } from "@/lib/rewardRings";
import { useAuth } from "@/lib/useAuth";
import helpHub from "@/data/helpHub.ru.json";

export function HelpRingsDetail() {
  const { isAuthenticated } = useAuth();
  const { cycle, loading: cycleLoading, error: cycleError, refetchToday } = useTodayCycle();
  const rewards: RewardsSnapshot | null = cycle?.rewards ?? null;

  if (isAuthenticated && cycleLoading && !rewards) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
        <LoadingSpinner />
      </div>
    );
  }

  if (isAuthenticated && cycleError && !rewards) {
    return (
      <div style={{ display: "grid", gap: "1rem", padding: "0.5rem 0" }}>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#57534e", lineHeight: 1.65 }}>
          Не удалось загрузить твой прогресс по контурам и индексу. Попробуй ещё раз.
        </p>
        <button
          type="button"
          className="orbit-button orbit-button-primary"
          style={{ justifySelf: "start" }}
          onClick={() => void refetchToday({ force: true })}
        >
          Повторить
        </button>
      </div>
    );
  }

  const c = REWARD_RINGS_COPY;

  if (isAuthenticated && rewards) {
    return (
      <div style={{ display: "grid", gap: "1.25rem" }}>
        <div
          className="todayflow-panel orbit-card"
          style={{
            padding: "1.05rem 1.15rem",
            borderRadius: "22px",
            border: "1px solid rgba(201, 168, 115, 0.28)",
            background: "linear-gradient(145deg, rgba(255, 253, 249, 0.97) 0%, rgba(252, 246, 236, 0.92) 100%)",
          }}
        >
          <ProfileGrowthMeter
            evolutionIndex={rewards.evolution_index}
            rewardRingsEarned={rewards.reward_rings_earned}
            archetypeLevel={rewards.archetype_level}
            scores={rewards.scores}
            indexPeak={rewards.reward_evolution_index_peak}
            variant="full"
          />
        </div>
        <RewardRingsLadder evolutionIndex={rewards.evolution_index} rewardRingsEarned={rewards.reward_rings_earned} />
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: "1rem" }}>
      <p className="orbit-body-sm" style={{ margin: 0, color: "#57534e", lineHeight: 1.65 }}>
        {helpHub.ringsAnonymousHint}
      </p>
      <div style={{ display: "grid", gap: "0.65rem" }}>
        {[...REWARD_RING_TIERS].sort((a, b) => a.order - b.order).map((tier) => (
          <div
            key={tier.id}
            className="orbit-card"
            style={{
              padding: "0.75rem 0.85rem",
              borderRadius: "14px",
              border: "1px solid rgba(226, 220, 208, 0.95)",
              background: "rgba(255,255,255,0.72)",
            }}
          >
            <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#5c4426" }}>
              {tier.order}. {tier.titleRu} · порог {tier.minEvolutionIndex}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#475569", lineHeight: 1.6 }}>
              {tier.collectViaRu}
            </p>
          </div>
        ))}
      </div>
      <p className="orbit-body-xs" style={{ margin: 0 }}>
        <Link href="/help/progress" style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "underline" }}>
          {c.howIndexWorksLink}
        </Link>
      </p>
    </div>
  );
}
