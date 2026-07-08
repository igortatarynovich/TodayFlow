"use client";

import Link from "next/link";
import type { CSSProperties, Dispatch, SetStateAction } from "react";
import { useCallback, useMemo, useState } from "react";
import { TodayEveningSection } from "@/components/today/TodayEveningSection";
import type { TodayCycleData } from "@/components/today/todayPageUtils";
import type { WeeklyGoal } from "@/components/today/todayPageUtils";
import type { TodayFourArea } from "@/components/today/todayFourAreas";
import type { SphereTriadRow, TodayGuideActionOption } from "@/components/today/todayGuideActionable";
import { TodayNarrativeView } from "@/components/today/contract/TodayNarrativeView";
import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodayNarrativeV1 } from "@/lib/todayNarrativeFromContract";
import { TodayDayHistoryStrip } from "@/components/today/TodayDayHistoryStrip";
import {
  RITUAL_BUILD_DAY_QUICK_CHIPS,
  RITUAL_COPY,
  formatActionOptionEstimatedMinutesSuffix,
  guideMeaningCompletionChipItems,
  hasGuideMeaningCompletionsPayload,
  rhythmTierLabelForScore,
} from "@/components/today/todayRitualCopy";
import type { TrackerEntityKind } from "@/app/tracking/calendar/trackerEntityCatalog";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { withOptionalGuideGenerationId } from "@/lib/todayRitualSpineMachine";

function min100(n: number) {
  return Math.max(0, Math.min(100, Math.round(n)));
}

export type TodayNarrativeGenerationIds = {
  guide: number | null;
  day_layer: number | null;
  spheres: number | null;
  evening: number | null;
};

function withNarrativeGenerationId(
  ids: TodayNarrativeGenerationIds | undefined,
  surface: keyof TodayNarrativeGenerationIds,
  payload: Record<string, unknown>,
): Record<string, unknown> {
  const raw = ids?.[surface];
  const id = typeof raw === "number" && raw > 0 ? raw : null;
  if (id == null) return payload;
  return { ...payload, generation_id: id };
}

export type TodayResultViewProps = {
  ritualTextWrap: CSSProperties;
  ritualSectionContain: CSSProperties;
  ritualChipWrap: CSSProperties;
  fourAll: TodayFourArea[];
  sphereTriadRows: SphereTriadRow[];
  mood: string | null;
  /** O6: низкий ресурс настроения — один шаг фокуса, меньше вторичных CTA и шума. */
  lowEnergyRitualMood?: boolean;
  actionOptionsRich: TodayGuideActionOption[];
  selectedActionOption: number;
  onSelectActionOption: (i: number) => void;
  focusSessionHint: boolean;
  setFocusSessionHint: (v: boolean) => void;
  onOpenHabit: (k: TrackerEntityKind) => void;
  onStartFocus20Minutes?: () => void;
  supportHooksList: string[];
  hasGoals: boolean;
  weeklyGoals: WeeklyGoal[];
  goalIdeas: { title: string; reason: string }[];
  essentials: Record<string, boolean>;
  setEssentials: Dispatch<SetStateAction<Record<string, boolean>>>;
  essentialsList: ReadonlyArray<{ id: string; label: string; explanation: string }>;
  essentialsCount: number;
  essentialsProgress: number;
  todayData: TodayCycleData;
  eveningPayload: Record<string, unknown> | null;
  eveningNarrativeLoading: boolean;
  eveningCustomPhrase: string;
  eveningMarkedDone: boolean;
  eveningObservations: { noticed: string; hardest: string; easier_than_expected: string };
  eveningReflectionInput: string;
  eveningSaving: boolean;
  onEveningCustomPhraseChange: (v: string) => void;
  onEveningMarkedDoneChange: (v: boolean) => void;
  onEveningObservationChange: (field: "noticed" | "hardest" | "easier_than_expected", value: string) => void;
  onEveningReflectionChange: (v: string) => void;
  onSaveEvening: () => void;
  onRefreshToday: () => void;
  onEveningPhaseSaved: () => void;
  eveningTarotLine: string | null;
  eveningHourCompact: boolean;
  narrativeGenerationIds?: TodayNarrativeGenerationIds;
  /** DE-7: `activity_context.guide_meaning_completions_today` с fusion за день. */
  guideMeaningCompletionsToday?: Record<string, unknown> | null;
  /** DE-9: строка из `fusion.day_history` — дублируем в «Твой день», чтобы контекст был виден у сфер. */
  fusionDayHistoryLine?: string | null;
  /** DE-9 v1.2: сводка недели из `trailing_7d_summary`. */
  fusionDayHistoryWeekLine?: string | null;
  /** DE-9 v1.4: смысловые шаги вчера. */
  fusionDayHistoryMeaningLine?: string | null;
  /** DE-9 v1.5: вечерняя заметка вчера. */
  fusionDayHistoryReflectionLine?: string | null;
  /** O7: `null` — скрыть подсказку под полоской (нет опоры вчера). */
  fusionDayHistoryFooterHint?: string | null;
  /** O11: показать дисклеймер про приблизительные проценты сфер. */
  sphereScoresProvisional?: boolean;
  /** P0.1: wire contract — заменяет legacy four areas в render path. */
  todayContract?: TodayContractV1 | null;
};

