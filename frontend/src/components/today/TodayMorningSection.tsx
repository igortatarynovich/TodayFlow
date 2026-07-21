"use client";

import Link from "next/link";
import { type ReactNode } from "react";
import { SectionGlyph } from "@/components/orbit/SectionGlyph";
import { DaySectionHeader, PhaseEmptyState } from "@/components/today/TodaySectionPrimitives";
import { stagePanelStyle, type MorningRitualData, type TodayCycleData } from "@/components/today/todayPageUtils";
import { PhaseStateCheckIn } from "@/components/today/TodayQuickActions";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

type TodayMorningSectionProps = {
  todayData: TodayCycleData;
  morningRitualData: MorningRitualData | null;
  expanded: boolean;
  morningIntention: string;
  savingIntention: boolean;
  refreshingMorning: boolean;
  tarotRevealed: boolean;
  numerologyRevealed: boolean;
  morningTarotDetailsOpen: boolean;
  morningNumerologyDetailsOpen: boolean;
  onToggleExpanded: () => void;
  onRefreshMorningBlock: () => void;
  onSaveMorningIntention: () => void;
  onMorningIntentionChange: (value: string) => void;
  onSetTarotRevealed: (value: boolean) => void;
  onSetNumerologyRevealed: (value: boolean) => void;
  onSetMorningTarotDetailsOpen: (value: boolean | ((prev: boolean) => boolean)) => void;
  onSetMorningNumerologyDetailsOpen: (value: boolean | ((prev: boolean) => boolean)) => void;
  onPhaseStateSaved?: () => void;
};

function trimStr(v: unknown): string {
  if (typeof v !== "string") return "";
  return v.trim();
}

type MorningDetailLine = { key: string; label: string; text: string; kind: "do" | "avoid" | "body" };

function tarotDetailLines(tarotEx: MorningRitualData["tarot_explanation"], mainBlurb: string): MorningDetailLine[] {
  if (!tarotEx || typeof tarotEx !== "object") return [];
  const main = mainBlurb.trim();
  const seen = new Set<string>();
  const lines: MorningDetailLine[] = [];

  const add = (key: string, label: string, kind: MorningDetailLine["kind"], raw: unknown) => {
    const t = trimStr(raw);
    if (!t || t === main || seen.has(t)) return;
    seen.add(t);
    lines.push({ key, label, text: t, kind });
  };

  add("why", RITUAL_COPY.morningTarotDetailWhyCard, "body", tarotEx.why_this_card);
  add("how", RITUAL_COPY.morningDetailHowDay, "body", tarotEx.how_day_looks);
  add("events", RITUAL_COPY.morningDetailPossibleEvents, "body", tarotEx.possible_events);
  add("do", RITUAL_COPY.morningDetailWhatSupports, "do", tarotEx.what_to_do);
  add("avoid", RITUAL_COPY.morningDetailWhatNotAmplify, "avoid", tarotEx.what_to_avoid);

  const kw = tarotEx.keywords;
  if (Array.isArray(kw) && kw.length) {
    const parts = kw.map((k) => trimStr(k)).filter(Boolean);
    const text = parts.join(" · ");
    if (text && text !== main && !seen.has(text)) {
      lines.push({ key: "kw", label: RITUAL_COPY.morningTarotKeywordsLabel, text, kind: "body" });
    }
  }

  return lines;
}

function numerologyDetailLines(numEx: MorningRitualData["numerology_explanation"], mainBlurb: string): MorningDetailLine[] {
  if (!numEx || typeof numEx !== "object") return [];
  const main = mainBlurb.trim();
  const seen = new Set<string>();
  const lines: MorningDetailLine[] = [];

  const add = (key: string, label: string, kind: MorningDetailLine["kind"], raw: unknown) => {
    const t = trimStr(raw);
    if (!t || t === main || seen.has(t)) return;
    seen.add(t);
    lines.push({ key, label, text: t, kind });
  };

  add("why", RITUAL_COPY.morningNumerologyDetailWhyNumber, "body", numEx.why_this_number);
  add("how", RITUAL_COPY.morningDetailHowDay, "body", numEx.how_day_looks);
  add("events", RITUAL_COPY.morningDetailPossibleEvents, "body", numEx.possible_events);
  add("meaning", RITUAL_COPY.morningNumerologyDetailSupplement, "body", numEx.meaning);
  add("do", RITUAL_COPY.morningDetailWhatSupports, "do", numEx.what_to_do);
  add("avoid", RITUAL_COPY.morningDetailWhatNotAmplify, "avoid", numEx.what_to_avoid);

  return lines;
}

