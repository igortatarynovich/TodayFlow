import { HOUSE_FALLBACK, HOUSE_LAYER } from "@/components/profile/profileHouseConstants";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { ProfileFrameworkCard } from "@/lib/profilePage/buildProfileQuickMapData";
import type { CoreProfile } from "@/lib/types";
import {
  getLifePathEntry,
  getMoonInSignEntry,
  getRisingSignEntry,
  getSunInSignEntry,
  normalizeSignId,
  zodiacRuName,
} from "@/lib/zodiacKnowledge";

export type EssenceFoundationCard = {
  id: string;
  label: string;
  /** RU fact line, e.g. «Водолей · 8 дом». */
  fact: string;
  /** One person-facing sentence — what it means for them. */
  meaning: string;
};

const PERSONAL_YEAR_MEANING: Record<number, string> = {
  1: "Год запуска: меньше ждать разрешения — больше своего первого шага.",
  2: "Год союза и тонкой настройки: сила в паре и в паузе, не в гонке.",
  3: "Год голоса и контакта: важнее сказать и показать, чем держать внутри.",
  4: "Год фундамента: режим, границы и опора важнее яркого рывка.",
  5: "Год свободы и смены: полезны эксперимент и выход из привычной клетки.",
  6: "Год заботы и обязательств: близкие и дом просят явного участия.",
  7: "Год смысла и дистанции: меньше шума снаружи — больше ясности «зачем».",
  8: "Год силы и результата: видимый вклад и честные амбиции окупаются.",
  9: "Год завершения циклов: отпустить старое, чтобы освободить место новому.",
};

function clipSentence(text: string, max = 160): string {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= max) return clean;
  const cut = clean.slice(0, max - 1);
  const at = Math.max(cut.lastIndexOf(". "), cut.lastIndexOf("; "), cut.lastIndexOf(", "));
  if (at > 60) return `${cut.slice(0, at + 1).trim()}`;
  return `${cut.trim()}…`;
}

function cardBody(cards: ProfileFrameworkCard[] | undefined, id: string): string | null {
  const body = cards?.find((c) => c.id === id)?.body?.trim();
  return body || null;
}

function houseZoneLine(house: number | null | undefined): string | null {
  if (house == null || house < 1 || house > 12) return null;
  const title = HOUSE_LAYER[house]?.title?.trim();
  const fallback = HOUSE_FALLBACK[house]?.trim();
  if (title && fallback) return `${title}: ${fallback}`;
  return title || fallback || null;
}

function factWithHouse(signRu: string, house: number | null | undefined): string {
  if (house != null && house >= 1 && house <= 12) return `${signRu} · ${house} дом`;
  return signRu;
}

function personalYearFromBirth(birthDate: string | null | undefined, refYear: number): number | null {
  if (!birthDate || typeof birthDate !== "string") return null;
  const m = birthDate.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return null;
  const month = Number(m[2]);
  const day = Number(m[3]);
  if (!month || !day) return null;
  let x = Math.abs(Math.trunc(month + day + refYear));
  while (x > 9) {
    x = String(x)
      .split("")
      .reduce((acc, d) => acc + Number(d), 0);
  }
  return x === 0 ? 1 : x;
}

/**
 * Birth pillars for Profile step «Твоя суть»: RU facts + one useful meaning each.
 * Prefer CE/framework prose; never leave English sign dumps without explanation.
 */
