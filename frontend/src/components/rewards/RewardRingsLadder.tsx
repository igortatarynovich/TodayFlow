"use client";

import Link from "next/link";
import { getNextRewardRing, getRewardRingStates, REWARD_RINGS_COPY } from "@/lib/rewardRings";

type Props = {
  evolutionIndex: number;
  rewardRingsEarned?: string[] | null;
};

export function RewardRingsLadder({ evolutionIndex, rewardRingsEarned }: Props) {
  const states = getRewardRingStates(evolutionIndex, rewardRingsEarned);
  const nextRing = getNextRewardRing(evolutionIndex, rewardRingsEarned);
  const earnedCount = states.filter((s) => s.earned).length;
  const c = REWARD_RINGS_COPY;

  return (
    <div style={{ display: "grid", gap: "0.75rem" }}>
      <p className="orbit-body-xs" style={{ margin: 0, color: "#6b5340", lineHeight: 1.55 }}>
        {c.ringsIntroShort}
      </p>
      <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", lineHeight: 1.55 }}>
        <Link
          href="/help/progress"
          style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "underline", textUnderlineOffset: "2px" }}
        >
          {c.howIndexWorksLink}
        </Link>
      </p>

      <div
        role="list"
        aria-label="Семь колец прогресса"
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: "0.25rem",
          overflowX: "auto",
          paddingBottom: "0.15rem",
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
              width: "52px",
            }}
          >
            <div
              title={`${state.tier.titleRu}. ${state.tier.collectViaRu}`}
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                boxSizing: "border-box",
                ...(state.earned
                  ? {
                      background: "radial-gradient(circle at 35% 30%, #fff9ed 0%, #e8c896 42%, #b8894a 88%)",
                      boxShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 0 4px rgba(201, 166, 107, 0.85), 0 6px 14px -4px rgba(90, 60, 30, 0.35)",
                    }
                  : {
                      background: "rgba(255,255,255,0.45)",
                      border: state.isNext ? "2px solid rgba(184, 134, 11, 0.75)" : "2px dashed rgba(148, 163, 184, 0.65)",
                      boxShadow: state.isNext ? "0 0 0 1px rgba(255,255,255,0.8)" : "none",
                    }),
              }}
            />
            <span
              className="orbit-body-xs"
              style={{
                marginTop: "0.35rem",
                textAlign: "center",
                color: state.earned ? "#5c4426" : "#64748b",
                fontWeight: state.earned ? 700 : 600,
                fontSize: "0.65rem",
                lineHeight: 1.25,
                maxWidth: "100%",
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
              }}
            >
              {state.tier.titleRu}
            </span>
          </div>
        ))}
      </div>

      <div
        className="orbit-card"
        style={{
          padding: "0.65rem 0.75rem",
          borderRadius: "14px",
          background: "rgba(255,255,255,0.72)",
          border: "1px solid rgba(201, 168, 115, 0.2)",
        }}
      >
        {nextRing ? (
          <>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700 }}>
              {c.nextSectionEyebrow}: {nextRing.titleRu}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#475569", lineHeight: 1.65 }}>
              {nextRing.collectViaRu}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#334155", fontWeight: 700 }}>
              {c.nextGrantsTitle}
            </p>
            <ul style={{ margin: "0.25rem 0 0", paddingLeft: "1.1rem", color: "#475569", lineHeight: 1.6 }} className="orbit-body-xs">
              {nextRing.grantsRu.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </>
        ) : (
          <p className="orbit-body-sm" style={{ margin: 0, color: "#5c4426", fontWeight: 700 }}>
            {c.allComplete}
          </p>
        )}
      </div>

      <p className="orbit-body-xs" style={{ margin: 0, color: "#94a3b8" }}>
        {c.collectedLabel}: {earnedCount} из {states.length}. {c.merchFootnote}
      </p>

      <details className="orbit-body-xs" style={{ color: "#64748b" }}>
        <summary style={{ cursor: "pointer", fontWeight: 700, color: "#7c6242" }}>{c.detailsSummary}</summary>
        <div style={{ marginTop: "0.65rem", display: "grid", gap: "0.75rem" }}>
          {states.map((state) => (
            <div
              key={state.tier.id}
              style={{
                padding: "0.55rem 0.65rem",
                borderRadius: "12px",
                background: "rgba(255,255,255,0.55)",
                border: "1px solid rgba(226, 220, 208, 0.9)",
              }}
            >
              <p style={{ margin: 0, fontWeight: 700, color: state.earned ? "#5c4426" : "#64748b" }}>
                {state.tier.order}. {state.tier.titleRu}
                {state.earned ? c.earnedSuffix : ""}
                {state.isNext ? c.nextSuffix : ""}
              </p>
              <p style={{ margin: "0.3rem 0 0", lineHeight: 1.6 }}>{state.tier.collectViaRu}</p>
              <p style={{ margin: "0.35rem 0 0", fontWeight: 700, color: "#334155" }}>{c.inAppLabel}</p>
              <ul style={{ margin: "0.2rem 0 0", paddingLeft: "1.1rem", lineHeight: 1.55 }}>
                {state.tier.grantsRu.map((g) => (
                  <li key={g}>{g}</li>
                ))}
              </ul>
              <p style={{ margin: "0.4rem 0 0", fontStyle: "italic", lineHeight: 1.55, color: "#78716c" }}>{state.tier.futureMerchRu}</p>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}
