/**
 * Enrich Profile Step-2 why anchors with person-facing meaning.
 * SoT: PROFILE_PRODUCT_JOURNEY_FORMS_V1 §2 — never claim Sun/element chose archetype.
 */
import { applyAct2AntiDupeMeaning } from "@/lib/profilePage/journeyAntiDupe";
import type { ProfileFrameworkCard } from "@/lib/profilePage/buildProfileQuickMapData";
import type { ProfileJourneyWhyRow } from "@/lib/profilePage/buildProfileJourneyProjection";
import type { WhyAnchorPresentation } from "@/lib/profilePage/presentWhyAnchors";
import { presentWhyAnchors } from "@/lib/profilePage/presentWhyAnchors";
import type { CoreProfile } from "@/lib/types";
import {
  getLifePathEntry,
  getMoonInSignEntry,
  getRisingSignEntry,
  getSunInSignEntry,
  normalizeSignId,
} from "@/lib/zodiacKnowledge";

export type WhyFormationCard = WhyAnchorPresentation & {
  /** Person-facing load: what this contributes to the portrait. */
  meaning: string;
};

const ELEMENT_PORTRAIT_MEANING: Record<string, string> = {
  fire: "В портрете больше импульса, тепла и прямой реакции — не через долгое обдумывание.",
  earth: "В портрете больше опоры на практику, тело и ощутимый результат.",
  air: "В портрете больше мысли, дистанции и обмена идеями, прежде чем «войти» эмоцией.",
  water: "В портрете больше чувствительности: сначала проживание, потом формулировка.",
  огонь: "В портрете больше импульса, тепла и прямой реакции — не через долгое обдумывание.",
  земля: "В портрете больше опоры на практику, тело и ощутимый результат.",
  воздух: "В портрете больше мысли, дистанции и обмена идеями, прежде чем «войти» эмоцией.",
  вода: "В портрете больше чувствительности: сначала проживание, потом формулировка.",
};

function clip(text: string, max = 170): string {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= max) return clean;
  const cut = clean.slice(0, max - 1);
  const at = Math.max(cut.lastIndexOf(". "), cut.lastIndexOf("; "), cut.lastIndexOf(", "));
  if (at > 50) return cut.slice(0, at + 1).trim();
  return `${cut.trim()}…`;
}

function frameworkBody(cards: ProfileFrameworkCard[] | undefined, id: string): string | null {
  return cards?.find((c) => c.id === id)?.body?.trim() || null;
}

function meaningForSelected(
  row: WhyAnchorPresentation,
  core: CoreProfile | null | undefined,
): string {
  const lp =
    core?.portrait_why_v0?.selected_by?.find((r) => r.id === row.id)?.life_path ??
    core?.numerology?.life_path ??
    null;
  const entry = lp != null ? getLifePathEntry(lp) : null;
  const essence = entry?.essence?.trim();
  const seedLabel = row.title.replace(/^Архетип\s+/i, "").trim() || "портрета";
  const honesty = `Имя «${seedLabel}» берётся только из числа пути — не из Солнца и не из стихии.`;
  if (essence) {
    const head = essence.length > 130 ? clip(essence, 130) : essence;
    return `${head} ${honesty}`;
  }
  return clip(
    row.detail
      ? `${row.detail[0]?.toUpperCase()}${row.detail.slice(1)}. ${honesty}`
      : honesty,
  );
}

