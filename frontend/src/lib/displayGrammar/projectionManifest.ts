/**
 * JSON/VM fields that may render — reverse of JSON→UI.
 * A filled legacy field without a slot_id here must stay invisible.
 */

export const PROJECTION_MANIFEST: Record<string, string> = {
  "global_context.period": "T1-hero.human_line",
  "global_day.primary_energy": "T1-hero.energy_word",
  "global_day.energy_scores": "T1-hero.energy_pct",
  "global_day.windows": "T1-clock.range",
  "global_day.drivers": "T1-clock.transit",
  "global_day.strength": "T1-strength.chip",
  "global_day.risk": "T1-risk.chip",
  "day_story.expect": "T1-hero.human_line",
  "day_story.day_personal.summary_ru": "T3.headline",
  "day_story.day_scenario.conflict.why_personal": "T3.focus_body",
  "day_story.day_personal.personal_astrology.summary_ru": "T3.focus_body",
  "day_story.do": "T3.priority",
  "day_story.today_move": "T3.priority",
  "day_story.avoid": "T3.caution",
  "personal_day.natal_overlay": "T3.focus_title",
  "ritual.card.catalog": "T2.catalog_card",
  "ritual.number.catalog": "T2.catalog_number",
  "ritual.card.lens": "T2.lens_card",
  "ritual.number.lens": "T2.lens_number",
  "gratitude.text": "T4.text",
  "profile.recognition_line": "P1.recognition_line",
  "profile.identity_core": "P1.identity_core",
  "profile.insight": "P3.insight",
  "profile.help": "P3.help",
  "profile.effort_vector": "P4.effort_vector",
  "profile.bridge_line": "P5.bridge_line",
};

/** Legacy payload fields that must not render without a new Inventory row. */
export const FORBIDDEN_RENDER_FIELDS = [
  "personal_growth.development_point",
  "primary_action",
  "storyNext",
  "T3.action",
  "benefits[]",
] as const;

export function projectionSlotForField(field: string): string | undefined {
  return PROJECTION_MANIFEST[field];
}
