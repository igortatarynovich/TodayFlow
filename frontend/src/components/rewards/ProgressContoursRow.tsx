"use client";

import { getRewardRingStates } from "@/lib/rewardRings";

type Props = {
  evolutionIndex: number;
  rewardRingsEarned?: string[] | null;
};

/** Семь вех на шкале — в виде мягких «контуров», а не залитых колец (концепт TodayFlow). */
export function ProgressContoursRow({ evolutionIndex, rewardRingsEarned }: Props) {
  const states = getRewardRingStates(evolutionIndex, rewardRingsEarned);

  return (
    <div
      role="list"
      aria-label="Семь контуров прогресса по индексу роста"
      style={{
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "flex-end",
        gap: "0.28rem",
        overflowX: "auto",
        paddingBottom: "0.15rem",
        maxWidth: "min(100%, 400px)",
        WebkitOverflowScrolling: "touch",
      }}
    >
      {states.map((state, i) => {
        const earned = state.earned;
        const next = state.isNext;
        const warm = i <= 2;
        const borderEarned = warm ? "2px solid rgba(176, 125, 48, 0.92)" : "2px solid rgba(100, 116, 139, 0.82)";
        const fillEarned = warm
          ? "linear-gradient(165deg, rgba(255, 252, 245, 0.95) 0%, rgba(252, 236, 210, 0.45) 100%)"
          : "linear-gradient(165deg, rgba(248, 250, 252, 0.98) 0%, rgba(226, 232, 240, 0.4) 100%)";
        return (
          <div
            key={state.tier.id}
            role="listitem"
            title={`${state.tier.titleRu}. ${state.tier.collectViaRu}`}
            style={{
              flex: "0 0 auto",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "44px",
            }}
          >
            <div
              style={{
                width: "34px",
                height: "40px",
                borderRadius: "11px",
                boxSizing: "border-box",
                position: "relative",
                background: earned ? fillEarned : "rgba(255,255,255,0.2)",
                border: earned ? borderEarned : next ? "2px solid rgba(184, 134, 11, 0.78)" : "2px dashed rgba(148, 163, 184, 0.55)",
                boxShadow: earned
                  ? `${warm ? "inset 0 1px 0 rgba(255,255,255,0.75), " : "inset 0 1px 0 rgba(255,255,255,0.6), "}0 2px 10px -4px rgba(90, 60, 30, 0.22)`
                  : next
                    ? "0 0 0 1px rgba(255, 250, 240, 0.95), 0 2px 8px -2px rgba(139, 90, 43, 0.2)"
                    : "none",
              }}
            >
              {earned ? (
                <span
                  aria-hidden
                  style={{
                    position: "absolute",
                    inset: "5px",
                    borderRadius: "7px",
                    border: `1px solid ${warm ? "rgba(120, 80, 40, 0.32)" : "rgba(71, 85, 105, 0.3)"}`,
                    pointerEvents: "none",
                  }}
                />
              ) : null}
            </div>
          </div>
        );
      })}
    </div>
  );
}
