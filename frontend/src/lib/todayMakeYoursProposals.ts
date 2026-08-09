/**
 * Make yours — proposals when a growth slot is empty.
 * Signals only from day contract / engagement / catalogs — no invent on empty.
 * Canon: docs/today/TODAY_MAKE_YOURS_AND_WELCOME_SOT.md
 */

import type { TodayContractV1 } from "@/lib/todayContract";

export type MakeYoursCategoryId =
  | "practice"
  | "ascetic"
  | "affirmation"
  | "mantra"
  | "habit"
  | "goal";

export type MakeYoursProposal = {
  categoryId: MakeYoursCategoryId;
  categoryLabel: string;
  title: string;
  reason: string | null;
  href: string;
  ctaLabel: string;
};

export type MakeYoursOccupied = Partial<Record<MakeYoursCategoryId, boolean>>;

const CATEGORY_LABEL: Record<MakeYoursCategoryId, string> = {
  practice: "Практика",
  ascetic: "Аскеза",
  affirmation: "Аффирмация",
  mantra: "Мантра",
  habit: "Привычка",
  goal: "Цель",
};

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function firstDo(contract: TodayContractV1 | null | undefined): string | null {
  const doItems = contract?.day_story?.do;
  if (!Array.isArray(doItems)) return null;
  for (const row of doItems) {
    const t = clean(typeof row === "string" ? row : null);
    if (t) return t;
  }
  return null;
}

/**
 * Build propose cards for empty categories only.
 * Occupied slots are omitted (tracker owns them).
 */
export function buildMakeYoursProposals(input: {
  contract: TodayContractV1 | null | undefined;
  occupied: MakeYoursOccupied;
  dayGoal?: string | null;
  promiseSuggestion?: string | null;
}): MakeYoursProposal[] {
  const out: MakeYoursProposal[] = [];
  const rec = input.contract?.day_story?.practice_recommendation;
  const recKind = clean(rec?.kind).toLowerCase();
  const recText = clean(rec?.text);
  const recReason = clean(rec?.reason) || null;
  const doLine = firstDo(input.contract);
  const move = clean(input.contract?.day_story?.today_move) || doLine;
  const primary = clean(input.contract?.primary_action);
  const growth = clean(input.contract?.personal_growth?.development_point);

  const push = (p: MakeYoursProposal) => {
    if (input.occupied[p.categoryId]) return;
    if (out.some((x) => x.categoryId === p.categoryId)) return;
    out.push(p);
  };

  if (!input.occupied.practice) {
    if (recKind === "practice" && recText) {
      push({
        categoryId: "practice",
        categoryLabel: CATEGORY_LABEL.practice,
        title: recText,
        reason: recReason,
        href: "/practices",
        ctaLabel: "Открыть практики",
      });
    } else if (move) {
      push({
        categoryId: "practice",
        categoryLabel: CATEGORY_LABEL.practice,
        title: move.length > 80 ? `${move.slice(0, 77)}…` : move,
        reason: "Из опоры дня",
        href: "/practices",
        ctaLabel: "Выбрать практику",
      });
    }
  }

  if (!input.occupied.ascetic) {
    if (recKind === "ascetic" && recText) {
      push({
        categoryId: "ascetic",
        categoryLabel: CATEGORY_LABEL.ascetic,
        title: recText,
        reason: recReason,
        href: "/tracking/calendar?create=ascetic",
        ctaLabel: "Поставить аскезу",
      });
    }
  }

  if (!input.occupied.affirmation) {
    if ((recKind === "affirmation" || recKind === "promise") && recText) {
      push({
        categoryId: "affirmation",
        categoryLabel: CATEGORY_LABEL.affirmation,
        title: recText,
        reason: recReason,
        href: "/affirmations",
        ctaLabel: "К аффирмациям",
      });
    }
  }

  // Mantra: no day signal SoT yet — omit propose (catalog only via empty footer link).

  if (!input.occupied.habit) {
    const habitTitle = move || primary || growth;
    if (habitTitle) {
      push({
        categoryId: "habit",
        categoryLabel: CATEGORY_LABEL.habit,
        title: habitTitle.length > 80 ? `${habitTitle.slice(0, 77)}…` : habitTitle,
        reason: "Можно закрепить как привычку",
        href: "/tracking/calendar?create=habit",
        ctaLabel: "Поставить привычку",
      });
    }
  }

  if (!input.occupied.goal) {
    const goalTitle = clean(input.dayGoal) || clean(input.promiseSuggestion) || primary || growth;
    if (goalTitle) {
      push({
        categoryId: "goal",
        categoryLabel: CATEGORY_LABEL.goal,
        title: goalTitle.length > 80 ? `${goalTitle.slice(0, 77)}…` : goalTitle,
        reason: input.dayGoal ? "Твоё обещание на сегодня" : "Из сигналов дня",
        href: "/tracking/calendar?create=goal",
        ctaLabel: "Поставить цель",
      });
    }
  }

  return out;
}

export function makeYoursOccupiedFromProgress(
  kinds: Iterable<string>,
  extras?: { goal?: boolean; affirmation?: boolean; mantra?: boolean },
): MakeYoursOccupied {
  const occupied: MakeYoursOccupied = {};
  for (const kind of kinds) {
    if (kind === "habit") occupied.habit = true;
    if (kind === "ascetic") occupied.ascetic = true;
    if (kind === "practice") occupied.practice = true;
  }
  if (extras?.goal) occupied.goal = true;
  if (extras?.affirmation) occupied.affirmation = true;
  if (extras?.mantra) occupied.mantra = true;
  return occupied;
}
