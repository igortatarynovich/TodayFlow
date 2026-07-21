/** RU user-facing filter — hide raw EN engine / metadata leaks in Today synthesis. */

import type { TodayContractV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import { buildTodayNarrativeV1, splitPeriodNarrative } from "@/lib/todayNarrativeFromContract";
import {
  dayStoryHeadline,
  hasAuthoritativeDayStory,
} from "@/lib/todayContractMapper";

export function countScriptChars(text: string): { cyrillic: number; latin: number } {
  const cyrillic = (text.match(/[а-яё]/gi) || []).length;
  const latin = (text.match(/[a-z]/gi) || []).length;
  return { cyrillic, latin };
}

export function isRuUserFacingText(text: string | null | undefined): boolean {
  const t = (text || "").trim();
  if (!t || t.length < 6) return false;
  const { cyrillic, latin } = countScriptChars(t);
  if (latin > 10 && latin > cyrillic) return false;
  if (/avoiding the inevitable|suppressed emotion|prolonged instability/i.test(t)) return false;
  return cyrillic >= 6;
}

export function isGenericRhythmCliche(text: string): boolean {
  const low = text.toLowerCase().trim();
  if (!low) return false;
  return (
    /устойчивость\s+через\s+понятный\s+ритм/.test(low) ||
    /^проживать день через/.test(low) ||
    /сегодня день устойчивость/.test(low)
  );
}

export function isBrokenDayHeadline(text: string): boolean {
  const low = text.toLowerCase().trim();
  if (!low) return true;
  if (isGenericRhythmCliche(text)) return true;
  if (/сегодня день \w+ость /.test(low) && !/сегодня день устойчивости/.test(low)) return true;
  if (/сегодня день .+ через /.test(low)) return true;
  if (/и действовать/.test(low) && !/лучше/.test(low)) return true;
  if (low.split(/\s+/).length > 16) return true;
  if (!/[.!?]$/.test(low) && low.length > 72) return true;
  return false;
}

function capitalizeFirst(text: string): string {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function pickDomainHeadline(contract: TodayContractV1): string | null {
  for (const id of ["money_work", "relationships", "family"] as const) {
    const domain = contract.domains[id];
    if (!isDomainLensPresent(domain)) continue;
    const opp = domain.opportunity?.trim();
    if (!opp || opp.length < 18 || !isRuUserFacingText(opp)) continue;
    const clean = opp.replace(/^сегодня\s+/i, "").replace(/[.!?]+$/, "").trim();
    if (!clean) continue;
    return `${capitalizeFirst(clean)}.`;
  }
  return null;
}

export function resolveTodayThemeHeadline(contract: TodayContractV1): string {
  if (hasAuthoritativeDayStory(contract)) {
    const fromStory = dayStoryHeadline(contract);
    if (fromStory && isRuUserFacingText(fromStory) && !isBrokenDayHeadline(fromStory)) {
      return fromStory.endsWith(".") ? fromStory : `${fromStory}.`;
    }
  }

  const period = contract.global_context.period;
  const growthPoint = contract.personal_growth.development_point;
  const split = splitPeriodNarrative(period);
  let headline = split.headline.trim();

  if (
    !headline ||
    isBrokenDayHeadline(headline) ||
    isGenericRhythmCliche(headline) ||
    isGenericRhythmCliche(period)
  ) {
    headline = polishDayHeadline(period, growthPoint);
  }

  if (isBrokenDayHeadline(headline) || isGenericRhythmCliche(headline)) {
    headline = pickDomainHeadline(contract) ?? headline;
  }

  if (isBrokenDayHeadline(headline) || isGenericRhythmCliche(headline)) {
    const action = contract.primary_action?.trim();
    if (action && isRuUserFacingText(action) && action.length < 120) {
      return action.endsWith(".") ? action : `${action}.`;
    }
  }

  return headline;
}

export function extractThemeShort(contract: TodayContractV1, headline: string): string {
  const direction = contract.day_story?.direction?.trim();
  if (direction && isRuUserFacingText(direction) && direction.length <= 72) {
    return capitalizeFirst(direction.replace(/[.!?]+$/, ""));
  }

  const period = contract.global_context.period.trim();
  const dash = period.split(/\s*[—–]\s+/);
  if (dash.length >= 2) {
    const short = dash.slice(1).join(" ").replace(/[.!?]+$/, "").trim();
    if (short && isRuUserFacingText(short) && short.length <= 72) {
      return capitalizeFirst(short);
    }
  }
  const trimmed = headline
    .replace(/^Сегодня[:\s—-]*/i, "")
    .replace(/[.!?]+$/, "")
    .trim();
  if (trimmed.length <= 56 && isRuUserFacingText(trimmed)) {
    return capitalizeFirst(trimmed);
  }
  const corpus = `${period} ${headline}`.toLowerCase();
  if (/ритм|устойчив/.test(corpus)) return "Спокойный ритм и устойчивость";
  if (/ясност|наблюд/.test(corpus)) return "Ясность и внимательность";
  return "Главная линия дня";
}

export function buildCentralDayThought(contract: TodayContractV1): string {
  const headline = resolveTodayThemeHeadline(contract).replace(/[.!?]+$/, "").trim();
  const growth = contract.personal_growth.development_point?.trim() ?? "";
  const narrative = buildTodayNarrativeV1(contract);

  let second: string | null = null;
  if (growth && isRuUserFacingText(growth)) {
    for (const sentence of growth.split(/(?<=[.!?])\s+/)) {
      const t = sentence.trim();
      if (!t || headline.toLowerCase().includes(t.toLowerCase().slice(0, 20))) continue;
      second = t.endsWith(".") ? t : `${t}.`;
      break;
    }
  }
  if (!second) {
    const subline = narrative.mainThought.subline?.trim();
    if (subline && isRuUserFacingText(subline) && !headline.toLowerCase().includes(subline.toLowerCase().slice(0, 20))) {
      second = subline.endsWith(".") ? subline : `${subline}.`;
    }
  }
  if (!second) {
    if (/ритм|устойчив|ровн|спеш/i.test(headline)) {
      second = "Самые сильные решения придут тогда, когда ты перестанешь их торопить.";
    } else if (/ясност|наблюд/i.test(headline)) {
      second = "День помогает замечать детали, которые раньше оставались незаметными.";
    } else {
      second = "День поддерживает те шаги, которые можно сделать спокойно и честно.";
    }
  }

  return `${headline}. ${second}`;
}

export function sanitizeRuCopy(text: string | null | undefined, fallback: string): string {
  const t = text?.trim();
  if (t && isRuUserFacingText(t)) return t;
  return fallback;
}

export function reframeAsHelpful(action: string | undefined, risk: string | undefined): string | null {
  const act = action?.replace(/^сегодня\s+/i, "").replace(/[.!?]+$/, "").trim();
  if (act && isRuUserFacingText(act) && act.length >= 10) {
    const lower = act.charAt(0).toLowerCase() + act.slice(1);
    return lower.endsWith(";") ? lower : `${lower};`;
  }
  if (!risk) return null;
  const r = risk.toLowerCase();
  if (/молч|дистанц/.test(r)) return "говорить прямо, если что-то волнует;";
  if (/конфликт|спор|резк/.test(r)) return "сначала уточнить детали, а потом принимать решение;";
  if (/импuls|спеш|тороп|сроч/.test(r)) return "оставлять место для паузы перед важным выбором;";
  if (/распыл|разброс|хаос/.test(r)) return "держать один вектор до конца;";
  if (/перегруз|устал|выгор/.test(r)) return "беречь ресурс и не требовать от себя лишнего;";
  if (/покуп|трат/.test(r)) return "сделать паузу перед импulsive решением;";
  if (/вывод|осуж/.test(r)) return "проверить факты, прежде чем делать вывод;";
  const cleaned = risk.replace(/^сегодня\s+не\s+/i, "").replace(/^не\s+/i, "").replace(/[.!?]+$/, "").trim();
  if (cleaned && isRuUserFacingText(cleaned)) {
    return `${cleaned.charAt(0).toLowerCase() + cleaned.slice(1)};`;
  }
  return null;
}

export function polishDayHeadline(period: string, growthPoint: string): string {
  const low = period.toLowerCase();
  if (/устойчив|ритм|ровн/.test(low)) {
    return "Сегодня лучше держаться понятного ритма и не пытаться успеть всё сразу.";
  }
  if (/последователь|заверш/.test(low)) {
    return "Сегодня спокойная последовательность даст больше результата, чем спешка.";
  }
  if (/ясност|наблюд/.test(low)) {
    return "Сегодня не нужно ускорять события — важнее двигаться ровно и последовательно.";
  }
  const growth = growthPoint.trim();
  if (growth.toLowerCase().startsWith("сегодня") && growth.length < 140) {
    const first = growth.split(/(?<=[.!?])\s+/)[0]?.trim();
    if (first && isRuUserFacingText(first)) return first.endsWith(".") ? first : `${first}.`;
  }
  return "Сегодня важнее ровный темп, чем попытка закрыть всё одним рывком.";
}
