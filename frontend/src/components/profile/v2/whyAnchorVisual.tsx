"use client";

import { ElementIcon } from "@/components/visualIdentity/ElementIcon";
import { PlanetIcon } from "@/components/visualIdentity/PlanetIcon";
import { ZodiacIcon } from "@/components/visualIdentity/ZodiacIcon";
import type { ElementSlug, PlanetSlug, ZodiacSlug } from "@/lib/visualIdentity/registry";

const ZODIAC: Array<{ re: RegExp; slug: ZodiacSlug }> = [
  { re: /овен|aries/i, slug: "aries" },
  { re: /телец|taurus/i, slug: "taurus" },
  { re: /близнец|gemini/i, slug: "gemini" },
  { re: /рак|cancer/i, slug: "cancer" },
  { re: /лев|leo/i, slug: "leo" },
  { re: /дев[аеы]|virgo/i, slug: "virgo" },
  { re: /весы|libra/i, slug: "libra" },
  { re: /скорпион|scorpio/i, slug: "scorpio" },
  { re: /стрелец|sagittarius/i, slug: "sagittarius" },
  { re: /козерог|capricorn/i, slug: "capricorn" },
  { re: /водолей|aquarius/i, slug: "aquarius" },
  { re: /рыб|pisces/i, slug: "pisces" },
];

const PLANETS: Array<{ re: RegExp; slug: PlanetSlug }> = [
  { re: /солнц|sun/i, slug: "sun" },
  { re: /лун[аые]|moon/i, slug: "moon" },
  { re: /меркури|mercury/i, slug: "mercury" },
  { re: /венер|venus/i, slug: "venus" },
  { re: /марс|mars/i, slug: "mars" },
  { re: /юпитер|jupiter/i, slug: "jupiter" },
  { re: /сатурн|saturn/i, slug: "saturn" },
];

const ELEMENTS: Array<{ re: RegExp; slug: ElementSlug }> = [
  { re: /огонь|огня|fire/i, slug: "fire" },
  { re: /земл|earth/i, slug: "earth" },
  { re: /воздух|air/i, slug: "air" },
  { re: /вод[аые]|water/i, slug: "water" },
];

export type WhyAnchorVisual =
  | { kind: "planet"; slug: PlanetSlug }
  | { kind: "zodiac"; slug: ZodiacSlug }
  | { kind: "element"; slug: ElementSlug }
  | { kind: "lifePath"; digit: string }
  | { kind: "mark" };

/** Resolve a live symbol from why-anchor label — never invents prose. */
export function resolveWhyAnchorVisual(label: string, rowClass?: string): WhyAnchorVisual {
  const text = label.trim();
  if (!text) return { kind: "mark" };

  if (/путь|life\s*path|числ/i.test(text) || rowClass === "selected_by") {
    const digit = text.match(/\b([1-9]|1[12]|2[2]|3[3])\b/)?.[1];
    if (digit) return { kind: "lifePath", digit };
  }

  for (const row of PLANETS) {
    if (row.re.test(text)) return { kind: "planet", slug: row.slug };
  }
  for (const row of ELEMENTS) {
    if (row.re.test(text)) return { kind: "element", slug: row.slug };
  }
  for (const row of ZODIAC) {
    if (row.re.test(text)) return { kind: "zodiac", slug: row.slug };
  }

  return { kind: "mark" };
}

export function WhyAnchorGlyph({
  label,
  rowClass,
  size = 28,
}: {
  label: string;
  rowClass?: string;
  size?: number;
}) {
  const visual = resolveWhyAnchorVisual(label, rowClass);
  const stroke = "currentColor";

  if (visual.kind === "planet") {
    return <PlanetIcon planet={visual.slug} size={size} stroke={stroke} />;
  }
  if (visual.kind === "zodiac") {
    return <ZodiacIcon sign={visual.slug} size={size} stroke={stroke} />;
  }
  if (visual.kind === "element") {
    return <ElementIcon element={visual.slug} size={size} stroke={stroke} />;
  }
  if (visual.kind === "lifePath") {
    return (
      <span aria-hidden style={{ fontFamily: "var(--tf-font-display)", fontSize: size * 0.72, fontWeight: 600, lineHeight: 1 }}>
        {visual.digit}
      </span>
    );
  }
  return <span aria-hidden style={{ width: size, height: size, display: "inline-block" }} />;
}
