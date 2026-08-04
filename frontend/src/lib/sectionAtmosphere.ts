/** Route → visual atmosphere. Shared shell, per-section mood via CSS vars on `html[data-atmosphere]`. */

import { usesProductWebAppShell } from "@/lib/productWebShell";

export type SectionAtmosphere =
  | "home"
  | "today"
  | "flow"
  | "profile"
  | "compatibility"
  | "practices"
  | "tarot"
  | "default";

export function resolveSectionAtmosphere(pathname: string | null | undefined): SectionAtmosphere {
  if (!pathname) return "default";
  if (pathname.startsWith("/tarot")) return "tarot";
  if (pathname.startsWith("/today")) return "today";
  if (pathname.startsWith("/flow") || pathname.startsWith("/tracking/calendar")) return "flow";
  if (pathname.startsWith("/profile")) return "profile";
  if (pathname.startsWith("/compatibility")) return "compatibility";
  if (pathname.startsWith("/practices")) return "practices";
  if (pathname === "/") return "home";
  return "default";
}

/** PWA / mobile browser chrome — matches section page bg. */
export const SECTION_THEME_COLORS: Record<SectionAtmosphere, string> = {
  home: "#f3efe8",
  today: "#f9f3ee",
  flow: "#f7f2ea",
  profile: "#f6f5f2",
  compatibility: "#f6f5f2",
  practices: "#faf9f7",
  tarot: "#07080c",
  default: "#fff9f5",
};

/**
 * Product chrome routes — Day Atmosphere + minimal footer.
 * SoT = `usesProductWebAppShell` (same surface as sidebar shell).
 */
export function isAppProductRoute(pathname: string | null | undefined): boolean {
  return usesProductWebAppShell(pathname);
}
