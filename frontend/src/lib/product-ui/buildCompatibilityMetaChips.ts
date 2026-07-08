import { ZODIAC_OPTIONS } from "@/lib/zodiacOptions";

const ZODIAC_GLYPH: Record<string, string> = {
  aries: "♈",
  taurus: "♉",
  gemini: "♊",
  cancer: "♋",
  leo: "♌",
  virgo: "♍",
  libra: "♎",
  scorpio: "♏",
  sagittarius: "♐",
  capricorn: "♑",
  aquarius: "♒",
  pisces: "♓",
};

function glyphFromSignLabel(label: string): string {
  const lower = label.trim().toLowerCase();
  for (const option of ZODIAC_OPTIONS) {
    if (lower.includes(option.name.toLowerCase())) {
      return ZODIAC_GLYPH[option.id] ?? label;
    }
  }
  return label;
}

type SynastryLayer = {
  profile_1?: string;
  profile_2?: string;
};

type CompatibilityMetaInput = {
  synastry?: Record<string, unknown> | null;
  deep_dive?: {
    knowledge?: {
      life_path_pair?: string | null;
      tarot_pair?: string | null;
    } | null;
  } | null;
  aspects?: Array<{ type: string; description?: string }>;
};

export function buildCompatibilityMetaChips(input: CompatibilityMetaInput): string[] {
  const chips: string[] = [];
  const synastry = input.synastry as { sun?: SynastryLayer; moon?: SynastryLayer } | null | undefined;

  if (synastry?.sun?.profile_1 && synastry?.sun?.profile_2) {
    chips.push(`${glyphFromSignLabel(synastry.sun.profile_1)} + ${glyphFromSignLabel(synastry.sun.profile_2)}`);
  }

  const lifePathPair = input.deep_dive?.knowledge?.life_path_pair?.trim();
  if (lifePathPair) {
    chips.push(lifePathPair);
  }

  const tarotPair = input.deep_dive?.knowledge?.tarot_pair?.trim();
  if (tarotPair) {
    chips.push(tarotPair);
  } else {
    const tarotAspect = input.aspects?.find((aspect) => /tarot|карт/i.test(aspect.type));
    if (tarotAspect?.description?.trim()) {
      chips.push(tarotAspect.description.trim());
    }
  }

  return chips.slice(0, 3);
}
