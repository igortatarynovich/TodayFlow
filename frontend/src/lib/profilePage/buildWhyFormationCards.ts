/**
 * Enrich Profile Step-2 why anchors with person-facing meaning.
 * Facts and lived meaning only — never explain product/engine mechanisms.
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
  fire: "В тебе больше импульса, тепла и прямой реакции — не через долгое обдумывание.",
  earth: "В тебе больше опоры на практику, тело и ощутимый результат.",
  air: "В тебе больше мысли, дистанции и обмена идеями, прежде чем «войти» эмоцией.",
  water: "В тебе больше чувствительности: сначала проживание, потом формулировка.",
  огонь: "В тебе больше импульса, тепла и прямой реакции — не через долгое обдумывание.",
  земля: "В тебе больше опоры на практику, тело и ощутимый результат.",
  воздух: "В тебе больше мысли, дистанции и обмена идеями, прежде чем «войти» эмоцией.",
  вода: "В тебе больше чувствительности: сначала проживание, потом формулировка.",
};

const ASC_CONTACT_BY_ELEMENT: Record<string, string> = {
  air: "В первом контакте тебя считывают по разговору, вопросам и лёгкой дистанции — ещё до близости.",
  fire: "В первом контакте тебя считывают по прямому заходу и теплу — без долгой разведки.",
  earth: "В первом контакте тебя считывают по плотности и спокойному темпу — сначала опора, потом открытость.",
  water: "В первом контакте тебя считывают по мягкой оболочке и чутью поля — тон раньше правил.",
};

/** Sign-specific first-contact (preferred over element when known). */
const ASC_CONTACT_BY_SIGN: Record<string, string> = {
  gemini: "В первом контакте — вопросы, варианты и лёгкая дистанция: тебя считывают по разговору, ещё до близости.",
  libra: "В первом контакте — баланс и взаимность: тебя считывают по тому, как ты держишь двоих.",
  aquarius: "В первом контакте — дистанция идей и свой метод: близость не равна сдаче контура.",
  aries: "В первом контакте — прямой старт без разведки: тепло и темп раньше осторожности.",
  leo: "В первом контакте — тепло и право быть увиденным: тебя считывают по присутствию.",
  sagittarius: "В первом контакте — смысл и горизонт: разговор про «зачем», не только про «как».",
  taurus: "В первом контакте — спокойная плотность: сначала опора, потом открытость.",
  virgo: "В первом контакте — точность и проверка: детали раньше большой открытости.",
  capricorn: "В первом контакте — обязательства и статус: серьёзность раньше лёгкости.",
  cancer: "В первом контакте — сначала «свои», потом открытость: тон поля раньше правил.",
  scorpio: "В первом контакте — дозированный доступ: глубину дают не сразу.",
  pisces: "В первом контакте — эмпатия и мягкие границы: чуткость раньше жёстких правил.",
};

function clip(text: string, max = 200): string {
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
  if (essence) {
    return essence.length > 180 ? clip(essence, 180) : essence;
  }
  if (row.claimProse && row.claimProse.trim().length >= 12) {
    return clip(row.claimProse);
  }
  if (row.detail && !/^(солнце|луна|асцендент|середина|число пути)/i.test(row.detail)) {
    return clip(`${row.detail[0]?.toUpperCase()}${row.detail.slice(1)}.`);
  }
  return clip(row.title || "Число пути — то, что выбрало имя в портрете.");
}

