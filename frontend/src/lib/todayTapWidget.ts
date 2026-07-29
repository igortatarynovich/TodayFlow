/**
 * Wave 2 Phase A — TapWidget prompt from day_scenario + API client.
 */

import { postJson, getJson } from "@/lib/api";
import type { TodayContractV1 } from "@/lib/todayContract";
import { readyDayScenario } from "@/lib/todayDaySpine";

export type TapResponseCode = "avoided_trap" | "fell_into_trap" | "not_applicable" | "skipped";

export type TapPromptScene = {
  sceneId: string;
  domain: string;
  promptedText: string;
  roleInStory: string;
};

export type TapEventV1 = {
  schema_version: string;
  event_id: string;
  user_id: string;
  day_facts_id: string;
  local_date: string;
  scene_id: string;
  domain: string;
  prompted_text: string;
  response: TapResponseCode | string;
  free_text: string | null;
  responded_at: string | null;
};

export type AccuracyBucket = { correct: number; total: number };

export type AccuracySummaryV1 = {
  schema_version: string;
  window: string;
  from_date: string;
  to_date: string;
  overall: AccuracyBucket;
  by_domain: Record<string, AccuracyBucket>;
};

const SPHERE_TO_DOMAIN: Record<string, string> = {
  work: "work",
  work_decisions: "work",
  career: "work",
  money: "money",
  finances: "money",
  money_work: "money",
  relationships: "relationships",
  love: "relationships",
  family: "relationships",
  energy: "energy",
  health: "energy",
  body: "energy",
};

export function mapSphereToDomain(sphere: string | null | undefined): string {
  const key = (sphere || "").trim().toLowerCase();
  if (key === "work" || key === "money" || key === "relationships" || key === "energy") return key;
  return SPHERE_TO_DOMAIN[key] ?? "work";
}

export function dayFactsIdAlias(userId: string | number | null | undefined, dateISO: string): string {
  return `${userId ?? "anon"}:${dateISO}`;
}

/** Pick primary, else caution, with explicit trap text — Wave 2 tap prompt. */
export function resolveTapPromptFromContract(contract: TodayContractV1): TapPromptScene | null {
  const sc = readyDayScenario(contract);
  if (!sc?.scenes?.length) return null;
  const scenes = sc.scenes as Array<Record<string, unknown>>;
  const ranked = [...scenes].sort((a, b) => {
    const rank = (role: unknown) =>
      role === "primary" ? 0 : role === "caution" ? 1 : role === "peak" ? 2 : 3;
    return rank(a.role_in_story) - rank(b.role_in_story);
  });
  for (const scene of ranked) {
    const role = String(scene.role_in_story || "");
    if (role !== "primary" && role !== "caution" && role !== "peak") continue;
    const trap = typeof scene.trap === "string" ? scene.trap.trim() : "";
    if (!trap) continue;
    const sceneId =
      (typeof scene.scene_id === "string" && scene.scene_id.trim()) ||
      (typeof scene.id === "string" && scene.id.trim()) ||
      "";
    if (!sceneId) continue;
    return {
      sceneId,
      domain: mapSphereToDomain(typeof scene.sphere === "string" ? scene.sphere : null),
      promptedText: trap,
      roleInStory: role,
    };
  }
  return null;
}

export async function postTapWidgetResponse(input: {
  localDate: string;
  sceneId: string;
  promptedText: string;
  response: TapResponseCode;
  domain?: string;
  freeText?: string | null;
  dayFactsId?: string | null;
}): Promise<TapEventV1> {
  return postJson<TapEventV1>("/today/tap-widget/response", {
    local_date: input.localDate,
    scene_id: input.sceneId,
    prompted_text: input.promptedText,
    response: input.response,
    domain: input.domain ?? "work",
    free_text: input.freeText ?? null,
    day_facts_id: input.dayFactsId ?? null,
  });
}

export async function fetchAccuracySummary(window = "14d"): Promise<AccuracySummaryV1> {
  return getJson<AccuracySummaryV1>(`/today/accuracy-summary?window=${encodeURIComponent(window)}`);
}

export function formatAccuracyLine(summary: AccuracySummaryV1 | null): string | null {
  if (!summary?.overall) return null;
  const { correct, total } = summary.overall;
  if (!total) return "Пока нет отметок — первый тап начнёт твою точность.";
  return `За ${summary.window.replace("d", " дней")}: ты был(а) точен(на) в ${correct} из ${total}.`;
}