function meaningForInfluenced(
  row: WhyAnchorPresentation,
  ctx: {
    core?: CoreProfile | null;
    frameworkCards?: ProfileFrameworkCard[] | null;
  },
): string {
  const cards = ctx.frameworkCards ?? [];
  const id = row.id.toLowerCase();

  if (id === "sun") {
    const fromCard = frameworkBody(cards, "sun");
    const sunSign = ctx.core?.astro?.sun_sign;
    const fromKnowledge = sunSign
      ? getSunInSignEntry(normalizeSignId(sunSign))?.bullets?.[0]?.trim() || null
      : null;
    return clip(
      fromCard ||
        fromKnowledge ||
        "Расширяет портрет: как ты проявляешь силу и себя в мире.",
    );
  }

  if (id === "moon") {
    const fromCard = frameworkBody(cards, "moon");
    const moonValue = ctx.core?.portrait_why_v0?.portrait_influenced_by?.find((r) => r.id === "moon")
      ?.value;
    const fromKnowledge = moonValue
      ? getMoonInSignEntry(normalizeSignId(String(moonValue)))?.bullets?.[0]?.trim()
      : null;
    return clip(
      fromCard ||
        fromKnowledge ||
        "Расширяет портрет: как ты чувствуешь, восстанавливаешься и реагируешь изнутри.",
    );
  }

  if (id === "asc" || id === "rising") {
    const fromCard = frameworkBody(cards, "rising") || frameworkBody(cards, "asc");
    const ascHow = ctx.core?.character_engine_asc_v0?.asc?.how?.trim();
    const ascValue = ctx.core?.portrait_why_v0?.portrait_influenced_by?.find((r) => r.id === "asc")
      ?.value;
    const fromKnowledge = ascValue
      ? getRisingSignEntry(normalizeSignId(String(ascValue)))?.bullets?.[0]?.trim()
      : null;
    return clip(
      fromCard ||
        ascHow ||
        fromKnowledge ||
        "Расширяет портрет: первый контакт — как тебя считывают до слов.",
    );
  }

  if (id === "mc" || id === "midheaven") {
    const fromCard = frameworkBody(cards, "mc");
    const mcHow = ctx.core?.character_engine_asc_v0?.mc?.how?.trim();
    return clip(
      fromCard ||
        mcHow ||
        "Расширяет портрет: публичная роль и след, по которому судят о результате.",
    );
  }

  if (id === "element") {
    const raw =
      String(ctx.core?.astro?.sun_element || row.detail || "")
        .trim()
        .toLowerCase() || "";
    return clip(
      ELEMENT_PORTRAIT_MEANING[raw] ||
        (row.detail
          ? `Стихия «${row.detail}» задаёт фон темперамента в портрете — без права выбирать имя архетипа.`
          : "Стихия Солнца задаёт фон темперамента в портрете."),
    );
  }

  if (id === "rhythm") {
    const rhythm = ctx.core?.baseline?.rhythm_style?.trim() || row.detail;
    if (rhythm) {
      return clip(
        `Ритм развития из карты: ${rhythm[0]?.toLowerCase()}${rhythm.slice(1)}. Это способ двигаться, не причина имени архетипа.`,
      );
    }
    return "Ритм развития из стихии и модальности — как ты обычно стартуешь и держишь темп.";
  }

  if (id === "life_path") {
    return meaningForSelected(row, ctx.core);
  }

  return clip(
    row.detail
      ? `В портрете учитывается: ${row.detail}.`
      : "Опора расширяет чтение портрета рядом с именем.",
  );
}

/**
 * Present Step-2 as formation cards: selected vs influenced, each with meaning.
 * Secondary chips are retired — every influenced anchor gets a full described card.
 */
export function buildWhyFormationCards(
  rows: ProfileJourneyWhyRow[],
  ctx: {
    core?: CoreProfile | null;
    frameworkCards?: ProfileFrameworkCard[] | null;
    /** Act 1 recognition line — anti-dupe source. */
    recognitionLine?: string | null;
    /** Act 1 kitchen identity — anti-dupe source when opened. */
    identityCore?: string | null;
  } = {},
): { selected: WhyFormationCard[]; influenced: WhyFormationCard[] } {
  const { primary, secondary } = presentWhyAnchors(rows);
  const all = [...primary, ...secondary];

  const selected: WhyFormationCard[] = [];
  const influenced: WhyFormationCard[] = [];

  for (const row of all) {
    const rawMeaning =
      row.role === "selected"
        ? meaningForSelected(row, ctx.core)
        : meaningForInfluenced(row, ctx);
    const meaning = applyAct2AntiDupeMeaning({
      meaning: rawMeaning,
      anchorId: row.id,
      recognitionLine: ctx.recognitionLine,
      identityCore: ctx.identityCore,
    });
    const card: WhyFormationCard = { ...row, meaning, tier: "primary" };
    if (row.role === "selected") selected.push(card);
    else influenced.push(card);
  }

  // Stable influenced order: sun → moon → asc → mc → element → rhythm → other
  const order = ["sun", "moon", "asc", "rising", "mc", "element", "rhythm"];
  influenced.sort((a, b) => {
    const ai = order.indexOf(a.id.toLowerCase());
    const bi = order.indexOf(b.id.toLowerCase());
    const ar = ai === -1 ? 99 : ai;
    const br = bi === -1 ? 99 : bi;
    return ar - br;
  });

  return { selected, influenced };
}
