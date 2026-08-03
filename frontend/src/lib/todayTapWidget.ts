/**
 * Wave 2 Phase A — TapWidget prompt from day_scenario + API client.
 * v3.1: trap from strongest-magnitude Reading scene (DOMAIN_MAGNITUDE irreversibility).
 */

import { postJson, getJson } from "@/lib/api";
import type { TodayContractV1 } from "@/lib/todayContract";
import { readyDayScenario } from "@/lib/todayDaySpine";
import { mapSphereToDomain, sceneMagnitudeScore } from "@/lib/todayDomainSignal";

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

export { mapSphereToDomain } from "@/lib/todayDomainSignal";

export function dayFactsIdAlias(userId: string | number | null | undefined, dateISO: string): string {
  return `${userId ?? "anon"}:${dateISO}`;
}

/**
 * Pick trap for Response: among scenes with trap text, highest magnitude wins.
 * Aligns with Reading ≤2 highlight set (same score). No trap → null (honest empty UI).
 */
export function resolveTapPromptFromContract(contract: TodayContractV1): TapPromptScene | null {
  const sc = readyDayScenario(contract);
  if (!sc?.scenes?.length) return null;
  const scenes = sc.scenes as Array<Record<string, unknown>>;

  const withTrap = scenes
    .map((scene) => {
      const trap = typeof scene.trap === "string" ? scene.trap.trim() : "";
      const sceneId =
        (typeof scene.scene_id === "string" && scene.scene_id.trim()) ||
        (typeof scene.id === "string" && scene.id.trim()) ||
        "";
      if (!trap || !sceneId) return null;
      const sphere = typeof scene.sphere === "string" ? scene.sphere : null;
      const role = String(scene.role_in_story || "");
      return {
        sceneId,
        trap,
        sphere,
        role,
        score: sceneMagnitudeScore({
          sphere,
          role_in_story: role,
          trap,
          opportunity: typeof scene.opportunity === "string" ? scene.opportunity : null,
          what_happens: typeof scene.what_happens === "string" ? scene.what_happens : null,
        }),
      };
    })
    .filter(Boolean) as Array<{
    sceneId: string;
    trap: string;
    sphere: string | null;
    role: string;
    score: number;
  }>;

  if (!withTrap.length) return null;
  withTrap.sort((a, b) => b.score - a.score);
  const top = withTrap.slice(0, 2)[0]!;
  return {
    sceneId: top.sceneId,
    domain: mapSphereToDomain(top.sphere),
    promptedText: top.trap,
    roleInStory: top.role || "primary",
  };
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