const revealKeyframes = `
@keyframes today-morning-reveal {
  from { opacity: 0; transform: scale(0.94) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.today-morning-reveal-in {
  animation: today-morning-reveal 0.58s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
`;

function RevealPanel({
  revealed,
  onReveal,
  revealLabel,
  closedLabel,
  children,
}: {
  revealed: boolean;
  onReveal: () => void;
  revealLabel: string;
  closedLabel: string;
  children: ReactNode;
}) {
  return (
    <div
      style={{
        border: "1px solid rgba(202, 177, 137, 0.38)",
        borderRadius: "18px",
        background: "linear-gradient(165deg, rgba(255,253,249,0.98) 0%, rgba(255,246,232,0.95) 100%)",
        padding: "1rem",
        minHeight: "168px",
        display: "flex",
        flexDirection: "column",
        justifyContent: revealed ? "flex-start" : "center",
        alignItems: "stretch",
        boxShadow: "0 12px 28px -18px rgba(90, 60, 30, 0.25)",
      }}
    >
      {!revealed ? (
        <>
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", textAlign: "center", lineHeight: 1.55 }}>
            {closedLabel}
          </p>
          <div
            aria-hidden
            style={{
              margin: "0.85rem auto",
              width: "72px",
              height: "96px",
              borderRadius: "10px",
              background: "linear-gradient(145deg, #3d3a36 0%, #1f1d1b 55%, #2c2824 100%)",
              border: "2px solid rgba(201, 168, 115, 0.45)",
              boxShadow: "inset 0 1px 0 rgba(255,255,255,0.12), 0 6px 16px rgba(0,0,0,0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.75rem",
              opacity: 0.92,
            }}
          >
            ✦
          </div>
          <button type="button" className="orbit-button orbit-button-primary orbit-button-sm" onClick={onReveal} style={{ width: "100%" }}>
            {revealLabel}
          </button>
        </>
      ) : (
        <div className="today-morning-reveal-in" style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
          {children}
        </div>
      )}
    </div>
  );
}

