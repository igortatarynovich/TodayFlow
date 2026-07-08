import { t } from "@/lib/i18n";
import type { AstroProfile, AstroProfileSaveResponse } from "@/lib/types";
import type { CompatibilityProfileLike } from "@/lib/compatibilityRoutes";

export type BirthFactsQuotaPick = Pick<
  AstroProfile,
  | "birth_facts_corrections_remaining"
  | "birth_facts_corrections_max"
  | "birth_facts_cooldown_remaining_seconds"
>;

/** Подпись про оставшиеся уточнения данных рождения; `null` если сервер не прислал счётчики. */
export function astroBirthFactsCaption(profile: BirthFactsQuotaPick): string | null {
  const cd = profile.birth_facts_cooldown_remaining_seconds;
  if (typeof cd === "number" && cd > 0) {
    const minutes = Math.max(1, Math.ceil(cd / 60));
    return t("account.astro.birthFactsCooldownHint", undefined, { minutes });
  }
  if (
    typeof profile.birth_facts_corrections_remaining !== "number" ||
    typeof profile.birth_facts_corrections_max !== "number"
  ) {
    return null;
  }
  if (profile.birth_facts_corrections_remaining === 0) {
    return t("account.astro.birthFactsLockedHint");
  }
  return t("account.astro.birthFactsRemaining", undefined, {
    n: profile.birth_facts_corrections_remaining,
    max: profile.birth_facts_corrections_max,
  });
}

/** Вставляет или обновляет строку профиля из ответа сохранения; `core_profile` отбрасывается. */
export function mergeAstroSaveIntoProfilesList(prev: AstroProfile[], saved: AstroProfileSaveResponse): AstroProfile[] {
  const { core_profile: _ignored, ...row } = saved;
  const others = prev.filter((p) => p.id !== row.id);
  const next = [...others, row as AstroProfile];
  next.sort((a, b) => a.id - b.id);
  return next;
}

export function enrichCircleItemsWithAstroProfiles(
  items: CompatibilityProfileLike[],
  astroProfiles: AstroProfile[],
): CompatibilityProfileLike[] {
  const byId = new Map(astroProfiles.map((p) => [p.id, p]));
  return items.map((item) => {
    const row = byId.get(item.id);
    if (!row) return item;
    return {
      ...item,
      birth_facts_corrections_used: row.birth_facts_corrections_used,
      birth_facts_corrections_max: row.birth_facts_corrections_max,
      birth_facts_corrections_remaining: row.birth_facts_corrections_remaining,
      birth_facts_cooldown_remaining_seconds: row.birth_facts_cooldown_remaining_seconds,
    };
  });
}
