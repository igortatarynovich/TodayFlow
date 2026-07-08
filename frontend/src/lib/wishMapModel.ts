import { formatMoodMapDate, type MoodMapLocale } from "@/lib/moodMapModel";
import { mergeWishAnchorsFromGoals, type WishAnchorRecord, type WishGoalIn } from "@/lib/wishMapStore";

export type { WishAnchorRecord, WishGoalIn };

export function buildWishAnchors(goals: WishGoalIn[]): WishAnchorRecord[] {
  return mergeWishAnchorsFromGoals(goals);
}

export function buildWishMapObservation(anchors: WishAnchorRecord[], locale: MoodMapLocale): string | null {
  if (!anchors.length) return null;
  const withSteps = anchors.filter((a) => (a.stepCount ?? 0) > 0);
  if (locale === "ru") {
    if (withSteps.length >= 2) {
      return `${withSteps.length} желания уже с малыми шагами — соз созвездие начинает складываться.`;
    }
    if (withSteps.length === 1) {
      return `«${withSteps[0].title}» — первый шаг уже на карте.`;
    }
    return `${anchors.length} якор${anchors.length === 1 ? "ь" : "я"} на карте — можно добавить маленький шаг.`;
  }
  if (withSteps.length >= 2) {
    return `${withSteps.length} wishes already have small steps—the constellation is forming.`;
  }
  if (withSteps.length === 1) {
    return `"${withSteps[0].title}"—the first step is already on the map.`;
  }
  return `${anchors.length} anchor${anchors.length === 1 ? "" : "s"} on the map—ready for a small step.`;
}

export function buildWishAnchorStory(anchor: WishAnchorRecord, locale: MoodMapLocale): string {
  const steps = anchor.stepCount ?? 0;
  if (locale === "ru") {
    if (steps >= 5) return `«${anchor.title}» — ${steps} маленьких шагов уже на карте.`;
    if (steps >= 1) return `«${anchor.title}» — история только начинается, ${steps} отметк${steps === 1 ? "а" : "и"}.`;
    return `«${anchor.title}» — якорь на карте. Следующий шаг может быть очень маленьким.`;
  }
  if (steps >= 5) return `"${anchor.title}"—${steps} small steps on the map already.`;
  if (steps >= 1) return `"${anchor.title}"—the story is beginning, ${steps} mark${steps === 1 ? "" : "s"}.`;
  return `"${anchor.title}"—an anchor on the map. The next step can be tiny.`;
}

export function buildWishShareLine(anchors: WishAnchorRecord[], locale: MoodMapLocale): string | null {
  if (!anchors.length) return null;
  const top = anchors[0];
  if (locale === "ru") {
    return anchors.length === 1
      ? `На моей карте желаний — «${top.title}». Маленькие шаги складываются в историю.`
      : `Моя карта желаний в TodayFlow — ${anchors.length} якоря, которые я берегу.`;
  }
  return anchors.length === 1
    ? `On my wish map—"${top.title}". Small steps become a story.`
    : `My wish map in TodayFlow—${anchors.length} anchors I'm tending.`;
}

export function formatWishStepDate(dateISO: string | null | undefined, locale: MoodMapLocale): string | null {
  if (!dateISO) return null;
  return formatMoodMapDate(dateISO.slice(0, 10), locale);
}
