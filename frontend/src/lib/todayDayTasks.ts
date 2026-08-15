/**
 * Block 5 — day tasks (SCENARIO v3.4).
 * Max 2 assignments for *today*; daily trackers shown separately.
 * No catalog shop. No invent.
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayProgressRow } from "@/lib/todayGrowthTrackers";

export type TodayDayTaskKind = "practice" | "affirmation" | "ascetic" | "habit" | "goal";

export type TodayDayTask = {
  id: string;
  kind: TodayDayTaskKind;
  kindLabel: string;
  title: string;
  detail: string | null;
  /** today = one-off / gift; daily = ongoing streak entity */
  cadence: "today" | "daily";
};

const KIND_LABEL: Record<TodayDayTaskKind, string> = {
  practice: "Практика",
  affirmation: "Аффирмация",
  ascetic: "Аскеза",
  habit: "Привычка",
  goal: "Цель",
};

function clean(s: string | null | undefined): string | null {
  const t = String(s || "").trim();
  return t ? t : null;
}

function kindFromRec(raw: string | null | undefined): TodayDayTaskKind | null {
  const k = String(raw || "")
    .trim()
    .toLowerCase();
  if (k === "practice") return "practice";
  if (k === "affirmation" || k === "promise") return "affirmation";
  if (k === "ascetic") return "ascetic";
  if (k === "habit") return "habit";
  if (k === "goal") return "goal";
  return null;
}

export function buildTodayDayTasks(input: {
  contract: TodayContractV1 | null | undefined;
  /** Gift practice title when Move support = practice */
  practiceTitle?: string | null;
  practiceDetail?: string | null;
  /** When Move support = affirmation */
  affirmationTitle?: string | null;
  affirmationDetail?: string | null;
  progressRows?: TodayProgressRow[] | null;
  maxToday?: number;
}): { today: TodayDayTask[]; daily: TodayDayTask[] } {
  const maxToday = input.maxToday ?? 2;
  const today: TodayDayTask[] = [];
  const seen = new Set<string>();

  const pushToday = (task: TodayDayTask) => {
    if (today.length >= maxToday) return;
    const key = `${task.kind}:${task.title.toLowerCase()}`;
    if (seen.has(key)) return;
    seen.add(key);
    today.push(task);
  };

  const practiceTitle = clean(input.practiceTitle);
  if (practiceTitle) {
    pushToday({
      id: "today-practice",
      kind: "practice",
      kindLabel: KIND_LABEL.practice,
      title: practiceTitle,
      detail: clean(input.practiceDetail),
      cadence: "today",
    });
  }

  const affirmationTitle = clean(input.affirmationTitle);
  if (affirmationTitle) {
    pushToday({
      id: "today-affirmation",
      kind: "affirmation",
      kindLabel: KIND_LABEL.affirmation,
      title: affirmationTitle,
      detail: clean(input.affirmationDetail),
      cadence: "today",
    });
  }

  const rec = input.contract?.day_story?.practice_recommendation;
  const recKind = kindFromRec(rec?.kind);
  const recText = clean(rec?.text);
  const typed = Array.isArray(input.contract?.daily_actions) ? input.contract.daily_actions : [];
  for (const action of typed) {
    const k = kindFromRec(action?.kind) || (action?.kind === "reflection" ? "practice" : null);
    const text = clean(action?.text);
    if (!k || !text) continue;
    const already =
      (k === "practice" && practiceTitle) || (k === "affirmation" && affirmationTitle);
    if (already) continue;
    pushToday({
      id: `today-action-${k}-${today.length}`,
      kind: k,
      kindLabel: KIND_LABEL[k],
      title: text,
      detail: null,
      cadence: "today",
    });
  }
  if (recKind && recText) {
    // Skip if already covered by gift practice/affirmation of same kind.
    const already =
      (recKind === "practice" && practiceTitle) || (recKind === "affirmation" && affirmationTitle);
    if (!already) {
      pushToday({
        id: `today-rec-${recKind}`,
        kind: recKind,
        kindLabel: KIND_LABEL[recKind],
        title: recText,
        detail: clean(rec?.reason),
        cadence: "today",
      });
    }
  }

  const daily: TodayDayTask[] = (input.progressRows || []).map((row) => {
    const kind: TodayDayTaskKind =
      row.kind === "ascetic" ? "ascetic" : row.kind === "practice" ? "practice" : "habit";
    return {
      id: `daily-${row.id}`,
      kind,
      kindLabel: row.kindLabel || KIND_LABEL[kind],
      title: row.name,
      detail: null,
      cadence: "daily" as const,
    };
  });

  return { today, daily };
}
