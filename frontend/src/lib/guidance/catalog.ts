import type { TodayCycleData } from "@/components/today/todayPageUtils";
import { firstPriorityLine } from "@/components/today/todayRitualSignals";
import { getLocale, t } from "@/lib/i18n";

export type GuidanceSpreadSection = "quick" | "medium" | "deep";

export type GuidanceSpreadCatalogEntry = {
  /** Stable UI id (matches backend spread id). */
  id: string;
  section: GuidanceSpreadSection;
  title: string;
  description: string;
  fitsFor: string[];
};

function g(key: string, defaultEn: string, locale?: string): string {
  return t(key, defaultEn, undefined, locale ?? getLocale());
}

export function localizedGuidanceSpreadCatalog(locale?: string): GuidanceSpreadCatalogEntry[] {
  const L = (key: string, en: string) => g(key, en, locale);
  return [
    {
      id: "one_card",
      section: "quick",
      title: L("guidance.catalog.spread.one_card.title", "One card"),
      description: L(
        "guidance.catalog.spread.one_card.description",
        "When you want a short answer, a focal point, or a nudge for the situation.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.one_card.fit0", "what matters for me to understand?"),
        L("guidance.catalog.spread.one_card.fit1", "what should I pay attention to?"),
        L("guidance.catalog.spread.one_card.fit2", "what step should I take?"),
        L("guidance.catalog.spread.one_card.fit3", "what am I missing?"),
      ],
    },
    {
      id: "guidance_yes_no",
      section: "quick",
      title: L("guidance.catalog.spread.guidance_yes_no.title", "Yes / No"),
      description: L(
        "guidance.catalog.spread.guidance_yes_no.description",
        "Not just “yes” or “no”, but a reading: what supports the situation, what gets in the way, and where the nuance is.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.guidance_yes_no.fit0", "should I agree?"),
        L("guidance.catalog.spread.guidance_yes_no.fit1", "message this person or not?"),
        L("guidance.catalog.spread.guidance_yes_no.fit2", "move forward or not?"),
        L("guidance.catalog.spread.guidance_yes_no.fit3", "revisit the topic or not?"),
      ],
    },
    {
      id: "guidance_what_happening",
      section: "quick",
      title: L("guidance.catalog.spread.guidance_what_happening.title", "What's going on?"),
      description: L(
        "guidance.catalog.spread.guidance_what_happening.description",
        "When the situation feels fuzzy, emotions are high, and there's no clear picture.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.guidance_what_happening.fit0", "why does this hook me?"),
        L("guidance.catalog.spread.guidance_what_happening.fit1", "what's actually happening?"),
        L("guidance.catalog.spread.guidance_what_happening.fit2", "where am I fooling myself?"),
        L("guidance.catalog.spread.guidance_what_happening.fit3", "what's under the surface?"),
      ],
    },
    {
      id: "three_cards",
      section: "medium",
      title: L("guidance.catalog.spread.three_cards.title", "Three cards"),
      description: L(
        "guidance.catalog.spread.three_cards.description",
        "A classic spread for a timeline: past, present, possible movement.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.three_cards.fit0", "situation over time"),
        L("guidance.catalog.spread.three_cards.fit1", "context — now — outlook"),
      ],
    },
    {
      id: "guidance_choice_two",
      section: "medium",
      title: L("guidance.catalog.spread.guidance_choice_two.title", "Choice"),
      description: L(
        "guidance.catalog.spread.guidance_choice_two.description",
        "When you need to decide between two paths.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.guidance_choice_two.fit0", "two offers"),
        L("guidance.catalog.spread.guidance_choice_two.fit1", "leave or stay"),
        L("guidance.catalog.spread.guidance_choice_two.fit2", "two different moves"),
      ],
    },
    {
      id: "guidance_relationship_five",
      section: "medium",
      title: L("guidance.catalog.spread.guidance_relationship_five.title", "Relationships"),
      description: L(
        "guidance.catalog.spread.guidance_relationship_five.description",
        "For questions about a person, feelings, distance, pull, conflict, or uncertainty.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.guidance_relationship_five.fit0", "feelings"),
        L("guidance.catalog.spread.guidance_relationship_five.fit1", "distance"),
        L("guidance.catalog.spread.guidance_relationship_five.fit2", "ambiguity between you"),
      ],
    },
    {
      id: "guidance_sexual_five",
      section: "medium",
      title: L("guidance.catalog.spread.guidance_sexual_five.title", "Sexual dynamics"),
      description: L(
        "guidance.catalog.spread.guidance_sexual_five.description",
        "When the question touches desire, attraction, closeness, distance, tension, or how your body responds.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.guidance_sexual_five.fit0", "desire and boundaries"),
        L("guidance.catalog.spread.guidance_sexual_five.fit1", "tension in contact"),
        L("guidance.catalog.spread.guidance_sexual_five.fit2", "closeness without illusion"),
      ],
    },
    {
      id: "guidance_inner_conflict",
      section: "deep",
      title: L("guidance.catalog.spread.guidance_inner_conflict.title", "Inner conflict"),
      description: L(
        "guidance.catalog.spread.guidance_inner_conflict.description",
        "When one part of you wants one thing and another part wants something else.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.guidance_inner_conflict.fit0", "split inside"),
        L("guidance.catalog.spread.guidance_inner_conflict.fit1", "I want and I'm afraid"),
        L("guidance.catalog.spread.guidance_inner_conflict.fit2", "stuck between impulses"),
      ],
    },
    {
      id: "guidance_work_money",
      section: "deep",
      title: L("guidance.catalog.spread.guidance_work_money.title", "Work & money"),
      description: L(
        "guidance.catalog.spread.guidance_work_money.description",
        "For calls about work, projects, money, career, negotiation, and risk.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.guidance_work_money.fit0", "offer"),
        L("guidance.catalog.spread.guidance_work_money.fit1", "negotiation"),
        L("guidance.catalog.spread.guidance_work_money.fit2", "project and resources"),
        L("guidance.catalog.spread.guidance_work_money.fit3", "risk and stakes"),
      ],
    },
    {
      id: "guidance_deep_eight",
      section: "deep",
      title: L("guidance.catalog.spread.guidance_deep_eight.title", "Deep reading"),
      description: L(
        "guidance.catalog.spread.guidance_deep_eight.description",
        "When the situation is layered and one answer won't cover it.",
      ),
      fitsFor: [
        L("guidance.catalog.spread.guidance_deep_eight.fit0", "many layers"),
        L("guidance.catalog.spread.guidance_deep_eight.fit1", "several people and factors"),
        L("guidance.catalog.spread.guidance_deep_eight.fit2", "need the full map"),
      ],
    },
  ];
}