export function buildEssenceFoundationCards(input: {
  natalPreview?: NatalChartPreview | null;
  numerology?: CoreProfile["numerology"] | null;
  frameworkCards?: ProfileFrameworkCard[] | null;
  refYear?: number;
}): EssenceFoundationCard[] {
  const natal = input.natalPreview ?? null;
  const cards = input.frameworkCards ?? [];
  const num = input.numerology ?? null;
  const refYear = input.refYear ?? new Date().getFullYear();
  const out: EssenceFoundationCard[] = [];

  const sun = natal?.positions?.sun;
  if (sun?.sign) {
    const signId = normalizeSignId(sun.sign);
    const signRu = zodiacRuName(sun.sign);
    const house = typeof sun.house === "number" ? sun.house : null;
    const fromCard = cardBody(cards, "sun");
    const fromKnowledge = getSunInSignEntry(signId)?.bullets?.[0]?.trim() || null;
    const zone = houseZoneLine(house);
    const meaning =
      fromCard ||
      fromKnowledge ||
      (zone
        ? `Солнце — как ты проявляешь силу. ${zone}`
        : "Солнце показывает, как ты проявляешь себя в мире.");
    out.push({
      id: "sun",
      label: "Солнце",
      fact: factWithHouse(signRu, house),
      meaning: clipSentence(meaning),
    });
  }

  const moon = natal?.positions?.moon;
  if (moon?.sign) {
    const signId = normalizeSignId(moon.sign);
    const signRu = zodiacRuName(moon.sign);
    const house = typeof moon.house === "number" ? moon.house : null;
    const fromCard = cardBody(cards, "moon");
    const fromKnowledge = getMoonInSignEntry(signId)?.bullets?.[0]?.trim() || null;
    const zone = houseZoneLine(house);
    const meaning =
      fromCard ||
      fromKnowledge ||
      (zone
        ? `Луна — как ты чувствуешь и восстанавливаешься. ${zone}`
        : "Луна описывает, как ты чувствуешь и восстанавливаешься.");
    out.push({
      id: "moon",
      label: "Луна",
      fact: factWithHouse(signRu, house),
      meaning: clipSentence(meaning),
    });
  }

  const timeUnknown =
    Boolean(natal?.time_unknown) ||
    natal?.mode === "unknown_time" ||
    natal?.ascendant_precision === "unavailable";
  const ascSign = natal?.ascendant?.sign || natal?.houses?.[0]?.sign || null;
  if (ascSign && !timeUnknown) {
    const signId = normalizeSignId(ascSign);
    const signRu = zodiacRuName(ascSign);
    const fromCard = cardBody(cards, "rising") || cardBody(cards, "asc");
    const fromKnowledge = getRisingSignEntry(signId)?.bullets?.[0]?.trim() || null;
    out.push({
      id: "asc",
      label: "Асцендент",
      fact: signRu,
      meaning: clipSentence(
        fromCard ||
          fromKnowledge ||
          "Асцендент — первый контакт: как тебя считывают до слов.",
      ),
    });
  }

  const mcSign = natal?.positions?.mc?.sign || natal?.houses?.[9]?.sign || null;
  if (mcSign && !timeUnknown) {
    const signRu = zodiacRuName(mcSign);
    const fromCard = cardBody(cards, "mc");
    out.push({
      id: "mc",
      label: "MC",
      fact: signRu,
      meaning: clipSentence(
        fromCard ||
          "MC — публичная роль: по какому следу тебя судят о результате.",
      ),
    });
  }

  if (num?.life_path != null) {
    const entry = getLifePathEntry(num.life_path);
    const fromCard = cardBody(cards, "life_path");
    const meaning =
      fromCard ||
      entry?.essence?.trim() ||
      entry?.driver?.trim() ||
      "Число пути задаёт долгий ритм развития и главную тему жизни.";
    const master = num.is_master_life_path ? " · мастер-линия" : "";
    out.push({
      id: "life_path",
      label: "Число пути",
      fact: `${num.life_path}${master}`,
      meaning: clipSentence(meaning),
    });
  }

  const py = personalYearFromBirth(num?.birth_date, refYear);
  if (py != null) {
    out.push({
      id: "personal_year",
      label: "Личный год",
      fact: `${py} · ${refYear}`,
      meaning: clipSentence(
        PERSONAL_YEAR_MEANING[py] ||
          `Личный год ${py}: тон этого календарного цикла поверх числа пути.`,
      ),
    });
  }

  return out;
}
