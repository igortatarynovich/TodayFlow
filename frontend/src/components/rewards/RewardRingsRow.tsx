"use client";

import { getRewardRingStates } from "@/lib/rewardRings";

type Props = {
  evolutionIndex: number;
  rewardRingsEarned?: string[] | null;
};

/** Только визуальный ряд из семи колец — для шапки «Главное» на Today без текстов про достижения. */
export function RewardRingsRow({ evolutionIndex, rewardRingsEarned }: Props) {
  const states = getRewardRingStates(evolutionIndex, rewardRingsEarned);

  return (
    <div
      role="list"
      aria-label="Семь колец прогресса"
      style={{
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "flex-end",
        gap: "0.2rem",
        overflowX: "auto",
        paddingBottom: "0.1rem",
        maxWidth: "min(100%, 380px)",
        WebkitOverflowScrolling: "touch",
      }}
    >
      {states.map((state) => (
        <div
          key={state.tier.id}
          role="listitem"
          style={{
            flex: "0 0 auto",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "46px",
          }}
        >
          <div
            title={`${state.tier.titleRu}. ${state.tier.collectViaRu}`}
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              boxSizing: "border-box",
              ...(state.earned
                ? {
                    background: "radial-gradient(circle at 35% 30%, #fff9ed 0%, #e8c896 42%, #b8894a 88%)",
                    boxShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 0 3px rgba(201, 166, 107, 0.75), 0 4px 10px -3px rgba(90, 60, 30, 0.3)",
                  }
                : {
                    background: "rgba(255,255,255,0.45)",
                    border: state.isNext ? "2px solid rgba(184, 134, 11, 0.7)" : "2px dashed rgba(148, 163, 184, 0.6)",
                    boxShadow: state.isNext ? "0 0 0 1px rgba(255,255,255,0.8)" : "none",
                  }),
            }}
          />
        </div>
      ))}
    </div>
  );
}
