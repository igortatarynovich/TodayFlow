import { postJson } from "@/lib/api";

export type TodayNarrativeSurface = "guide" | "day_layer" | "spheres" | "evening" | "deepen";

/** DE-8: глубина одного вызова narrative (не тариф insight_depth). */
export type TodayNarrativeDepthLevel = "quick" | "normal" | "deep";

/** Явная передача в теле запроса; по умолчанию не шлём — бэк берёт `user_settings.today_narrative_depth_level`. */
export const TODAY_NARRATIVE_DEPTH_LEVEL_OVERRIDE: TodayNarrativeDepthLevel = "normal";

/** Тело `ritual_context` для POST /today/narrative (guide и при необходимости child surfaces). */
export type TodayGuideRitualContext = {
  tarot_main_id?: number;
  tarot_name_ru?: string;
  numerology_value?: string;
  mood?: string;
  /** id чипа «тема в голове» — в intent на бэке. */
  head_topic?: string;
  day_events?: string[];
};

/** Полный контекст после ритуала S4 — в POST guide (PR1: mood optional). */
export type TodayRitualNarrativePayload = {
  tarot_main_id: number;
  tarot_name_ru: string;
  numerology_value: string;
  mood?: string | null;
  day_events: string[];
  head_topic?: string | null;
};
export type TodayNarrativePolicyVersion = "clean-info-v1";
export type TodayNarrativeVoiceProfile = "live-clean-supportive-v1";

export const TODAY_NARRATIVE_POLICY_VERSION: TodayNarrativePolicyVersion = "clean-info-v1";
export const TODAY_NARRATIVE_VOICE_PROFILE: TodayNarrativeVoiceProfile = "live-clean-supportive-v1";

/** O2: только `surface: "guide"`; машиночитаемый primary якорь дня (паритет `orchestration.primary_narrative_anchor` в логе). */
export type NarrativeHierarchyV0 = {
  contract_version: "narrative_hierarchy_v0";
  primary_anchor: "day_engine_brief";
};

/** Ответ POST /today/narrative. Для `surface: "guide"` в `payload` часто есть `day_engine_brief`, `day_model` (`day_model_v0`) и `narrative_hierarchy` — см. todayGuideActionable. */
export type TodayNarrativeApiResponse = {
  generation_id: number;
  /** Тот же id, что в таблице generation_logs; для `POST /learning/feedback`. */
  generation_log_id: number;
  surface: string;
  used_fallback: boolean;
  payload: Record<string, unknown>;
  /** Урезанный срез селектора; можно передать в `metadata.profile_selector` для learning/feedback. */
  profile_selector?: Record<string, unknown> | null;
};

/** Безопасно извлекает объект `profile_selector` из ответа narrative для metadata. */
export function narrativeProfileSelectorPayload(v: unknown): Record<string, unknown> | null {
  if (v === null || v === undefined) return null;
  if (typeof v === "object" && !Array.isArray(v)) return v as Record<string, unknown>;
  return null;
}

export async function postTodayNarrative(body: {
  target_date: string;
  surface: TodayNarrativeSurface;
  parent_generation_id?: number | null;
  deepen_topic?: string | null;
  /** Если задано — переопределяет настройку аккаунта на один запрос. */
  depth_level?: TodayNarrativeDepthLevel | null;
  ritual_context?: TodayGuideRitualContext | null;
}): Promise<TodayNarrativeApiResponse> {
  const payload: Record<string, unknown> = {
    target_date: body.target_date,
    surface: body.surface,
    policy_version: TODAY_NARRATIVE_POLICY_VERSION,
    voice_profile: TODAY_NARRATIVE_VOICE_PROFILE,
  };
  if (body.parent_generation_id != null) payload.parent_generation_id = body.parent_generation_id;
  if (body.deepen_topic != null && body.deepen_topic !== "") payload.deepen_topic = body.deepen_topic;
  if (body.depth_level != null) payload.depth_level = body.depth_level;
  if (body.ritual_context != null) payload.ritual_context = body.ritual_context;
  return postJson<TodayNarrativeApiResponse>("/today/narrative", payload);
}

export function narrativeString(v: unknown): string {
  return typeof v === "string" ? v.trim() : "";
}

export function narrativeStringArray(v: unknown, fallback: string[]): string[] {
  if (!Array.isArray(v)) return fallback;
  const out = v.map((x) => (typeof x === "string" ? x.trim() : "")).filter(Boolean);
  return out.length ? out : fallback;
}
