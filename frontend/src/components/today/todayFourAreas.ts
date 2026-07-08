/**
 * Логика четырёх сфер ритуала «Сегодня» — паритет с `RitualFourAreaBuilder` в
 * `ios/TodayFlow/TodayFlow/Views/TodayRitualFlowView.swift` (включая `selectDisplayed` ↔ `selectDisplayedSphereAreas`).
 * При изменении порогов, fallback-формул или ключей нарратива обновляй оба места.
 */
import type { FusionResponse } from "@/components/today/todayPageUtils";
import type { MeaningRingsResponse } from "@/lib/types";
import {
  RITUAL_COPY,
  formatFourAreaEnergyRiskChunk,
  fourAreaMoodSuffix,
  rhythmTierLabelForScore,
} from "@/components/today/todayRitualCopy";

export type TodayFourArea = {
  id: string;
  label: string;
  score: number;
  rhythmTier: string;
  todayHeadline: string;
  todayDetail: string;
  hasDayScenario: boolean;
  insight: string;
  watch: string;
  reason: string;
};

export function clampAreaScore(value: number): number {
  return Math.min(96, Math.max(28, Math.round(Number.isFinite(value) ? value : 28)));
}

/**
 * O11: нет сигнала по кольцам Meaning и мало разных опор в `rhythm_context` —
 * проценты у сфер условные (паритет iOS `sphereScoresProvisional`).
 */
export function computeSphereScoresProvisional(
  rings: MeaningRingsResponse["rings"] | null | undefined,
  fusion: FusionResponse | null | undefined,
): boolean {
  const hasRingSignal = Boolean(rings?.some((r) => (Number(r.score) || 0) > 0));
  if (hasRingSignal) return false;
  const rc = fusion?.rhythm_context;
  if (!rc) return true;
  let categories = 0;
  if (rc.goals?.length) categories += 1;
  if (rc.habits?.length) categories += 1;
  if (rc.ascetics?.length) categories += 1;
  const d = rc.diary;
  if (d && ((d.entries_last_7_days ?? 0) > 0 || d.has_entry_today)) categories += 1;
  return categories < 2;
}

/** Лёгкий сдвиг «опоры в ритме» по символу вытянутой карты (после «Применить к Today»). */
export function applyTarotSphereBias(
  areas: TodayFourArea[],
  bump: Partial<Record<string, number>>,
): TodayFourArea[] {
  if (!bump || Object.keys(bump).length === 0) return areas;
  return areas.map((a) => {
    const add = bump[a.id];
    if (add == null || !Number.isFinite(add)) return a;
    const score = clampAreaScore(a.score + add);
    return {
      ...a,
      score,
      rhythmTier: rhythmTierLabelForScore(score),
    };
  });
}

function narrativePick(payload: Record<string, unknown> | null | undefined, keys: string[]): string | null {
  if (!payload) return null;
  for (const key of keys) {
    const v = payload[key];
    if (typeof v === "string") {
      const t = v.trim();
      if (t) return t;
    }
  }
  return null;
}

function ringMeta(
  rings: MeaningRingsResponse["rings"] | null | undefined,
  candidates: string[],
): { score: number; contributors: string[] } | null {
  if (!rings?.length) return null;
  for (const name of candidates) {
    const x = rings.find((r) => r.ring === name || r.ring?.toLowerCase() === name.toLowerCase());
    if (x && x.score > 0) {
      return { score: x.score, contributors: x.top_contributors ?? [] };
    }
  }
  return null;
}

function pickScenarioBySlug(
  scenarios: Record<string, unknown>[] | undefined,
  slugs: string[],
): Record<string, unknown> | null {
  if (!Array.isArray(scenarios)) return null;
  for (const slug of slugs) {
    const hit = scenarios.find((s) => String((s as Record<string, unknown>)?.slug ?? "") === slug);
    if (hit) return hit as Record<string, unknown>;
  }
  return null;
}

function partsFromScenario(scenario: Record<string, unknown> | null): {
  hasScenario: boolean;
  headline: string;
  detail: string;
} {
  if (!scenario) return { hasScenario: false, headline: "", detail: "" };
  const focus = typeof scenario.focus === "string" ? scenario.focus.trim() : "";
  const summary = typeof scenario.summary === "string" ? scenario.summary.trim() : "";
  const title = typeof scenario.title === "string" ? scenario.title.trim() : "";
  const headline = (focus || title || "").trim();
  const detailRaw = summary && (!focus || summary !== focus) ? summary.trim() : "";
  return {
    hasScenario: !!(headline || detailRaw),
    headline,
    detail: detailRaw,
  };
}

