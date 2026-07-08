import type { MeaningEventInput } from "@/lib/types";

export type BlockEcho = "yes" | "partial" | "no";

export const COMPATIBILITY_DEEP_BLOCK_KEYS = [
  "emotions",
  "communication",
  "conflicts",
  "sexuality",
  "long_term",
] as const;

export type CompatibilityDeepBlockKey = (typeof COMPATIBILITY_DEEP_BLOCK_KEYS)[number];

export type CompatibilityEchoTarget =
  | "main_thought"
  | "strongest_resource"
  | "main_risk"
  | `deep:${string}`
  | `scenario:${string}`;

export const COMPATIBILITY_ECHO_OPTIONS: Array<{ id: BlockEcho; label: string }> = [
  { id: "yes", label: "точно" },
  { id: "partial", label: "частично" },
  { id: "no", label: "мимо" },
];

export function isCompatibilityDeepBlockKey(key: string): key is CompatibilityDeepBlockKey {
  return (COMPATIBILITY_DEEP_BLOCK_KEYS as readonly string[]).includes(key);
}

export function blockKeyFromEchoTarget(target: CompatibilityEchoTarget): string | null {
  if (!target.startsWith("deep:")) return null;
  const key = target.slice("deep:".length);
  return isCompatibilityDeepBlockKey(key) ? key : null;
}

export type CompatibilityLearningMeta = {
  surface: string;
  scenarioId?: string | null;
  formatId?: string | null;
  toneMode?: string | null;
  fromSign?: string | null;
  toSign?: string | null;
  score?: number | null;
  /** From CUM read — user's current focus topic for learning trace. */
  cumFocusTopic?: string | null;
};

export function buildCompatibilityEchoEvent(
  meta: CompatibilityLearningMeta,
  target: CompatibilityEchoTarget,
  echo: BlockEcho,
): MeaningEventInput {
  const blockKey = blockKeyFromEchoTarget(target);
  const dayKey = new Date().toISOString().slice(0, 10);
  return {
    event_type: "compatibility_echo",
    event_source: "compatibility",
    idempotency_key: `compatibility_echo:${meta.surface}:${target}:${echo}:${dayKey}`,
    payload: {
      surface: meta.surface,
      target,
      echo,
      block_key: blockKey,
      scenario_id: meta.scenarioId ?? null,
      format_id: meta.formatId ?? meta.scenarioId ?? null,
      tone_mode: meta.toneMode ?? null,
      from_sign: meta.fromSign ?? null,
      to_sign: meta.toSign ?? null,
      score: meta.score ?? null,
      cum_focus_topic: meta.cumFocusTopic ?? null,
    },
  };
}

export function buildCompatibilityScenarioSwitchEvent(
  meta: CompatibilityLearningMeta,
  toScenarioId: string,
  href: string,
): MeaningEventInput {
  return {
    event_type: "compatibility_scenario_switch",
    event_source: "compatibility",
    idempotency_key: `compatibility_scenario_switch:${meta.surface}:${toScenarioId}:${new Date().toISOString().slice(0, 10)}`,
    payload: {
      surface: meta.surface,
      from_scenario_id: meta.scenarioId ?? null,
      to_scenario_id: toScenarioId,
      format_id: toScenarioId,
      href,
      tone_mode: meta.toneMode ?? null,
    },
  };
}

export function buildCompatibilityDeepOpenEvent(meta: CompatibilityLearningMeta): MeaningEventInput {
  return {
    event_type: "compatibility_deep_open",
    event_source: "compatibility",
    idempotency_key: `compatibility_deep_open:${meta.surface}:${meta.scenarioId ?? "unknown"}:${new Date().toISOString().slice(0, 10)}`,
    payload: {
      surface: meta.surface,
      scenario_id: meta.scenarioId ?? null,
      format_id: meta.formatId ?? meta.scenarioId ?? null,
      tone_mode: meta.toneMode ?? null,
    },
  };
}
