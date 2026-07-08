"use client";

import Link from "next/link";
import {
  getHighestEarnedRingTier,
  getProgressToNextRing,
  getRewardRingStates,
  REWARD_RING_TIERS,
  REWARD_RINGS_COPY,
} from "@/lib/rewardRings";

export type GrowthMeterScores = {
  discipline: number;
  reflection: number;
  energy: number;
  mind: number;
};

type Props = {
  evolutionIndex: number;
  rewardRingsEarned?: string[] | null;
  /** Титул архетипа из /today (англ. имя) — рядом с рангом по кольцу */
  archetypeLevel?: string | null;
  /** Четыре опоры индекса с `/today` — только в полной шапке профиля */
  scores?: GrowthMeterScores | null;
  /** Пик индекса с бэкенда — если выше текущего, показываем пояснение про кольца */
  indexPeak?: number | null;
  variant?: "full" | "compact";
  /** В компактном виде: полоска Today — ссылка на формулу; профиль — одна ссылка на хаб справки */
  compactContext?: "todayStrip" | "profile";
};

function clampScore100(n: number): number {
  const x = Number.isFinite(n) ? n : 0;
  return Math.max(0, Math.min(100, Math.round(x)));
}

export function ProfileGrowthMeter({
  evolutionIndex,
  rewardRingsEarned,
  archetypeLevel,
  scores,
  indexPeak,
  variant = "full",
  compactContext = "todayStrip",
}: Props) {
  const c = REWARD_RINGS_COPY;
  const profileCompact = variant === "compact" && compactContext === "profile";
  const rankTier = getHighestEarnedRingTier(evolutionIndex, rewardRingsEarned);
  const seg = getProgressToNextRing(evolutionIndex, rewardRingsEarned);
  const safe = seg.safeIndex;
  const ticks = [...REWARD_RING_TIERS].sort((a, b) => a.minEvolutionIndex - b.minEvolutionIndex);
  const states = getRewardRingStates(evolutionIndex, rewardRingsEarned);
  const earnPills = [
    c.earnChannelToday,
    c.earnChannelTrackers,
    c.earnChannelGoals,
    c.earnChannelHabits,
    c.earnChannelAscetics,
    c.earnChannelPractices,
    c.earnChannelJournal,
  ];

  return (
    <div style={{ display: "grid", gap: variant === "compact" ? "0.5rem" : "0.75rem" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", justifyContent: "space-between", gap: "0.5rem 1rem" }}>
        <div style={{ minWidth: 0 }}>
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
            {c.rankLabel}
          </p>
          <p className="orbit-heading-3" style={{ margin: "0.2rem 0 0", color: "#37281a" }}>
            {rankTier.titleRu}
          </p>
          {archetypeLevel ? (
            <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#78716c" }}>
              {c.archetypeInSystemLabel}: {archetypeLevel}
            </p>
          ) : null}
        </div>
        <div style={{ textAlign: variant === "compact" ? "left" : "right" }}>
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
            {c.growthIndexLabel}
          </p>
          <p className="orbit-heading-3" style={{ margin: "0.2rem 0 0", color: "#5c4426" }}>
            {safe}
            <span className="orbit-body-sm" style={{ color: "#a8a29e", fontWeight: 600 }}>
              {" "}
              / 100
            </span>
          </p>
        </div>
      </div>

      {(variant === "full" || profileCompact) && indexPeak != null && indexPeak > safe ? (
        <p className="orbit-body-xs" style={{ margin: 0, color: "#78716c", lineHeight: 1.55 }}>
          {c.indexPeakExplainer.replace("{current}", String(safe)).replace("{peak}", String(indexPeak))}
        </p>
      ) : null}

      <div
        role="img"
        aria-label={`${c.growthIndexLabel} ${safe} из ста, отметки колец на шкале`}
        style={{ position: "relative", paddingTop: "0.35rem", paddingBottom: variant === "compact" ? "0.55rem" : "2.1rem" }}
      >
        <div
          style={{
            height: "12px",
            borderRadius: "999px",
            background: "rgba(148, 163, 184, 0.22)",
            overflow: "hidden",
            border: "1px solid rgba(201, 168, 115, 0.2)",
          }}
        >
          <div
            style={{
              width: `${safe}%`,
              height: "100%",
              borderRadius: "999px",
              background: "linear-gradient(100deg, #e8d4b0, #c9a66b 45%, #a67c3a)",
              transition: "width 0.35s ease-out",
            }}
          />
        </div>
        {ticks.map((tier) => {
          const state = states.find((s) => s.tier.id === tier.id);
          const earned = state?.earned ?? false;
          const leftPct = tier.minEvolutionIndex;
          return (
            <div
              key={tier.id}
              title={`${tier.titleRu} · порог ${tier.minEvolutionIndex}`}
              style={{
                position: "absolute",
                left: `calc(${leftPct}% - 5px)`,
                top: "26px",
                width: "10px",
                height: "10px",
                borderRadius: "50%",
                boxSizing: "border-box",
                background: earned ? "linear-gradient(145deg, #fef3c7, #d4a574)" : "rgba(255,255,255,0.85)",
                border: earned ? "2px solid rgba(168, 120, 48, 0.85)" : "2px solid rgba(148, 163, 184, 0.55)",
                boxShadow: earned ? "0 1px 4px rgba(90, 60, 30, 0.25)" : "none",
              }}
            />
          );
        })}
        {variant === "full" ? (
          <div
            style={{
              position: "absolute",
              top: "42px",
              left: 0,
              right: 0,
              display: "flex",
              justifyContent: "space-between",
              pointerEvents: "none",
            }}
          >
            {ticks.map((tier) => (
              <span
                key={`lbl-${tier.id}`}
                className="orbit-body-xs"
                style={{
                  position: "absolute",
                  left: `calc(${tier.minEvolutionIndex}% - 10px)`,
                  width: "20px",
                  textAlign: "center",
                  fontSize: "0.62rem",
                  color: "#a8a29e",
                  fontWeight: 700,
                }}
              >
                {tier.minEvolutionIndex}
              </span>
            ))}
          </div>
        ) : null}
      </div>

      {seg.isMax ? (
        <p className="orbit-body-xs" style={{ margin: 0, color: "#57534e", lineHeight: 1.6 }}>
          {c.progressMaxedShort}
        </p>
      ) : seg.nextTier ? (
        <p className="orbit-body-xs" style={{ margin: 0, color: "#44403c", lineHeight: 1.65 }}>
          <span style={{ fontWeight: 700 }}>{c.progressToNextRing}</span>: «{seg.nextTier.titleRu}» — {seg.pctInSegment}% {c.segmentPartLabel}{" "}
          <span style={{ color: "#78716c" }}>
            ({c.growthIndexLabel.toLowerCase()} {safe}, пороги {seg.prevThreshold}→{seg.nextThreshold})
          </span>
        </p>
      ) : null}

      {variant === "full" ? (
        <p className="orbit-body-xs" style={{ margin: 0, color: "#78716c", lineHeight: 1.6 }}>
          {c.growthScaleHint}
        </p>
      ) : null}

      {variant === "full" || !profileCompact ? (
        <p className="orbit-body-xs" style={{ margin: variant === "full" ? "0.35rem 0 0" : 0, lineHeight: 1.6 }}>
          <Link
            href="/help/progress"
            className="orbit-body-xs"
            style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "underline", textUnderlineOffset: "2px" }}
          >
            {c.howIndexWorksLink}
          </Link>
        </p>
      ) : null}

      {variant === "full" ? (
        <>
          <div>
            <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#7c6242" }}>
              {c.earnChannelsTitle}
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
              {earnPills.map((label) => (
                <span
                  key={label}
                  className="orbit-body-xs"
                  style={{
                    padding: "0.22rem 0.5rem",
                    borderRadius: "999px",
                    background: "rgba(255,255,255,0.7)",
                    border: "1px solid rgba(201, 168, 115, 0.28)",
                    color: "#57534e",
                    fontWeight: 600,
                  }}
                >
                  {label}
                </span>
              ))}
            </div>
          </div>

          {scores ? (
            <div
              role="region"
              aria-label={c.scoresBreakdownTitle}
              style={{
                marginTop: "0.15rem",
                paddingTop: "0.65rem",
                borderTop: "1px solid rgba(201, 168, 115, 0.22)",
                display: "grid",
                gap: "0.5rem",
              }}
            >
              <p className="orbit-body-xs" style={{ margin: 0, fontWeight: 700, color: "#7c6242" }}>
                {c.scoresBreakdownTitle}
              </p>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#78716c", lineHeight: 1.55 }}>
                {c.scoresBreakdownHint}
              </p>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(148px, 1fr))",
                  gap: "0.55rem 0.75rem",
                }}
              >
                {(
                  [
                    ["discipline", c.scoreDisciplineLabel, scores.discipline],
                    ["reflection", c.scoreReflectionLabel, scores.reflection],
                    ["energy", c.scoreEnergyLabel, scores.energy],
                    ["mind", c.scoreMindLabel, scores.mind],
                  ] as const
                ).map(([key, label, raw]) => {
                  const v = clampScore100(raw);
                  return (
                    <div key={key} style={{ minWidth: 0 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: "0.35rem" }}>
                        <span className="orbit-body-xs" style={{ color: "#57534e", fontWeight: 700 }}>
                          {label}
                        </span>
                        <span className="orbit-body-xs" style={{ color: "#a67c3a", fontWeight: 700 }}>
                          {v}
                        </span>
                      </div>
                      <div
                        role="progressbar"
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-valuenow={v}
                        aria-label={`${label}: ${v} из 100`}
                        style={{
                          marginTop: "0.28rem",
                          height: "6px",
                          borderRadius: "999px",
                          background: "rgba(148, 163, 184, 0.2)",
                          overflow: "hidden",
                          border: "1px solid rgba(201, 168, 115, 0.15)",
                        }}
                      >
                        <div
                          style={{
                            width: `${v}%`,
                            height: "100%",
                            borderRadius: "999px",
                            background: "linear-gradient(95deg, #e8d4b0, #c9a66b 55%, #9d7439)",
                            transition: "width 0.35s ease-out",
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