function energySphereToday(
  spine: { best_mode?: string; main_risk?: string } | null,
  possible: string[],
  support: string[],
): { hasScenario: boolean; headline: string; detail: string } {
  const best = spine?.best_mode?.trim() || "";
  const risk = spine?.main_risk?.trim() || "";
  const sup0 = support[0]?.trim() || "";
  const pos0 = possible[0]?.trim() || "";
  const headline = best || sup0 || pos0 || RITUAL_COPY.fourAreaEnergyHeadlineFallback;
  const chunks: string[] = [];
  if (pos0 && pos0 !== headline) chunks.push(pos0);
  if (risk) chunks.push(formatFourAreaEnergyRiskChunk(risk));
  const detail = chunks.join(" ");
  const hasScenario = !!(best || risk || (pos0 && pos0 !== headline) || sup0);
  return { hasScenario, headline, detail };
}

export type BuildTodayFourAreasArgs = {
  rings: MeaningRingsResponse["rings"] | null | undefined;
  fusion: FusionResponse | null;
  spine: { best_mode?: string; main_risk?: string; first_move?: string } | null;
  scenarios: Record<string, unknown>[] | undefined;
  possible: string[];
  support: string[];
  spheresNarrative: Record<string, unknown> | null | undefined;
  mood: string | null | undefined;
  /** `morning.daily_recommendations` — для дефолтного reason по деньгам, как в iOS */
  recommendations: { what_to_avoid?: string | null; what_to_do?: string | null } | null | undefined;
};

/** head_topic из check-in (как на вебе) → id сферы из `buildTodayFourAreas`. */
const HEAD_TOPIC_TO_AREA: Record<string, string> = {
  work: "work",
  money: "money",
  relations: "love",
  family: "love",
  body: "energy",
  decision: "work",
  none: "",
};

/**
 * Показываем 3–4 сферы: сильная, слабая, приоритет по ответу «что в голове», добор по убыванию score.
 * Паритет с `RitualFourAreaBuilder.selectDisplayed` в iOS.
 */
export function selectDisplayedSphereAreas(
  areas: TodayFourArea[],
  headTopic: string | null | undefined,
): TodayFourArea[] {
  if (areas.length === 0) return areas;
  const byDesc = [...areas].sort((a, b) => b.score - a.score);
  const byAsc = [...areas].sort((a, b) => a.score - b.score);
  const out: TodayFourArea[] = [];
  const seen = new Set<string>();
  const take = (a: TodayFourArea | undefined) => {
    if (!a || seen.has(a.id)) return;
    out.push(a);
    seen.add(a.id);
  };
  take(byDesc[0]);
  take(byAsc[0]);
  const hid = headTopic ? HEAD_TOPIC_TO_AREA[headTopic] : "";
  if (hid) {
    take(areas.find((x) => x.id === hid));
  }
  for (const a of byDesc) {
    if (out.length >= 4) break;
    take(a);
  }
  while (out.length < 3) {
    let added = false;
    for (const a of byDesc) {
      if (out.length >= 3) break;
      if (!seen.has(a.id)) {
        take(a);
        added = true;
      }
    }
    if (!added) break;
  }
  return out;
}

