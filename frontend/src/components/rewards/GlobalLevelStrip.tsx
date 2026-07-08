"use client";

import { usePathname } from "next/navigation";
import { SkeletonLoader } from "@/components/orbit/SkeletonLoader";
import { ProfileLevelStrip } from "@/components/rewards/ProfileLevelStrip";
import { useTodayCycle } from "@/components/providers/TodayCycleProvider";
import { isProductWebFullPageRoute } from "@/lib/productWebShell";

export function GlobalLevelStrip() {
  const pathname = usePathname();
  const hideProductWebShell = isProductWebFullPageRoute(pathname);
  const { cycle, todayHeavyLayersPending } = useTodayCycle();
  const rewards = cycle?.rewards;

  if (hideProductWebShell) return null;

  if (!rewards) {
    if (!todayHeavyLayersPending) return null;
    return (
      <div className="tf-global-level-strip tf-global-level-strip--pending" aria-busy="true" style={{ width: "100%", flexShrink: 0 }}>
        <SkeletonLoader height="4px" width="100%" />
      </div>
    );
  }

  return (
    <ProfileLevelStrip evolutionIndex={rewards.evolution_index} rewardRingsEarned={rewards.reward_rings_earned} />
  );
}