const TOPIC_IDS = ["relationships", "work", "money", "family", "choice", "inner_state", "intimacy", "other"] as const;
export type GuidanceTopicId = (typeof TOPIC_IDS)[number];

export function localizedGuidanceTopicOptions(
  locale?: string,
): ReadonlyArray<{ id: GuidanceTopicId; label: string }> {
  return TOPIC_IDS.map((id) => ({
    id,
    label: g(`guidance.catalog.topic.${id}`, TOPIC_LABEL_EN_FALLBACK[id], locale),
  }));
}

const TOPIC_LABEL_EN_FALLBACK: Record<GuidanceTopicId, string> = {
  relationships: "Relationships",
  work: "Work",
  money: "Money",
  family: "Family",
  choice: "Choice",
  inner_state: "Inner state",
  intimacy: "Sex / closeness",
  other: "Other",
};

const OUTCOME_IDS = [
  "clarity",
  "decision",
  "confirmation",
  "warning",
  "next_step",
  "understand_other",
  "understand_self",
] as const;
export type GuidanceOutcomeId = (typeof OUTCOME_IDS)[number];

export function localizedGuidanceOutcomeOptions(
  locale?: string,
): ReadonlyArray<{ id: GuidanceOutcomeId; label: string }> {
  return OUTCOME_IDS.map((id) => ({
    id,
    label: g(`guidance.catalog.outcome.${id}`, OUTCOME_LABEL_EN_FALLBACK[id], locale),
  }));
}

const OUTCOME_LABEL_EN_FALLBACK: Record<GuidanceOutcomeId, string> = {
  clarity: "Clarity",
  decision: "Decision",
  confirmation: "Confirmation",
  warning: "Heads-up",
  next_step: "Next step",
  understand_other: "Understand the other person",
  understand_self: "Understand myself",
};

