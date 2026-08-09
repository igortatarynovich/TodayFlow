/**
 * Focus deepen chips — show only today's strongest / weakest topics.
 * Catalog may be larger; presentation filters by day_scenario magnitude.
 * Canon: docs/TODAY_DEPTH_LAYER_V1.md · user rule: not all spheres every day.
 */

import type { TodayContractDepthLayerV1, TodayContractV1, TodayDepthTopicId } from "@/lib/todayContract";
import { mapSphereToDomain, sceneMagnitudeScore } from "@/lib/todayDomainSignal";
import { readyDayScenario } from "@/lib/todayDaySpine";

type DepthMenuRow = TodayContractDepthLayerV1["menu"][number];

const DOMAIN_TO_DEPTH: Record<string, TodayDepthTopicId[]> = {
  money: ["money"],
  work: ["career"],
  relationships: ["love", "intimacy", "family"],
  energy: [],
};

const CHIP_CAP = 3;

function topicCandidatesFromSphere(sphere: string | null | undefined): TodayDepthTopicId[] {
  const domain = mapSphereToDomain(sphere);
  return DOMAIN_TO_DEPTH[domain] ?? [];
}

/**
 * Rank depth menu by today's scenes: strongest first, then weak/caution if present.
 * Falls back to original menu (capped) when scenes are empty.
 */
export function pickTodayDepthMenu(
  menu: DepthMenuRow[] | null | undefined,
  contract: TodayContractV1 | null | undefined,
  cap = CHIP_CAP,
): DepthMenuRow[] {
  const rows = Array.isArray(menu) ? menu.filter((r) => r && String(r.topic || "").trim()) : [];
  if (rows.length === 0) return [];

  const byTopic = new Map(rows.map((r) => [String(r.topic).trim(), r]));
  const sc = contract ? readyDayScenario(contract) : null;
  const scenes = (sc?.scenes ?? []).filter((s) => s && typeof s === "object");
  if (!scenes.length) {
    return rows.slice(0, Math.min(cap, rows.length));
  }

  const scored = scenes
    .map((scene) => ({
      scene,
      score: sceneMagnitudeScore({
        sphere: scene.sphere,
        role_in_story: scene.role_in_story,
        trap: scene.trap,
        opportunity: scene.opportunity,
        what_happens: scene.what_happens,
      }),
      hasTrap: Boolean(typeof scene.trap === "string" && scene.trap.trim()),
      caution: String(scene.role_in_story || "")
        .trim()
        .toLowerCase() === "caution",
    }))
    .sort((a, b) => b.score - a.score);

  const picked: DepthMenuRow[] = [];
  const seen = new Set<string>();

  const pushTopic = (topic: string) => {
    if (picked.length >= cap) return;
    if (seen.has(topic)) return;
    const row = byTopic.get(topic);
    if (!row) return;
    seen.add(topic);
    picked.push(row);
  };

  // Strongest scene → first matching menu topic.
  for (const row of scored) {
    for (const t of topicCandidatesFromSphere(row.scene.sphere)) {
      pushTopic(t);
      if (picked.length >= 1) break;
    }
    if (picked.length >= 1) break;
  }

  // Weak / danger: lowest score among trap/caution scenes (if any).
  const danger = [...scored]
    .filter((s) => s.hasTrap || s.caution)
    .sort((a, b) => a.score - b.score);
  for (const row of danger) {
    for (const t of topicCandidatesFromSphere(row.scene.sphere)) {
      pushTopic(t);
      if (picked.length >= 2) break;
    }
    if (picked.length >= 2) break;
  }

  // Fill with next strongest until cap.
  for (const row of scored) {
    for (const t of topicCandidatesFromSphere(row.scene.sphere)) {
      pushTopic(t);
    }
    if (picked.length >= cap) break;
  }

  if (picked.length === 0) {
    return rows.slice(0, Math.min(cap, rows.length));
  }
  return picked;
}
