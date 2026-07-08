import type { PracticeCatalogDirectionKey } from "@/components/today/practicesCatalogContent";
import { postJson } from "@/lib/api";

export type ActiveJTBDContext = {
  generation_log_id: number;
  lane?: string | null;
  source_surface?: string | null;
  arrived_path?: string | null;
  arrived_route?: string | null;
  arrived_at?: string | null;
};

const ACTIVE_JTBD_CONTEXT_KEY = "todayflow_active_jtbd_context";
const ACTIVE_DAY_SPINE_CONTEXT_KEY = "todayflow_active_day_spine_context";

export type ActiveDaySpineContext = {
  generation_log_id?: number | null;
  action_kind?: string | null;
  action_label?: string | null;
  source_surface?: string | null;
  arrived_path?: string | null;
  target_href?: string | null;
  arrived_at?: string | null;
};

export function saveActiveJTBDContext(context: ActiveJTBDContext) {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(ACTIVE_JTBD_CONTEXT_KEY, JSON.stringify(context));
  } catch (error) {
    console.error("Failed to persist JTBD context", error);
  }
}

export function getActiveJTBDContext(): ActiveJTBDContext | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(ACTIVE_JTBD_CONTEXT_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as ActiveJTBDContext;
    if (!parsed?.generation_log_id) return null;
    return parsed;
  } catch (error) {
    console.error("Failed to read JTBD context", error);
    return null;
  }
}

export function saveActiveDaySpineContext(context: ActiveDaySpineContext) {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(ACTIVE_DAY_SPINE_CONTEXT_KEY, JSON.stringify(context));
  } catch (error) {
    console.error("Failed to persist day spine context", error);
  }
}

export function getActiveDaySpineContext(): ActiveDaySpineContext | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(ACTIVE_DAY_SPINE_CONTEXT_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as ActiveDaySpineContext;
    if (!parsed?.generation_log_id && !parsed?.arrived_path && !parsed?.target_href && !parsed?.action_kind) return null;
    return parsed;
  } catch (error) {
    console.error("Failed to read day spine context", error);
    return null;
  }
}

export async function logActiveJTBDAction(signal: string, metadata?: Record<string, unknown>) {
  const context = getActiveJTBDContext();
  const daySpineContext = getActiveDaySpineContext();
  if (!context?.generation_log_id && !daySpineContext) return;

  const generationLogId = context?.generation_log_id || daySpineContext?.generation_log_id;
  if (!generationLogId) return;

  await postJson("/learning/feedback", {
    generation_log_id: generationLogId,
    signal,
    metadata: {
      lane: context?.lane || null,
      source_surface: context?.source_surface || null,
      arrived_path: context?.arrived_path || null,
      arrived_route: context?.arrived_route || null,
      day_spine_action_kind: daySpineContext?.action_kind || null,
      day_spine_action_label: daySpineContext?.action_label || null,
      day_spine_source_surface: daySpineContext?.source_surface || null,
      day_spine_arrived_path: daySpineContext?.arrived_path || null,
      day_spine_target_href: daySpineContext?.target_href || null,
      ...metadata,
    },
  });
}

export function inferCompatibilityDefaultsFromJTBD() {
  const context = getActiveJTBDContext();
  if (!context?.lane) return null;

  if (context.lane === "love") {
    return {
      relationMode: "romantic" as const,
      compatibilityType: "full" as const,
    };
  }

  if (context.lane === "money_career") {
    return {
      relationMode: "business" as const,
      compatibilityType: "full" as const,
    };
  }

  return null;
}

export function inferPracticeDefaultsFromJTBD(): {
  goalId: string;
  direction: PracticeCatalogDirectionKey;
} | null {
  const context = getActiveJTBDContext();
  if (!context?.lane) return null;

  if (context.lane === "state") {
    return {
      goalId: "calm",
      direction: "Дыхательные практики",
    };
  }

  if (context.lane === "pattern") {
    return {
      goalId: "growth",
      direction: "Рефлексия",
    };
  }

  if (context.lane === "love") {
    return {
      goalId: "relationships",
      direction: "Открытость",
    };
  }

  if (context.lane === "money_career") {
    return {
      goalId: "focus",
      direction: "Внимание",
    };
  }

  return null;
}