const CLARIFY_IDS = ["blind_spot", "next_step", "risk", "boundary"] as const;

export function localizedGuidanceClarificationGoals(
  locale?: string,
): ReadonlyArray<{ id: (typeof CLARIFY_IDS)[number]; label: string }> {
  return CLARIFY_IDS.map((id) => ({
    id,
    label: g(`guidance.catalog.clarify.${id}`, CLARIFY_LABEL_EN_FALLBACK[id], locale),
  }));
}

const CLARIFY_LABEL_EN_FALLBACK: Record<(typeof CLARIFY_IDS)[number], string> = {
  blind_spot: "what I don't see",
  next_step: "next step",
  risk: "where the risk is",
  boundary: "healthy boundary",
};

export type GuidanceClarificationGoalId = (typeof CLARIFY_IDS)[number];

const REL_ROLE_IDS = ["partner", "ex", "crush", "unclear", "sexual_pull", "other_rel"] as const;

export function localizedGuidanceRelationshipRoleOptions(
  locale?: string,
): ReadonlyArray<{ id: (typeof REL_ROLE_IDS)[number]; label: string }> {
  return REL_ROLE_IDS.map((id) => ({
    id,
    label: g(`guidance.catalog.relRole.${id}`, REL_ROLE_LABEL_EN_FALLBACK[id], locale),
  }));
}

const REL_ROLE_LABEL_EN_FALLBACK: Record<(typeof REL_ROLE_IDS)[number], string> = {
  partner: "Partner",
  ex: "Ex",
  crush: "Crush",
  unclear: "Unclear situation",
  sexual_pull: "Sexual attraction",
  other_rel: "Other",
};

const INTIMACY_IDS = ["desire", "distance", "tension", "attachment", "lack_closeness", "boundaries", "other_in"] as const;

export function localizedGuidanceIntimacyFocusOptions(
  locale?: string,
): ReadonlyArray<{ id: (typeof INTIMACY_IDS)[number]; label: string }> {
  return INTIMACY_IDS.map((id) => ({
    id,
    label: g(`guidance.catalog.intimacy.${id}`, INTIMACY_LABEL_EN_FALLBACK[id], locale),
  }));
}

const INTIMACY_LABEL_EN_FALLBACK: Record<(typeof INTIMACY_IDS)[number], string> = {
  desire: "Desire",
  distance: "Distance",
  tension: "Tension",
  attachment: "Attachment",
  lack_closeness: "Lack of closeness",
  boundaries: "Boundaries",
  other_in: "Other",
};

const SPREAD_GOAL_IDS = [
  "understand_situation",
  "choose_action",
  "understand_person",
  "see_risk",
  "close_cycle",
  "clarify_feelings",
] as const;

const SPREAD_GOAL_EN_FALLBACK: Record<(typeof SPREAD_GOAL_IDS)[number], string> = {
  understand_situation: "Understand the situation",
  choose_action: "Choose an action",
  understand_person: "Understand someone",
  see_risk: "See the risk",
  close_cycle: "Close the cycle",
  clarify_feelings: "Clarify feelings",
};

/** Цель расклада (spread session intent) — `user_intent` в POST /questions/reading. */
export function localizedGuidanceSpreadGoals(
  locale?: string,
): ReadonlyArray<{ id: (typeof SPREAD_GOAL_IDS)[number]; label: string }> {
  return SPREAD_GOAL_IDS.map((id) => ({
    id,
    label: g(`guidance.catalog.spreadGoal.${id}`, SPREAD_GOAL_EN_FALLBACK[id], locale),
  }));
}

export function userIntentFromOutcome(outcomeId: string | null | undefined): string | undefined {
  if (!outcomeId) return undefined;
  const map: Record<string, string> = {
    clarity: "understand_situation",
    decision: "choose_action",
    next_step: "choose_action",
    understand_other: "understand_person",
    understand_self: "clarify_feelings",
    warning: "see_risk",
    confirmation: "close_cycle",
  };
  return map[outcomeId];
}

