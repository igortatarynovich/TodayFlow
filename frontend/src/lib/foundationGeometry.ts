/** Foundation Geometry — TODAYFLOW_FOUNDATION_UI §3 */

export type FoundationGeometryPreset = "profile" | "today" | "portal";

export type FoundationGeometryEmphasis = "soft" | "strong";

export type FoundationGeometryTone = "light" | "dark";

export function resolveGeometryPreset(
  preset: FoundationGeometryPreset | undefined,
  emphasis: FoundationGeometryEmphasis,
): FoundationGeometryPreset {
  if (preset) return preset;
  return emphasis === "strong" ? "portal" : "profile";
}