export function TodayMorningSection({
  todayData,
  morningRitualData,
  expanded,
  morningIntention,
  savingIntention,
  refreshingMorning,
  tarotRevealed,
  numerologyRevealed,
  morningTarotDetailsOpen,
  morningNumerologyDetailsOpen,
  onToggleExpanded,
  onRefreshMorningBlock,
  onSaveMorningIntention,
  onMorningIntentionChange,
  onSetTarotRevealed,
  onSetNumerologyRevealed,
  onSetMorningTarotDetailsOpen,
  onSetMorningNumerologyDetailsOpen,
  onPhaseStateSaved,
}: TodayMorningSectionProps) {
  const tarotCard = morningRitualData?.tarot_card || todayData.morning?.tarot_card;
  const numerologyNumber = morningRitualData?.numerology_number || todayData.morning?.numerology_number;
  const hasTarot = Boolean(tarotCard);
  const hasNum = Boolean(numerologyNumber);

  const tarotEx = morningRitualData?.tarot_explanation;
  const numEx = morningRitualData?.numerology_explanation;

  const tarotMeaning =
    trimStr(tarotEx?.meaning) || trimStr(tarotEx?.summary) || trimStr(tarotCard?.meaning);

  const numSummary =
    trimStr(numerologyNumber?.summary) || trimStr(numEx?.summary) || trimStr(numEx?.meaning);

  const tarotDetailBlocks = tarotDetailLines(tarotEx, tarotMeaning);
  const numerologyDetailBlocks = numerologyDetailLines(numEx, numSummary);

  const allRelevantRevealed =
    (!hasTarot || tarotRevealed) && (!hasNum || numerologyRevealed) && (hasTarot || hasNum);

  return (
    <section id="meaning-section" className="todayflow-reveal" style={{ marginBottom: "var(--orbit-space-3xl)" }}>
      <style dangerouslySetInnerHTML={{ __html: revealKeyframes }} />
      <style jsx>{`
        @media (max-width: 768px) {
          .today-morning-reveal-grid {
            grid-template-columns: 1fr !important;
            gap: 0.75rem !important;
          }

          .today-morning-reveal-grid :global(.orbit-button) {
            width: 100%;
            justify-content: center;
          }

          .today-morning-intention {
            padding: 0.95rem 0.9rem !important;
          }

          .today-morning-intention :global(button) {
            width: 100%;
            justify-content: center;
          }

          .today-morning-combined {
            padding: 0.9rem 0.9rem !important;
          }
        }
      `}</style>
      <div className="todayflow-stage" style={stagePanelStyle(todayData.morning_completed, expanded)}>
        <DaySectionHeader
          icon={<SectionGlyph type="morning" size="lg" />}
          title={RITUAL_COPY.morningSectionTitle}
          done={todayData.morning_completed}
          expanded={expanded}
          onToggle={onToggleExpanded}
          hintWhenDone={null}
        />

        {expanded && (
          <>
            {todayData.morning ? (
              <div>
                {(hasTarot || hasNum) && (
                  <div
                    className="today-morning-reveal-grid"
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 240px), 1fr))",
                      gap: "0.85rem",
                      marginBottom: "var(--orbit-space-lg)",
                    }}
                  >
                    {hasTarot ? (
                      <RevealPanel
                        revealed={tarotRevealed}
                        onReveal={() => onSetTarotRevealed(true)}
                        revealLabel={RITUAL_COPY.morningTarotRevealCta}
                        closedLabel={RITUAL_COPY.morningTarotClosedHint}
                      >
                        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", fontWeight: 700 }}>
                          {RITUAL_COPY.morningTarotEyebrow}
                        </p>
                        <p className="orbit-body" style={{ margin: "0.15rem 0 0", fontWeight: 700, color: "#5f4323" }}>
                          {tarotCard?.name || RITUAL_COPY.morningTarotNameFallback}
                        </p>
                        {morningRitualData?.tarot_card?.orientation ? (
                          <p className="orbit-body-xs" style={{ margin: 0, color: "#7d6240" }}>
                            {morningRitualData.tarot_card.orientation}
                          </p>
                        ) : null}
                        {tarotMeaning ? (
                          <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#475569", lineHeight: 1.6 }}>
                            {tarotMeaning}
                          </p>
                        ) : null}
                        {tarotDetailBlocks.length ? (
                          <>
                            <button
                              type="button"
                              className="orbit-button orbit-button-secondary orbit-button-sm"
                              onClick={() => onSetMorningTarotDetailsOpen((prev) => !prev)}
                              style={{ marginTop: "0.35rem", alignSelf: "flex-start" }}
                            >
                              {morningTarotDetailsOpen ? RITUAL_COPY.morningDetailsHideCta : RITUAL_COPY.morningDetailsShowCta}
                            </button>
                            {morningTarotDetailsOpen ? (
                              <div style={{ marginTop: "0.35rem", borderTop: "1px solid rgba(202,177,137,0.28)", paddingTop: "0.45rem", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                                {tarotDetailBlocks.map((row) => (
                                  <p
                                    key={row.key}
                                    className="orbit-body-xs"
                                    style={{
                                      margin: 0,
                                      color: row.kind === "do" ? "#166534" : row.kind === "avoid" ? "#991b1b" : "#475569",
                                      lineHeight: 1.6,
                                    }}
                                  >
                                    {row.kind === "do" ? (
                                      <>✓ {row.text}</>
                                    ) : row.kind === "avoid" ? (
                                      <>⚠ {row.text}</>
                                    ) : (
                                      <>
                                        <span style={{ fontWeight: 700, color: "#5f4323" }}>{row.label}: </span>
                                        {row.text}
                                      </>
                                    )}
                                  </p>
                                ))}
                              </div>
                            ) : null}
                          </>
                        ) : null}
                        <Link
                          href="/today"
                          className="orbit-button orbit-button-secondary orbit-button-sm"
                          style={{
                            marginTop: "0.35rem",
                            alignSelf: "flex-start",
                            textDecoration: "none",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          {RITUAL_COPY.morningTarotEyebrow}
                        </Link>
                      </RevealPanel>
                    ) : null}

                    {hasNum ? (
                      <RevealPanel
                        revealed={numerologyRevealed}
                        onReveal={() => onSetNumerologyRevealed(true)}
                        revealLabel={RITUAL_COPY.numberRevealCta}
                        closedLabel={RITUAL_COPY.morningNumerologyClosedHint}
                      >
                        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", fontWeight: 700 }}>
                          {RITUAL_COPY.morningNumerologyEyebrow}
                        </p>
                        <p
                          className="orbit-body"
                          style={{
                            margin: "0.2rem 0 0",
                            fontWeight: 800,
                            color: "#5f4323",
                            fontSize: "clamp(2rem, 6vw, 2.65rem)",
                            letterSpacing: "-0.02em",
                            lineHeight: 1.1,
                          }}
                        >
                          {numerologyNumber?.value || numerologyNumber?.reduced_value || "—"}
                        </p>
                        {numSummary ? (
                          <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.6 }}>
                            {numSummary}
                          </p>
                        ) : null}
                        {numerologyDetailBlocks.length ? (
                          <>
                            <button
                              type="button"
                              className="orbit-button orbit-button-secondary orbit-button-sm"
                              onClick={() => onSetMorningNumerologyDetailsOpen((prev) => !prev)}
                              style={{ marginTop: "0.35rem", alignSelf: "flex-start" }}
                            >
                              {morningNumerologyDetailsOpen ? RITUAL_COPY.morningDetailsHideCta : RITUAL_COPY.morningDetailsShowCta}
                            </button>
                            {morningNumerologyDetailsOpen ? (
                              <div style={{ marginTop: "0.35rem", borderTop: "1px solid rgba(202,177,137,0.28)", paddingTop: "0.45rem", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                                {numerologyDetailBlocks.map((row) => (
                                  <p
                                    key={row.key}
                                    className="orbit-body-xs"
                                    style={{
                                      margin: 0,
                                      color: row.kind === "do" ? "#166534" : row.kind === "avoid" ? "#991b1b" : "#475569",
                                      lineHeight: 1.6,
                                    }}
                                  >
                                    {row.kind === "do" ? (
                                      <>✓ {row.text}</>
                                    ) : row.kind === "avoid" ? (
                                      <>⚠ {row.text}</>
                                    ) : (
                                      <>
                                        <span style={{ fontWeight: 700, color: "#5f4323" }}>{row.label}: </span>
                                        {row.text}
                                      </>
                                    )}
                                  </p>
                                ))}
                              </div>
                            ) : null}
                          </>
                        ) : null}
                      </RevealPanel>
                    ) : null}
                  </div>
                )}

                {allRelevantRevealed ? (
                  <div
                    className="today-morning-reveal-in today-morning-combined"
                    style={{
                      marginBottom: "var(--orbit-space-lg)",
                      padding: "1rem 1.1rem",
                      borderRadius: "16px",
                      border: "1px solid rgba(201, 168, 115, 0.32)",
                      background: "rgba(255, 252, 247, 0.96)",
                    }}
                  >
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#a67c3a", fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                      {RITUAL_COPY.morningCombinedSummaryEyebrow}
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "#5e4222", lineHeight: 1.65 }}>
                      {hasTarot && hasNum
                        ? RITUAL_COPY.morningCombinedBothOpenLine
                        : hasTarot
                          ? RITUAL_COPY.morningCombinedTarotOnlyLine
                          : RITUAL_COPY.morningCombinedNumberOnlyLine}
                    </p>
                  </div>
                ) : null}

                {todayData.morning.daily_recommendations?.what_to_do || todayData.morning.daily_recommendations?.what_to_avoid ? (
                  <details
                    style={{
                      marginBottom: "var(--orbit-space-lg)",
                      borderRadius: "14px",
                      background: "rgba(255, 248, 235, 0.96)",
                      border: "1px solid rgba(201,168,115,0.24)",
                      padding: "0.8rem 0.95rem",
                    }}
                  >
                    <summary className="orbit-body-sm" style={{ cursor: "pointer", color: "#5f4323", fontWeight: 700 }}>
                      {RITUAL_COPY.morningHoroscopeHintSummary}
                    </summary>
                    <div style={{ marginTop: "0.6rem", display: "grid", gap: "0.45rem" }}>
                      {todayData.morning.daily_recommendations.what_to_do ? (
                        <p className="orbit-body-sm" style={{ margin: 0, color: "#166534", lineHeight: 1.6 }}>
                          ✓ {todayData.morning.daily_recommendations.what_to_do}
                        </p>
                      ) : null}
                      {todayData.morning.daily_recommendations.what_to_avoid ? (
                        <p className="orbit-body-sm" style={{ margin: 0, color: "#991b1b", lineHeight: 1.6 }}>
                          ⚠ {todayData.morning.daily_recommendations.what_to_avoid}
                        </p>
                      ) : null}
                    </div>
                  </details>
                ) : null}

                <PhaseStateCheckIn
                  date={todayData.date}
                  phase="morning"
                  title={RITUAL_COPY.morningPhaseCheckInTitle}
                  hint={RITUAL_COPY.morningPhaseCheckInHint}
                  onSaved={onPhaseStateSaved}
                />

                <div
                  className="today-morning-intention"
                  style={{
                    padding: "1.15rem 1.2rem",
                    borderRadius: "20px",
                    border: "1px solid rgba(201, 168, 115, 0.35)",
                    background: "linear-gradient(165deg, rgba(255,255,255,0.98) 0%, rgba(255, 248, 236, 0.94) 100%)",
                    boxShadow: "0 14px 32px -22px rgba(90, 60, 30, 0.28)",
                  }}
                >
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#a67c3a", fontWeight: 700, letterSpacing: "0.07em", textTransform: "uppercase" }}>
                    {RITUAL_COPY.morningIntentionEyebrow}
                  </p>
                  <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#5e4222", lineHeight: 1.65, fontWeight: 600 }}>
                    {RITUAL_COPY.morningIntentionLead}
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6242", lineHeight: 1.6 }}>
                    {RITUAL_COPY.morningIntentionHint}
                  </p>
                  <textarea
                    value={morningIntention}
                    onChange={(e) => onMorningIntentionChange(e.target.value)}
                    placeholder={RITUAL_COPY.morningIntentionPlaceholder}
                    style={{
                      width: "100%",
                      minHeight: "96px",
                      marginTop: "0.75rem",
                      padding: "0.75rem 0.85rem",
                      borderRadius: "14px",
                      border: "1px solid rgba(202, 177, 137, 0.45)",
                      fontFamily: "inherit",
                      fontSize: "0.9375rem",
                      lineHeight: 1.55,
                      resize: "vertical",
                      background: "rgba(255,255,255,0.92)",
                      color: "#37281a",
                    }}
                  />
                  <button
                    onClick={onSaveMorningIntention}
                    disabled={savingIntention || !morningIntention.trim()}
                    className="orbit-button orbit-button-primary orbit-button-sm"
                    style={{ marginTop: "0.75rem" }}
                  >
                    {savingIntention ? RITUAL_COPY.formSavingShort : RITUAL_COPY.formSaveCta}
                  </button>
                </div>
              </div>
            ) : (
              <PhaseEmptyState
                text={RITUAL_COPY.morningEmptyStateLine}
                action={
                  <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                    <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onRefreshMorningBlock} disabled={refreshingMorning}>
                      {refreshingMorning ? RITUAL_COPY.morningRefreshingShort : RITUAL_COPY.morningRefreshBlockCta}
                    </button>
                    <Link href="/today" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none", display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
                      {RITUAL_COPY.morningTarotRevealCta}
                    </Link>
                  </div>
                }
              />
            )}
          </>
        )}
      </div>
    </section>
  );
}