export function guidanceSpreadTitle(spreadId: string | null | undefined, locale?: string): string {
  if (!spreadId) return "";
  const catalog = localizedGuidanceSpreadCatalog(locale);
  const hit = catalog.find((s) => s.id === spreadId);
  return hit?.title ?? spreadId;
}

export function guidanceTopicLabel(topicId: string | null | undefined, locale?: string): string {
  if (!topicId) return "";
  const hit = localizedGuidanceTopicOptions(locale).find((o) => o.id === topicId);
  return hit?.label ?? topicId;
}

export function formatCardOrientation(orientation: string | null | undefined, locale?: string): string {
  if (!orientation) return "";
  const o = orientation.toLowerCase();
  if (o === "reversed" || o === "reverse") {
    return g("guidance.catalog.cardOrientation.reversed", "Reversed", locale);
  }
  return g("guidance.catalog.cardOrientation.upright", "Upright", locale);
}

const TODAY_CONTEXT_MAX_LEN = 400;

/** Короткий контекст дня для `today_context_summary` в `POST /questions/reading` (паритет с iOS `TodayDashboard`). */
export function guidanceTodayContextSummaryFromCycle(cycle: TodayCycleData | null): string | undefined {
  if (!cycle?.morning || typeof cycle.morning !== "object") return undefined;
  const morning = cycle.morning as Record<string, unknown>;
  const dh = morning.daily_horoscope;
  let headline = "";
  if (dh && typeof dh === "object") {
    const h = (dh as Record<string, unknown>).headline;
    if (typeof h === "string" && h.trim()) headline = h.trim();
  }
  const priority = firstPriorityLine(morning)?.trim() ?? "";
  const parts: string[] = [];
  if (headline) parts.push(headline);
  if (priority && priority !== headline) parts.push(priority);
  const out = parts.join(" · ").trim();
  if (!out) return undefined;
  if (out.length <= TODAY_CONTEXT_MAX_LEN) return out;
  return `${out.slice(0, TODAY_CONTEXT_MAX_LEN - 1)}…`;
}

export function hubLaneHintForTopic(topicId: string | null): string | undefined {
  if (!topicId) return undefined;
  if (topicId === "relationships" || topicId === "family" || topicId === "intimacy") return "love";
  if (topicId === "work" || topicId === "money") return "money_career";
  if (topicId === "choice") return "decision";
  if (topicId === "inner_state") return "state";
  return undefined;
}

/** Подстроки (RU) — паритет `GuidanceSafetyKeywords.swift` (`ruNeedles`). */
const GUIDANCE_SAFETY_SUBSTRING_RU = [
  "суицид",
  "самоубийств",
  "насили",
  "изнасилован",
  "беремен",
  "аборт",
  "онколог",
  "инфаркт",
  "юрист",
  "адвокат",
  "суд ",
  "иск ",
  "ипотек",
  "кредит",
  "долг миллион",
] as const;

/** Фразы и безопасные для `includes` EN-токены — паритет `GuidanceSafetyKeywords.swift` (`enNeedles`). */
const GUIDANCE_SAFETY_SUBSTRING_EN = [
  "suicide",
  "suicidal",
  "kill myself",
  "end my life",
  "self-harm",
  "self harm",
  "hurt myself",
  "sexual assault",
  "domestic violence",
  "raped",
  "rapist",
  "pregnancy",
  "pregnant",
  "abortion",
  "miscarriage",
  "cancer",
  "oncology",
  "heart attack",
  "stroke",
  "lawyer",
  "attorney",
  "lawsuit",
  "malpractice",
  "court case",
  "restraining order",
  "foreclosure",
  "mortgage",
  "debt collector",
  "subpoena",
] as const;

/** Короткие EN-слова, где нужна граница слова (например `rape` vs `grape`). */
const GUIDANCE_SAFETY_REGEX_EN = [/\brape\b/i, /\braping\b/i] as const;

export function guidanceSafetyKeywords(question: string): boolean {
  const q = question.toLowerCase();
  if (GUIDANCE_SAFETY_SUBSTRING_RU.some((n) => q.includes(n))) return true;
  if (GUIDANCE_SAFETY_SUBSTRING_EN.some((n) => q.includes(n))) return true;
  return GUIDANCE_SAFETY_REGEX_EN.some((re) => re.test(q));
}
