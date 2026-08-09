/**
 * Make yours — proposals when a growth slot is empty.
 * Practices live on their own ScreenFlow step / `/practices` — not here.
 * Canon: docs/today/TODAY_MAKE_YOURS_AND_WELCOME_SOT.md
 */

import type { TodayContractV1 } from "@/lib/todayContract";

export type MakeYoursCategoryId =
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
  ascetic: "Аскеза",
  affirmation: "Аффирмация",
  mantra: "Мантра",
  habit: "Привычка",
  goal: "Цель",
};

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

/**
 * Build propose cards for empty categories only.
 * Never invent affirmation/habit from the same day `do`/`today_move` line —
 * those cards come from real catalogs via inline pick on the step.
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
  const primary = clean(input.contract?.primary_action);
  const growth = clean(input.contract?.personal_growth?.development_point);

  const push = (p: MakeYoursProposal) => {
    if (input.occupied[p.categoryId]) return;
    if (out.some((x) => x.categoryId === p.categoryId)) return;
    out.push(p);
  };

  if (!input.occupied.ascetic && recKind === "ascetic" && recText) {
    push({
      categoryId: "ascetic",
      categoryLabel: CATEGORY_LABEL.ascetic,
      title: recText,
      reason: recReason,
      href: "/tracking/calendar?create=ascetic",
      ctaLabel: "Выбрать аскезу",
    });
  }

  if (
    !input.occupied.affirmation &&
    (recKind === "affirmation" || recKind === "promise") &&
    recText
  ) {
    push({
      categoryId: "affirmation",
      categoryLabel: CATEGORY_LABEL.affirmation,
      title: recText,
      reason: recReason,
      href: "/affirmations",
      ctaLabel: "Выбрать аффирмацию",
    });
  }

  // Habit / mantra: catalog-only via inline picker — no invent from day move.

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
  kinds: readonly string[],
  extras?: { goal?: boolean; affirmation?: boolean; mantra?: boolean },
): MakeYoursOccupied {
  const occupied: MakeYoursOccupied = {};
  for (const kind of kinds) {
    if (kind === "habit") occupied.habit = true;
    if (kind === "ascetic") occupied.ascetic = true;
    // practice progress is tracked on the Practice step, not Make yours.
  }
  if (extras?.goal) occupied.goal = true;
  if (extras?.affirmation) occupied.affirmation = true;
  if (extras?.mantra) occupied.mantra = true;
  return occupied;
}
