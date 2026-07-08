/** Минимум полей воронки для текста prefill (без импорта из client-компонента). */
type CompatFunnelSummary = {
  accuracy_tier?: string;
  accuracy_label?: string;
} | null | undefined;

const STORAGE_KEY = "todayflow_guidance_compat_prefill_v1";

export type GuidanceCompatibilityPrefillV1 = {
  v: 1;
  from: "compatibility";
  pair_display: string;
  relationship_context?: string;
  accuracy_tier?: string;
  score?: number;
  score_tagline?: string;
  suggested_question: string;
  topic_id: "relationships";
  relationship_role_id?: string;
  spread_id?: string;
  outcome_id?: string;
};

export type GuidanceCompatibilityPrefillInput = Omit<GuidanceCompatibilityPrefillV1, "v" | "from">;

/** Маппинг контекста совместимости → роль в Guidance (relationship_context). */
/** Режим связи на хабе /compatibility → контекст для маппинга роли Guidance. */
export function mapHubRelationModeToRelationshipContext(
  mode: "romantic" | "family" | "parent_child" | "business"
): string | undefined {
  if (mode === "romantic") return "in_relationship";
  return undefined;
}

export function mapCompatContextToGuidanceRole(ctx: string | null | undefined): string | undefined {
  const n = (ctx || "").trim().toLowerCase();
  if (!n || n === "unspecified") return undefined;
  const map: Record<string, "partner" | "ex" | "crush" | "unclear" | "sexual_pull" | "other_rel"> = {
    just_met: "crush",
    mutual_attraction: "sexual_pull",
    in_relationship: "partner",
    unclear: "unclear",
    conflict_distance: "partner",
    split_but_pull: "ex",
  };
  return map[n];
}

export function stashGuidanceCompatibilityPrefill(payload: GuidanceCompatibilityPrefillInput): void {
  if (typeof window === "undefined") return;
  const full: GuidanceCompatibilityPrefillV1 = {
    v: 1,
    from: "compatibility",
    ...payload,
    topic_id: "relationships",
  };
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(full));
  } catch {
    /* ignore quota */
  }
}

export function consumeGuidanceCompatibilityPrefill(): GuidanceCompatibilityPrefillV1 | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    sessionStorage.removeItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as GuidanceCompatibilityPrefillV1;
    if (parsed?.v !== 1 || parsed.from !== "compatibility" || !parsed.suggested_question) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function buildGuidancePrefillFromCompatibilityDynamics(result: {
  /** Если задано (например даты с подписями), подставляется вместо «имя × имя». */
  pair_display?: string;
  from_sign_name?: string;
  to_sign_name?: string;
  relationship_context?: string | null;
  score: number;
  /** Альтернатива `product_surface.score_tagline` (хаб профилей и т.п.). */
  score_tagline?: string;
  product_surface?: { score_tagline: string };
  funnel_artifact?: CompatFunnelSummary;
  personalized?: { do_focus?: string; avoid_focus?: string } | null;
}): GuidanceCompatibilityPrefillInput {
  const pair_display =
    (result.pair_display && result.pair_display.trim()) ||
    `${result.from_sign_name ?? ""} × ${result.to_sign_name ?? ""}`.trim();
  const relationship_context = result.relationship_context || undefined;
  const role = mapCompatContextToGuidanceRole(relationship_context);
  const fa = result.funnel_artifact;
  const tagline =
    (result.score_tagline || result.product_surface?.score_tagline || "").trim() || "Краткий вектор связи.";
  const lines = [
    `Совместимость: ${pair_display}. ${tagline} (общий индекс ${result.score}%).`,
    fa?.accuracy_label ? `Уровень: ${fa.accuracy_label}.` : null,
    result.personalized?.do_focus ? `Сегодня полезно (Today): ${result.personalized.do_focus}` : null,
    result.personalized?.avoid_focus ? `Сегодня осторожнее (Today): ${result.personalized.avoid_focus}` : null,
    `Мой вопрос к раскладу: что мне важно понять в нашей динамике на ближайшие 2–3 недели и какой один шаг сейчас наиболее честный?`,
  ].filter(Boolean) as string[];
  return {
    pair_display,
    relationship_context,
    accuracy_tier: fa?.accuracy_tier,
    score: result.score,
    score_tagline: tagline,
    suggested_question: lines.join("\n"),
    topic_id: "relationships",
    relationship_role_id: role,
    spread_id: "guidance_relationship_five",
    outcome_id: "next_step",
  };
}