function meaningForInfluenced(
  row: WhyAnchorPresentation,
  ctx: {
    core?: CoreProfile | null;
    frameworkCards?: ProfileFrameworkCard[] | null;
  },
): string {
  // CE claim prose already person-facing — use it; never echo fact detail as meaning.
  if (row.claimProse && row.claimProse.trim().length >= 12) {
    return clip(row.claimProse);
  }

  const cards = ctx.frameworkCards ?? [];
  const id = row.id.toLowerCase();

  if (id.startsWith("ce_claim:")) {
    const thesis = id.slice("ce_claim:".length);
    if (thesis.includes("presence") || thesis.includes("_asc")) {
      const fromTitle = row.title.match(/в\s+(\S+?)(?:\.|$)/i)?.[1]?.replace(/[.,;:]+$/u, "") || "";
      const prepToId: Record<string, string> = {
        овне: "aries",
        тельце: "taurus",
        близнецах: "gemini",
        раке: "cancer",
        льве: "leo",
        деве: "virgo",
        весах: "libra",
        скорпионе: "scorpio",
        стрельце: "sagittarius",
        козероге: "capricorn",
        водолее: "aquarius",
        рыбах: "pisces",
      };
      const signId =
        prepToId[fromTitle.toLowerCase()] ||
        normalizeSignId(fromTitle) ||
        null;
      const bySign = signId ? ASC_CONTACT_BY_SIGN[signId] : null;
      if (bySign) return clip(bySign);
      return clip(
        "В первом контакте тебя считывают по темпу и дистанции — до знакомства с ядром.",
      );
    }
    if (thesis.includes("air_mind") || thesis.includes("direction")) {
      return clip("Ты проявляешь силу через идеи, связи и ясный обмен — не через размах.");
    }
  }

  if (id === "sun") {
    const fromCard = frameworkBody(cards, "sun");
    const sunSign = ctx.core?.astro?.sun_sign;
    const fromKnowledge = sunSign
      ? getSunInSignEntry(normalizeSignId(sunSign))?.bullets?.[0]?.trim() || null
      : null;
    return clip(
      fromCard ||
        fromKnowledge ||
        "Ты проявляешь силу и себя в мире так, как это видно окружающим без объяснений.",
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
        "Ты чувствуешь, восстанавливаешься и реагируешь изнутри — это видно рядом с тобой.",
    );
  }

  if (id === "asc" || id === "rising") {
    const fromCard = frameworkBody(cards, "rising") || frameworkBody(cards, "asc");
    const ascHow = ctx.core?.character_engine_asc_v0?.asc?.how?.trim();
    const ascValue = ctx.core?.portrait_why_v0?.portrait_influenced_by?.find((r) => r.id === "asc")
      ?.value;
    const signId = ascValue ? normalizeSignId(String(ascValue)) : null;
    const fromKnowledge = signId
      ? getRisingSignEntry(signId)?.bullets?.[0]?.trim()
      : null;
    const bySign = signId ? ASC_CONTACT_BY_SIGN[signId] : null;
    const byElement =
      signId && ["gemini", "libra", "aquarius"].includes(signId)
        ? ASC_CONTACT_BY_ELEMENT.air
        : signId && ["aries", "leo", "sagittarius"].includes(signId)
          ? ASC_CONTACT_BY_ELEMENT.fire
          : signId && ["taurus", "virgo", "capricorn"].includes(signId)
            ? ASC_CONTACT_BY_ELEMENT.earth
            : signId && ["cancer", "scorpio", "pisces"].includes(signId)
              ? ASC_CONTACT_BY_ELEMENT.water
              : null;
    // Prefer concrete contact meaning; avoid repeating the same vague ASC line twice.
    return clip(
      bySign ||
        fromKnowledge ||
        byElement ||
        fromCard ||
        ascHow ||
        "В первом контакте тебя считывают по темпу и дистанции — до знакомства с ядром.",
    );
  }

  if (id === "mc" || id === "midheaven") {
    const fromCard = frameworkBody(cards, "mc");
    const mcHow = ctx.core?.character_engine_asc_v0?.mc?.how?.trim();
    return clip(
      fromCard ||
        mcHow ||
        "Публичная роль и след результата — то, по чему тебя судят снаружи.",
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
          ? `Стихия «${row.detail}» окрашивает темперамент в портрете.`
          : "Стихия Солнца окрашивает темперамент в портрете."),
    );
  }

  if (id === "rhythm") {
    const rhythm = ctx.core?.baseline?.rhythm_style?.trim() || row.detail;
    if (rhythm) {
      return clip(`Ритм развития: ${rhythm[0]?.toLowerCase()}${rhythm.slice(1)}.`);
    }
    return "Ритм развития — как ты обычно стартуешь и держишь темп.";
  }

  if (id === "life_path") {
    return meaningForSelected(row, ctx.core);
  }

  return clip(
    row.detail && !/^(солнце|луна|асцендент|середина|число пути)/i.test(row.detail)
      ? `${row.detail[0]?.toUpperCase()}${row.detail.slice(1)}.`
      : "Это расширяет портрет рядом с именем.",
  );
}

/**
 * Present Step-2 as formation cards: selected vs influenced, each with meaning.
 */
export function buildWhyFormationCards(
  rows: ProfileJourneyWhyRow[],
  ctx: {
    core?: CoreProfile | null;
    frameworkCards?: ProfileFrameworkCard[] | null;
    recognitionLine?: string | null;
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