export function TodayResultView(props: TodayResultViewProps) {
  const { trackMeaningEvent } = useMeaningRuntime();
  const [sphereModalArea, setSphereModalArea] = useState<string | null>(null);
  const gmcRaw = props.guideMeaningCompletionsToday ?? null;
  const gmcPresent = hasGuideMeaningCompletionsPayload(gmcRaw);
  const meaningCompletionChips = useMemo(() => guideMeaningCompletionChipItems(gmcRaw ?? undefined), [gmcRaw]);
  const lowEnergy = !!props.lowEnergyRitualMood;
  const contract = props.todayContract;
  const useContractDomains = Boolean(contract);
  const actionOptionsForUi = useMemo(
    () => (lowEnergy ? props.actionOptionsRich.slice(0, 1) : props.actionOptionsRich),
    [lowEnergy, props.actionOptionsRich],
  );
  const effectiveActionIndex = Math.min(
    props.selectedActionOption,
    Math.max(0, actionOptionsForUi.length - 1),
  );
  const essentialsListUi = useMemo(
    () => (lowEnergy ? props.essentialsList.slice(0, 1) : props.essentialsList),
    [lowEnergy, props.essentialsList],
  );

  const closeSphereModal = useCallback(() => setSphereModalArea(null), []);

  const onDayHistoryStripFirstVisibleYourDay = useCallback(() => {
    const gid = props.narrativeGenerationIds?.guide ?? null;
    trackMeaningEvent({
      event_type: "today_day_history_first_visible",
      event_source: "today",
      quality_score: 0.45,
      payload: withOptionalGuideGenerationId({ surface: "your_day_spheres" }, gid),
    });
  }, [props.narrativeGenerationIds?.guide, trackMeaningEvent]);

  const sphereModalAreaData = sphereModalArea ? props.fourAll.find((x) => x.id === sphereModalArea) : null;
  const sphereModalRow = sphereModalArea
    ? props.sphereTriadRows.find((r) => r.area === sphereModalArea)
    : null;

  return (
    <>
      <section
        id="today-ritual-your-day"
        data-testid="today-ritual-areas"
        className="todayflow-surface-primary todayflow-inset"
        style={{ marginTop: "1.25rem", ...props.ritualSectionContain }}
      >
        {props.fusionDayHistoryLine ? (
          <TodayDayHistoryStrip
            line={props.fusionDayHistoryLine}
            footerHint={props.fusionDayHistoryFooterHint}
            weekSummaryLine={props.fusionDayHistoryWeekLine}
            meaningLine={props.fusionDayHistoryMeaningLine}
            reflectionLine={props.fusionDayHistoryReflectionLine}
            onFirstVisible={onDayHistoryStripFirstVisibleYourDay}
            ritualTextWrap={props.ritualTextWrap}
            ritualSectionContain={props.ritualSectionContain}
            style={{ marginBottom: "0.75rem" }}
          />
        ) : null}
        {useContractDomains && contract ? (
          <TodayNarrativeView narrative={buildTodayNarrativeV1(contract)} />
        ) : (
          <>
        <p className="todayflow-eyebrow" style={{ ...props.ritualTextWrap }}>
          {RITUAL_COPY.areasEyebrow}
        </p>
        <h2 className="orbit-heading-3" style={{ margin: "0.2rem 0 0.75rem", ...props.ritualTextWrap }}>
          {RITUAL_COPY.areasTitle}
        </h2>
        <p className="orbit-body-xs" style={{ margin: "0 0 0.65rem", color: "#7a6a52", lineHeight: 1.55, ...props.ritualTextWrap }}>
          {RITUAL_COPY.areasIntroToday}
        </p>
        {props.sphereScoresProvisional ? (
          <p className="orbit-body-xs" style={{ margin: "0 0 0.55rem", color: "#6a5a48", lineHeight: 1.5, ...props.ritualTextWrap }}>
            {RITUAL_COPY.areasScoresProvisionalHint}
          </p>
        ) : null}
        {!props.mood ? (
          <p className="orbit-body-sm" style={{ margin: "0 0 0.65rem", color: "#6a5132", lineHeight: 1.55, ...props.ritualTextWrap }}>
            {RITUAL_COPY.areasBeforeMoodHint}
          </p>
        ) : null}
        <div className="todayflow-stack" style={{ gap: "0.5rem" }}>
          {props.sphereTriadRows.map((row) => {
            const a = props.fourAll.find((x) => x.id === row.area);
            if (!a) return null;
            const stanceMark = row.stance === "up" ? "↑" : row.stance === "down" ? "↓" : "○";
            return (
              <div
                key={row.area}
                role="button"
                tabIndex={0}
                onClick={() => {
                  setSphereModalArea(row.area);
                  trackMeaningEvent({
                    event_type: "sphere_opened",
                    event_source: "today",
                    payload: withNarrativeGenerationId(props.narrativeGenerationIds, "guide", { sphere_id: row.area }),
                  });
                }}
                onKeyDown={(e) => {
                  if (e.target !== e.currentTarget) return;
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    setSphereModalArea(row.area);
                  }
                }}
                className="todayflow-surface-soft today-ritual-sphere-card"
                style={{
                  width: "100%",
                  maxWidth: "100%",
                  boxSizing: "border-box",
                  overflow: "hidden",
                  textAlign: "left",
                  padding: "1rem 1rem 0.95rem",
                  border: "1px solid rgba(201,168,115,0.22)",
                  background: "rgba(255,255,255,0.85)",
                  borderRadius: 18,
                  cursor: "pointer",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: "0.5rem",
                    minWidth: 0,
                  }}
                >
                  <p
                    className="orbit-body-sm"
                    style={{
                      margin: 0,
                      fontWeight: 700,
                      color: "#1f1a16",
                      flex: "1 1 auto",
                      minWidth: 0,
                      ...props.ritualTextWrap,
                    }}
                  >
                    {row.area === "love" ? RITUAL_COPY.relationshipSphereLabel : a.label}{" "}
                    <span
                      style={{ color: row.stance === "up" ? "#2d7a3e" : row.stance === "down" ? "#a33c3c" : "#7a6a52" }}
                      aria-hidden
                    >
                      {stanceMark}
                    </span>{" "}
                    <span style={{ color: "#8a4a1b", fontWeight: 700 }}>
                      {props.sphereScoresProvisional ? "≈" : ""}
                      {min100(a.score)}%
                    </span>
                  </p>
                  <p
                    className="orbit-body-xs"
                    style={{
                      margin: 0,
                      fontWeight: 700,
                      color: "#8a4a1b",
                      textAlign: "right",
                      maxWidth: "11rem",
                      flexShrink: 0,
                      ...props.ritualTextWrap,
                      lineHeight: 1.35,
                    }}
                  >
                    {a.rhythmTier}
                  </p>
                </div>
                <p
                  className="orbit-body-sm"
                  style={{
                    margin: "0.45rem 0 0",
                    color: "#2d241c",
                    lineHeight: 1.5,
                    fontWeight: 600,
                    ...props.ritualTextWrap,
                  }}
                >
                  {row.line}
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.5rem 0 0", color: "#8a7a68", fontWeight: 600, ...props.ritualTextWrap }}>
                  {RITUAL_COPY.areasTriadModalDetailHint}
                </p>
              </div>
            );
          })}
        </div>
          </>
        )}
      </section>

      <section className="todayflow-surface-soft todayflow-inset" style={{ marginTop: "1.25rem", ...props.ritualSectionContain }}>
        <p className="todayflow-eyebrow" style={{ ...props.ritualTextWrap }}>
          {RITUAL_COPY.focusEyebrow}
        </p>
        <h2 className="orbit-heading-3" style={{ margin: "0.2rem 0 0.55rem", ...props.ritualTextWrap }}>
          {RITUAL_COPY.focusTitle}
        </h2>
        <p className="orbit-body-xs" style={{ margin: "0 0 0.55rem", color: "#6a5132", lineHeight: 1.45, ...props.ritualTextWrap }}>
          {RITUAL_COPY.focusChooseOneHint}
        </p>
        {gmcPresent && !lowEnergy ? (
          <div style={{ margin: "0 0 0.55rem" }}>
            <p
              className="todayflow-eyebrow"
              style={{ margin: "0 0 0.35rem", fontSize: "0.68rem", letterSpacing: "0.06em", ...props.ritualTextWrap }}
            >
              {RITUAL_COPY.guideMeaningCompletionsEyebrow}
            </p>
            {meaningCompletionChips.length > 0 ? (
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "0.35rem",
                  ...props.ritualChipWrap,
                }}
              >
                {meaningCompletionChips.map((c) => (
                  <span
                    key={c.key}
                    className="orbit-body-xs"
                    style={{
                      padding: "0.28rem 0.6rem",
                      borderRadius: 999,
                      background: "rgba(214,142,122,0.14)",
                      border: "1px solid rgba(214,142,122,0.3)",
                      color: "#4a3828",
                      fontWeight: 700,
                    }}
                  >
                    {c.label} · {c.count}
                  </span>
                ))}
              </div>
            ) : (
              <p className="orbit-body-xs" style={{ margin: 0, color: "#5f4930", lineHeight: 1.5, ...props.ritualTextWrap }}>
                {RITUAL_COPY.guideMeaningCompletionsEmpty}
              </p>
            )}
          </div>
        ) : null}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem", marginBottom: "0.75rem" }}>
          {actionOptionsForUi.map((opt, i) => (
            <button
              key={`${opt.title}-${i}`}
              type="button"
              onClick={() => props.onSelectActionOption(i)}
              className={`orbit-button orbit-button-sm ${effectiveActionIndex === i ? "orbit-button-primary" : "orbit-button-secondary"}`}
              style={{
                width: "100%",
                justifyContent: "flex-start",
                textAlign: "left",
                borderRadius: 14,
                padding: "0.55rem 0.75rem",
                ...props.ritualTextWrap,
                whiteSpace: "normal",
                height: "auto",
                minHeight: 0,
                flexDirection: "column",
                alignItems: "stretch",
              }}
            >
              <span style={{ fontWeight: 700 }}>{opt.title}</span>
              {opt.reason ? (
                <span className="orbit-body-xs" style={{ display: "block", marginTop: 6, opacity: 0.92, fontWeight: 500 }}>
                  {opt.reason}
                  {opt.estimated_minutes != null ? formatActionOptionEstimatedMinutesSuffix(opt.estimated_minutes) : ""}
                </span>
              ) : null}
            </button>
          ))}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem", marginBottom: 0 }}>
          {!lowEnergy ? (
            <button
              type="button"
              onClick={() => {
                const opt = actionOptionsForUi[effectiveActionIndex];
                trackMeaningEvent({
                  event_type: "action_option_selected",
                  event_source: "today",
                  payload: withNarrativeGenerationId(props.narrativeGenerationIds, "guide", {
                    action_option_index: effectiveActionIndex,
                    action_option_title: opt?.title ?? "",
                  }),
                });
                props.onOpenHabit("goal");
              }}
              className="orbit-button orbit-button-secondary orbit-button-sm"
              style={{ ...props.ritualChipWrap, borderRadius: 999 }}
            >
              {RITUAL_COPY.focusPickStep}
            </button>
          ) : null}
          <button
            type="button"
            onClick={() => {
              props.setFocusSessionHint(true);
              props.onStartFocus20Minutes?.();
              const opt = actionOptionsForUi[effectiveActionIndex];
              trackMeaningEvent({
                event_type: "focus_started",
                event_source: "today",
                payload: withNarrativeGenerationId(props.narrativeGenerationIds, "guide", {
                  duration_minutes: 20,
                  action_option_index: effectiveActionIndex,
                  action_option_title: opt?.title ?? "",
                }),
              });
            }}
            className="orbit-button orbit-button-primary orbit-button-sm"
            style={{ ...props.ritualChipWrap, borderRadius: 999 }}
          >
            {RITUAL_COPY.focusStart20}
          </button>
          {!lowEnergy ? (
          <Link
            href="/tracking/calendar"
            className="orbit-button orbit-button-secondary orbit-button-sm"
            style={{
              textDecoration: "none",
              borderRadius: 999,
              display: "inline-flex",
              alignItems: "center",
              ...props.ritualChipWrap,
            }}
          >
            Flow
          </Link>
          ) : null}
        </div>
        {props.focusSessionHint ? (
          <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: "#5f4930", lineHeight: 1.5, ...props.ritualTextWrap }}>
            {RITUAL_COPY.focusStart20Hint}
          </p>
        ) : null}
      </section>

      {(props.supportHooksList.length > 0 || props.hasGoals) && !lowEnergy && (
        <section className="todayflow-surface-primary todayflow-inset" style={{ marginTop: "1.25rem", ...props.ritualSectionContain }}>
          <p className="todayflow-eyebrow" style={{ ...props.ritualTextWrap }}>
            {RITUAL_COPY.supportEyebrow}
          </p>
          <h2 className="orbit-heading-3" style={{ margin: "0.2rem 0 0.55rem", ...props.ritualTextWrap }}>
            {RITUAL_COPY.supportSectionTitle}
          </h2>
          {!props.hasGoals ? (
            <p className="orbit-body-sm" style={{ margin: "0 0 0.65rem", color: "#5f4930", lineHeight: 1.55, ...props.ritualTextWrap }}>
              {RITUAL_COPY.supportIntroNoStructure}
            </p>
          ) : null}
          {props.supportHooksList.length > 0 ? (
            <ul className="orbit-body-sm" style={{ margin: "0 0 0.65rem", paddingLeft: "1.2rem", color: "#3f3428", lineHeight: 1.55, ...props.ritualTextWrap }}>
              {props.supportHooksList.map((line) => (
                <li key={line} style={{ margin: "0.25rem 0", ...props.ritualTextWrap }}>
                  {line}
                </li>
              ))}
            </ul>
          ) : null}
          {props.hasGoals ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
              {props.weeklyGoals.slice(0, 4).map((g) => (
                <p key={g.id} className="orbit-body-sm" style={{ margin: 0, fontWeight: 600, color: "#2d241c", ...props.ritualTextWrap }}>
                  {g.title}
                </p>
              ))}
              <Link
                href="/tracking/calendar"
                className="orbit-button orbit-button-secondary orbit-button-sm"
                style={{ marginTop: "0.35rem", textDecoration: "none", borderRadius: 999, ...props.ritualChipWrap }}
              >
                Flow
              </Link>
            </div>
          ) : null}
        </section>
      )}

      {!props.hasGoals && (
        <section className="todayflow-surface-primary todayflow-inset" style={{ marginTop: "1.25rem", ...props.ritualSectionContain }}>
          <p className="todayflow-eyebrow" style={{ ...props.ritualTextWrap }}>
            {RITUAL_COPY.buildDayEyebrow}
          </p>
          <h2 className="orbit-heading-3" style={{ margin: "0.2rem 0 0.55rem", ...props.ritualTextWrap }}>
            {RITUAL_COPY.buildDayTitle}
          </h2>
          <p className="orbit-body-sm" style={{ color: "#5f4930", lineHeight: 1.55, margin: "0 0 0.6rem", ...props.ritualTextWrap }}>
            {RITUAL_COPY.buildDayBody}
          </p>
          <p className="orbit-body-xs" style={{ color: "#6b5a48", fontWeight: 600, margin: "0 0 0.35rem", letterSpacing: "0.02em", ...props.ritualTextWrap }}>
            {RITUAL_COPY.buildDayIdeasTitle}
          </p>
          <p className="orbit-body-sm" style={{ color: "#5f4930", lineHeight: 1.55, margin: "0 0 0.65rem", ...props.ritualTextWrap }}>
            {RITUAL_COPY.buildDayIdeasIntro}
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "0.75rem" }}>
            {props.goalIdeas.map((g) => (
              <div
                key={g.title}
                className="todayflow-surface-soft"
                style={{
                  padding: "0.65rem 0.85rem",
                  borderRadius: 14,
                  border: "1px solid rgba(201,168,115,0.2)",
                  background: "rgba(255,255,255,0.72)",
                  ...props.ritualSectionContain,
                }}
              >
                <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 600, color: "#2d241c", ...props.ritualTextWrap }}>
                  {g.title}
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#5f4930", lineHeight: 1.5, ...props.ritualTextWrap }}>
                  {g.reason}
                </p>
              </div>
            ))}
          </div>
          <p className="orbit-body-xs" style={{ margin: "0 0 0.5rem", color: "#7a6a52", lineHeight: 1.5, ...props.ritualTextWrap }}>
            {RITUAL_COPY.buildDayCalendarHint}
          </p>
          {!lowEnergy ? (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
              {RITUAL_BUILD_DAY_QUICK_CHIPS.map((x) => (
                <button
                  key={x.id}
                  type="button"
                  className="orbit-button orbit-button-secondary orbit-button-sm"
                  onClick={() => props.onOpenHabit(x.entityKind)}
                  style={{ ...props.ritualChipWrap, borderRadius: 999 }}
                >
                  {x.label}
                </button>
              ))}
            </div>
          ) : null}
        </section>
      )}

      <section className="todayflow-surface-soft todayflow-inset" style={{ marginTop: "1.25rem", ...props.ritualSectionContain }}>
        <p className="todayflow-eyebrow" style={{ ...props.ritualTextWrap }}>
          {RITUAL_COPY.essentialsEyebrow}
        </p>
        <h2 className="orbit-heading-3" style={{ margin: "0.2rem 0 0.5rem", ...props.ritualTextWrap }}>
          {RITUAL_COPY.essentialsTitle}
        </h2>
        <p className="orbit-body-sm" style={{ margin: "0 0 0.35rem", color: "#5f4930", lineHeight: 1.5, ...props.ritualTextWrap }}>
          {RITUAL_COPY.essentialsSub}
        </p>
        <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#6a5132", lineHeight: 1.45, ...props.ritualTextWrap }}>
          {RITUAL_COPY.essentialsPurposeHint}
        </p>
        {props.mood &&
        ["tired", "anxious", "quiet_wish", "heavy", "motivated", "move_wish", "driven", "other"].includes(props.mood) ? (
          <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#8a6c45", lineHeight: 1.45, ...props.ritualTextWrap }}>
            {RITUAL_COPY.essentialsMoodAdaptHint}
          </p>
        ) : null}
        <p
          className="orbit-body-xs"
          style={{ margin: "0 0 0.45rem", color: "#6a5132", fontWeight: 600, letterSpacing: "0.02em", ...props.ritualTextWrap }}
        >
          {RITUAL_COPY.essentialsProgressLabel(props.essentialsCount, essentialsListUi.length)}
        </p>
        <div
          style={{ height: 6, borderRadius: 99, background: "rgba(201,168,115,0.2)", overflow: "hidden", marginBottom: 6 }}
          aria-valuenow={props.essentialsCount}
          aria-valuemin={0}
          aria-valuemax={essentialsListUi.length}
          role="progressbar"
          aria-label={RITUAL_COPY.essentialsProgressLabel(props.essentialsCount, essentialsListUi.length)}
        >
          <div style={{ width: `${props.essentialsProgress}%`, height: "100%", background: "linear-gradient(90deg, #c9a873, #b88950)" }} />
        </div>
        <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#6a5132", lineHeight: 1.45, ...props.ritualTextWrap }}>
          {RITUAL_COPY.essentialsProgressExplain}
        </p>
        {essentialsListUi.map((e) => (
          <label key={e.id} style={{ display: "block", margin: "0.45rem 0", cursor: "pointer" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
              <input
                type="checkbox"
                checked={!!props.essentials[e.id]}
                onChange={() =>
                  props.setEssentials((prev) => {
                    const n = { ...prev, [e.id]: !prev[e.id] };
                    if (!prev[e.id]) {
                      trackMeaningEvent({
                        event_type: "consistency_bonus",
                        event_source: "today",
                        payload: withNarrativeGenerationId(props.narrativeGenerationIds, "guide", { essential: e.id }),
                      });
                    }
                    return n;
                  })
                }
                style={{ marginTop: 4 }}
              />
              <span style={{ minWidth: 0, ...props.ritualTextWrap }}>
                <span className="orbit-body-sm" style={{ color: "#2d241c", fontWeight: 600, ...props.ritualTextWrap }}>
                  {e.label}
                </span>
                <span
                  className="orbit-body-xs"
                  style={{ display: "block", color: "#6a5132", lineHeight: 1.45, marginTop: 4, ...props.ritualTextWrap }}
                >
                  {e.explanation}
                </span>
              </span>
            </div>
          </label>
        ))}
      </section>

      <section
        id="today-ritual-evening"
        className="todayflow-surface-primary todayflow-inset"
        style={{
          marginTop: "1.4rem",
          marginBottom: "0.5rem",
          textAlign: "center",
          ...props.ritualSectionContain,
        }}
      >
        <h2 className="orbit-heading-3" style={{ margin: 0, ...props.ritualTextWrap }}>
          {RITUAL_COPY.eveningHookTitle}
        </h2>
        <p className="orbit-body-sm" style={{ color: "#5f4930", lineHeight: 1.6, margin: "0.45rem 0 0", ...props.ritualTextWrap }}>
          {props.eveningHourCompact ? RITUAL_COPY.eveningHookBodyCompact : RITUAL_COPY.eveningHookBody}
        </p>
        {props.eveningTarotLine ? (
          <p
            className="orbit-body-sm"
            style={{
              color: "#4a3d2e",
              lineHeight: 1.6,
              margin: "0.65rem 0 0",
              textAlign: "left",
              maxWidth: "36rem",
              marginLeft: "auto",
              marginRight: "auto",
              ...props.ritualTextWrap,
            }}
          >
            {props.eveningTarotLine}
          </p>
        ) : null}
      </section>

      <details className="today-ritual-evening-details" style={{ marginTop: "0.4rem", ...props.ritualSectionContain }}>
        <summary className="orbit-body-sm" style={{ cursor: "pointer", color: "#6a4b2a", fontWeight: 600, ...props.ritualTextWrap }}>
          {RITUAL_COPY.eveningDetails}
        </summary>
        <div style={{ marginTop: 12 }}>
          <TodayEveningSection
            eveningNarrative={props.eveningPayload}
            eveningNarrativeLoading={props.eveningNarrativeLoading}
            todayData={props.todayData}
            expanded
            eveningCustomPhrase={props.eveningCustomPhrase}
            eveningMarkedDone={props.eveningMarkedDone}
            eveningObservations={props.eveningObservations}
            eveningReflectionInput={props.eveningReflectionInput}
            eveningSaving={props.eveningSaving}
            onToggleExpanded={() => undefined}
            onEveningCustomPhraseChange={props.onEveningCustomPhraseChange}
            onEveningMarkedDoneChange={props.onEveningMarkedDoneChange}
            onEveningObservationChange={props.onEveningObservationChange}
            onEveningReflectionChange={props.onEveningReflectionChange}
            onSaveEvening={props.onSaveEvening}
            onRefreshBlock={props.onRefreshToday}
            onEveningPhaseSaved={props.onEveningPhaseSaved}
          />
        </div>
      </details>

      {sphereModalArea && sphereModalAreaData ? (
        <div
          role="dialog"
          aria-modal
          aria-label={RITUAL_COPY.sphereSheetNavTitle}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 55,
            background: "rgba(15, 15, 15, 0.35)",
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "center",
          }}
          onClick={closeSphereModal}
        >
          <div
            className="todayflow-surface-primary todayflow-inset"
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "100%",
              maxWidth: 560,
              maxHeight: "70vh",
              overflow: "auto",
              borderRadius: "20px 20px 0 0",
              marginBottom: 0,
            }}
          >
            <h3 className="orbit-heading-3" style={{ margin: "0 0 0.5rem", ...props.ritualTextWrap }}>
              {sphereModalArea === "love" ? RITUAL_COPY.relationshipSphereLabel : sphereModalAreaData.label}
            </h3>
            {sphereModalRow ? (
              <p className="orbit-body-sm" style={{ margin: "0 0 0.75rem", color: "#2d241c", lineHeight: 1.5, ...props.ritualTextWrap }}>
                {sphereModalRow.line}
              </p>
            ) : null}
            <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#5f4323", ...props.ritualTextWrap }}>
              {RITUAL_COPY.areaRhythmEyebrow}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0 0 0.75rem", color: "#6a5132", lineHeight: 1.5, ...props.ritualTextWrap }}>
              {rhythmTierLabelForScore(sphereModalAreaData.score)}. {RITUAL_COPY.areaRhythmExpanded}{" "}
              {RITUAL_COPY.heroScoreFootnote(min100(sphereModalAreaData.score))}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#6a5132", ...props.ritualTextWrap }}>
              {RITUAL_COPY.areaSignal}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0 0 0.75rem", color: "#6a5132", lineHeight: 1.5, ...props.ritualTextWrap }}>
              {sphereModalAreaData.reason}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#6a5132", ...props.ritualTextWrap }}>
              {RITUAL_COPY.areaNuance}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0 0 1rem", color: "#5c4a3a", lineHeight: 1.5, ...props.ritualTextWrap }}>
              {sphereModalAreaData.watch}
            </p>
            <button type="button" onClick={closeSphereModal} className="orbit-button orbit-button-primary" style={{ width: "100%", ...props.ritualTextWrap }}>
              {RITUAL_COPY.sheetCloseCta}
            </button>
          </div>
        </div>
      ) : null}
    </>
  );
}
