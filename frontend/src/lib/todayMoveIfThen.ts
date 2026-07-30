/**
 * Wave 2 D.4 — Move act if/then from day_scenario scenes.
 * SoT: contract.day_story.day_scenario.scenes[].recommended_action / do_not.
 * No invented copy when slots empty.
 */

import type { TodayContractV1 } from "@/lib/todayContract";

export type MoveIfThenCopy = {
  do: string;
  avoid: string;
};

function clean(value: string | null | undefined): string {
  return (value || "").replace(/\s+/g, " ").trim();
}

type SceneLike = {
  role_in_story?: string | null;
  recommended_action?: string | null;
  do_not?: string | null;
};

export function pickMoveIfThenFromScenes(
  scenes: SceneLike[] | null | undefined,
): MoveIfThenCopy | null {
  if (!scenes?.length) return null;
  const ordered = [
    ...scenes.filter((s) => s.role_in_story === "primary"),
    ...scenes.filter((s) => s.role_in_story !== "primary"),
  ];
  for (const scene of ordered) {
    const doLine = clean(scene.recommended_action);
    const avoidLine = clean(scene.do_not);
    if (doLine && avoidLine) {
      return { do: doLine, avoid: avoidLine };
    }
  }
  // Single-sided: still useful if one slot is filled (honest partial).
  for (const scene of ordered) {
    const doLine = clean(scene.recommended_action);
    const avoidLine = clean(scene.do_not);
    if (doLine || avoidLine) {
      return { do: doLine, avoid: avoidLine };
    }
  }
  return null;
}

export function pickMoveIfThenFromContract(contract: TodayContractV1 | null | undefined): MoveIfThenCopy | null {
  const scenes = contract?.day_story?.day_scenario?.scenes as SceneLike[] | undefined;
  return pickMoveIfThenFromScenes(scenes);
}
