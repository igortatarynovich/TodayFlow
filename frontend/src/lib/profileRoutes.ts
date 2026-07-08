/** Canonical Profile routes (web). Natal chart lives inside Profile — not a separate page. */

export const PROFILE_PATH = "/profile";

/** Opens Quick Map with layer 3 (chart) expanded and scrolled into view. */
export const PROFILE_CHART_DEEP_PATH = "/profile?section=chart#profile-chart";

/** Opens Quick Map scrolled to life spheres. */
export const PROFILE_SPHERES_DEEP_PATH = "/profile?section=spheres#profile-life-spheres";

/** Full portrait layout (ProfileV0Screen) — dev/QA and pre-launch min flag off. */
export const PROFILE_V0_PATH = "/profile?view=v0";

export const PROFILE_CHART_SECTION_ID = "profile-chart";

export const PROFILE_LIFE_SPHERES_SECTION_ID = "profile-life-spheres";

export type ProfileViewMode = "quickMap" | "v0";

export function parseProfileView(raw: string | null | undefined): ProfileViewMode {
  const key = (raw ?? "").trim().toLowerCase();
  if (key === "v0" || key === "portrait") return "v0";
  return "quickMap";
}
