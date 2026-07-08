/** Значения query/API `relationship_context` для GET /compatibility/signs */

export const RELATIONSHIP_CONTEXT_OPTIONS = [
  { id: "just_met", label: "Только познакомились / начинаем общение" },
  { id: "mutual_attraction", label: "Есть притяжение" },
  { id: "in_relationship", label: "Уже в отношениях" },
  { id: "unclear", label: "Непонятная ситуация" },
  { id: "conflict_distance", label: "Конфликт или дистанция" },
  { id: "split_but_pull", label: "Расстались, но тянет" },
] as const;

export type RelationshipContextId = (typeof RELATIONSHIP_CONTEXT_OPTIONS)[number]["id"];

/** Короткая строка под заголовком результата: «Контекст: …». */
const WIREFRAME_LABEL_BY_ID: Record<RelationshipContextId, string> = {
  just_met: "только познакомились",
  mutual_attraction: "есть притяжение",
  in_relationship: "уже в отношениях",
  unclear: "непонятная ситуация",
  conflict_distance: "конфликт или дистанция",
  split_but_pull: "расстались, но тянет",
};

export function relationshipContextWireframeLabel(
  raw: RelationshipContextId | "" | "unspecified" | undefined | null
): string {
  if (!raw || raw === "unspecified") return "контекст не указан";
  return WIREFRAME_LABEL_BY_ID[raw as RelationshipContextId] ?? "контекст не указан";
}
