import type { CoreProfile } from "@/lib/types";

export function productWebUserInitial(
  profile?: CoreProfile | null,
  displayName?: string | null,
): string {
  const name = profile?.person?.first_name || profile?.person?.display_name || displayName || "?";
  return name.trim().charAt(0).toUpperCase();
}

export function productWebDisplayName(
  profile?: CoreProfile | null,
  fallback?: string | null,
): string {
  return (
    profile?.person?.first_name ||
    profile?.person?.display_name ||
    fallback?.trim() ||
    "Путник"
  );
}

export function productWebProfileMeta(
  profile?: CoreProfile | null,
  extras: Array<string | null | undefined> = [],
): string | null {
  const parts = [
    profile?.numerology?.life_path != null ? `Путь ${profile.numerology.life_path}` : null,
    profile?.astro?.sun_sign ? `Солнце ${profile.astro.sun_sign}` : null,
    ...extras,
  ].filter(Boolean) as string[];
  return parts.length > 0 ? parts.join(" · ") : null;
}