export function buildTodayFourAreas(args: BuildTodayFourAreasArgs): TodayFourArea[] {
  const { rings, fusion, spine, scenarios, possible, support, spheresNarrative, mood, recommendations } = args;
  const narrative = spheresNarrative;

  const loveM = ringMeta(rings, ["Love", "love"]);
  const workM = ringMeta(rings, ["Purpose", "purpose"]);
  const moneyM = ringMeta(rings, ["Wealth", "wealth"]);
  const energyM = ringMeta(rings, ["Energy", "energy"]);

  const loveRaw =
    loveM?.score ?? (fusion ? Math.min(100, Math.round(fusion.scores.energy + 4)) : 72);
  const workRaw =
    workM?.score ?? (fusion ? Math.min(100, Math.floor(fusion.scores.focus * 0.7 + 25)) : 68);
  const moneyRaw =
    moneyM?.score ??
    (fusion
      ? Math.min(100, Math.floor((fusion.scores.energy + fusion.scores.focus) / 2) + 8)
      : 64);
  const eAvg = fusion
    ? (fusion.scores.energy + fusion.scores.emotional_balance + fusion.scores.focus) / 3
    : 74;
  const energyRaw = energyM?.score ?? (fusion ? Math.min(100, Math.round(eAvg)) : 74);

  const love = clampAreaScore(loveRaw);
  const work = clampAreaScore(workRaw);
  const money = clampAreaScore(moneyRaw);
  const energy = clampAreaScore(energyRaw);

  const bm = spine?.best_mode?.trim() || "";
  const energyInsight = bm || RITUAL_COPY.fourAreaEnergyInsightSoftDay;
  const firstMove = spine?.first_move?.trim() || "";
  const whatToAvoid = recommendations?.what_to_avoid?.trim() || "";

  const loveSc = partsFromScenario(pickScenarioBySlug(scenarios, ["love", "family"]));
  const workSc = partsFromScenario(pickScenarioBySlug(scenarios, ["career"]));
  const moneySc = partsFromScenario(pickScenarioBySlug(scenarios, ["money"]));
  const energySc = energySphereToday(spine, possible, support);

  return [
    {
      id: "love",
      label: RITUAL_COPY.fourAreaLabelLove,
      score: love,
      rhythmTier: rhythmTierLabelForScore(love),
      todayHeadline: loveSc.headline,
      todayDetail: loveSc.detail,
      hasDayScenario: loveSc.hasScenario,
      insight:
        narrativePick(narrative, ["love_insight", "relationships_insight"]) ??
        RITUAL_COPY.fourAreaLoveInsightFallback,
      watch: RITUAL_COPY.fourAreaLoveWatch,
      reason:
        narrativePick(narrative, ["love_reason", "relationship_reason", "relationships_reason"]) ??
        RITUAL_COPY.fourAreaLoveReasonBase + fourAreaMoodSuffix(mood),
    },
    {
      id: "work",
      label: RITUAL_COPY.fourAreaLabelWork,
      score: work,
      rhythmTier: rhythmTierLabelForScore(work),
      todayHeadline: workSc.headline,
      todayDetail: workSc.detail,
      hasDayScenario: workSc.hasScenario,
      insight:
        narrativePick(narrative, ["work_insight", "career_insight", "purpose_insight"]) ??
        RITUAL_COPY.fourAreaWorkInsightFallback,
      watch: RITUAL_COPY.fourAreaWorkWatch,
      reason:
        narrativePick(narrative, ["work_reason", "career_reason", "purpose_reason"]) ??
        (firstMove || RITUAL_COPY.fourAreaWorkReasonNoFirstMoveFallback),
    },
    {
      id: "money",
      label: RITUAL_COPY.fourAreaLabelMoney,
      score: money,
      rhythmTier: rhythmTierLabelForScore(money),
      todayHeadline: moneySc.headline,
      todayDetail: moneySc.detail,
      hasDayScenario: moneySc.hasScenario,
      insight:
        narrativePick(narrative, ["money_insight", "wealth_insight", "resource_insight"]) ??
        RITUAL_COPY.fourAreaMoneyInsightFallback,
      watch: RITUAL_COPY.fourAreaMoneyWatch,
      reason:
        narrativePick(narrative, ["money_reason", "wealth_reason", "resource_reason"]) ??
        (whatToAvoid || RITUAL_COPY.fourAreaMoneyReasonNoAvoidFallback),
    },
    {
      id: "energy",
      label: RITUAL_COPY.fourAreaLabelEnergy,
      score: energy,
      rhythmTier: rhythmTierLabelForScore(energy),
      todayHeadline: energySc.headline,
      todayDetail: energySc.detail,
      hasDayScenario: energySc.hasScenario,
      insight: bm ? bm : RITUAL_COPY.fourAreaEnergyInsightNoBestModeFallback,
      watch: RITUAL_COPY.fourAreaEnergyWatch,
      reason:
        narrativePick(narrative, ["energy_reason", "body_reason", "state_reason"]) ??
        RITUAL_COPY.fourAreaEnergyReasonFallback,
    },
  ];
}
