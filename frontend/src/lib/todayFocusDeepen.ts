/**
 * Morning focus topic → Reading sphere and/or depth_layer topic.
 * Handoff CTA «Разобрать тему точнее» — no new screen; wire existing homes.
 */

import type { TodayDepthTopicId } from "@/lib/todayContract";
import type { DomainKey } from "@/lib/todayDomainVerdicts";

export const FOCUS_DEEPEN_CTA_LABEL = "Разобрать тему точнее →";

/** Reading DomainLens / scenario chapter keys (sphere-{domain}). */
export type FocusReadingSphere = DomainKey;

export type FocusDeepenTarget = {
  /** Morning focus topic id (may be null → full_day / omit). */
  focusTopicId: string | null;
  /** Reading chapter to expand, if mappable. */
  readingSphere: FocusReadingSphere | null;
  /** depth_layer topic preferred when menu offers it. */
  depthTopic: TodayDepthTopicId | null;
};

const FOCUS_TO_READING: Record<string, FocusReadingSphere> = {
  work: "work",
  money: "money",
  relations: "relationships",
  family: "relationships",
  health: "energy",
  // growth / decision / other — no 1:1 Reading domain
};

const FOCUS_TO_DEPTH: Record<string, TodayDepthTopicId> = {
  work: "career",
  money: "money",
  relations: "love",
  family: "family",
  // intimacy not offered as morning chip; health/growth/decision/other → full_day
  health: "full_day",
  growth: "full_day",
  decision: "full_day",
  other: "full_day",
};

export function readingSphereChapterId(sphere: FocusReadingSphere | string): string {
  const key = String(sphere || "").trim();
  if (!key) return "";
  return key.startsWith("sphere-") ? key : `sphere-${key}`;
}

export function resolveFocusDeepenTarget(
  focusTopicId: string | null | undefined,
  depthMenuTopics?: ReadonlyArray<string> | null,
): FocusDeepenTarget {
  const topic = (focusTopicId || "").trim() || null;
  const readingSphere = topic ? FOCUS_TO_READING[topic] ?? null : null;
  let depthTopic: TodayDepthTopicId | null = topic ? FOCUS_TO_DEPTH[topic] ?? "full_day" : "full_day";

  const menu = (depthMenuTopics ?? []).map((t) => String(t || "").trim()).filter(Boolean);
  if (menu.length > 0 && depthTopic && !menu.includes(depthTopic)) {
    // Prefer a menu item that still matches the reading domain, else first menu row.
    const fallbackByReading: Partial<Record<FocusReadingSphere, TodayDepthTopicId[]>> = {
      work: ["career", "full_day"],
      money: ["money", "full_day"],
      relationships: ["love", "intimacy", "family", "full_day"],
      energy: ["full_day"],
    };
    const candidates = readingSphere ? fallbackByReading[readingSphere] ?? ["full_day"] : ["full_day"];
    depthTopic =
      (candidates.find((c) => menu.includes(c)) as TodayDepthTopicId | undefined) ??
      (menu[0] as TodayDepthTopicId);
  }
  if (menu.length === 0) {
    depthTopic = null;
  }

  return {
    focusTopicId: topic,
    readingSphere,
    depthTopic,
  };
}

/** True when CTA can do something useful (Reading jump and/or deepen menu). */
export function canOfferFocusDeepen(input: {
  focusTopicId?: string | null;
  hasReading?: boolean;
  depthMenuTopics?: ReadonlyArray<string> | null;
}): boolean {
  if (input.hasReading) return true;
  const menu = input.depthMenuTopics ?? [];
  return menu.length > 0;
}
