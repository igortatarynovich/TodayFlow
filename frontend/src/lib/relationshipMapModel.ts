import { formatMoodMapDate, type MoodMapLocale } from "@/lib/moodMapModel";
import {
  readRelationshipMapCircles,
  relationshipCircleRadius,
  type RelationshipCircleRecord,
} from "@/lib/relationshipMapStore";

export type { RelationshipCircleRecord };

export function scanRelationshipMapCircles(): RelationshipCircleRecord[] {
  return readRelationshipMapCircles().sort((a, b) => b.lastSeenAt.localeCompare(a.lastSeenAt));
}

export function buildRelationshipMapObservation(circles: RelationshipCircleRecord[], locale: MoodMapLocale): string | null {
  if (!circles.length) return null;
  const top = circles[0];
  if (locale === "ru") {
    if (circles.length >= 3) {
      return `Внимание чаще возвращается к «${top.label}» — вокруг него складывается круг.`;
    }
    return `«${top.label}» — первый узел на карте связей.`;
  }
  if (circles.length >= 3) {
    return `Attention keeps returning to "${top.label}"—a circle is forming around it.`;
  }
  return `"${top.label}"—the first node on your relationship map.`;
}

export function buildRelationshipCircleStory(circle: RelationshipCircleRecord, locale: MoodMapLocale): string {
  const seen = formatMoodMapDate(circle.lastSeenAt.slice(0, 10), locale);
  if (locale === "ru") {
    const visits =
      circle.visitCount >= 5
        ? "ты не раз возвращался к этой теме"
        : circle.visitCount >= 2
          ? "есть повторные визиты"
          : "первый заход на карту";
    return `«${circle.label}» — ${seen}. На карте: ${visits}, без процентов совместимости.`;
  }
  const visits =
    circle.visitCount >= 5
      ? "you've returned to this theme more than once"
      : circle.visitCount >= 2
        ? "repeat visits on the map"
        : "first mark on the map";
  return `"${circle.label}"—${seen}. On the map: ${visits}, no compatibility score as the story.`;
}

export function buildRelationshipShareLine(circles: RelationshipCircleRecord[], locale: MoodMapLocale): string | null {
  if (!circles.length) return null;
  const top = circles[0];
  if (locale === "ru") {
    return circles.length === 1
      ? `Моя карта связей — «${top.label}». Внимание, не проценты.`
      : `Моя карта связей в TodayFlow — ${circles.length} кругов, к которым возвращается внимание.`;
  }
  return circles.length === 1
    ? `My relationship map—"${top.label}". Attention, not percentages.`
    : `My relationship map in TodayFlow—${circles.length} circles my attention returns to.`;
}

export { relationshipCircleRadius };
