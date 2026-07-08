import type { OnboardingRecognitionLens } from "@/lib/interpretation/onboardingRecognitionTypes";
import { polishRussianCopy } from "@/lib/interpretation/polishRussianCopy";

export function normText(text: string): string {
  return text.replace(/\s+/g, " ").trim().toLowerCase();
}

export function ensurePeriod(text: string): string {
  const t = text.trim();
  if (!t) return t;
  return /[.!?…]$/.test(t) ? t : `${t}.`;
}

export function capitalizeFirst(text: string): string {
  const t = text.trim();
  if (!t) return t;
  return t.charAt(0).toUpperCase() + t.slice(1);
}

function startsSecondPerson(text: string): boolean {
  return /^(ты|тебе|твой|твоя|твои)([\s,—-]|$)/i.test(text.trim());
}

function stripLeadingTy(text: string): string {
  return text.trim().replace(/^ты[\s,—-]+/i, "");
}

export function signNarrativeToYou(text: string, ruSignName?: string): string {
  const t = text.trim();
  if (ruSignName && t.toLowerCase().startsWith(ruSignName.toLowerCase())) {
    const rest = t.slice(ruSignName.length).trim();
    const growthMatch = rest.match(/^раст[ёe]?[^\s,]*,?\s*(.*)$/i);
    if (growthMatch) {
      const tail = growthMatch[1]?.trim();
      return capitalizeFirst(tail ? `Ты растёшь, когда ${tail.charAt(0).toLowerCase()}${tail.slice(1)}` : "Ты растёшь");
    }
    return capitalizeFirst(`Ты ${rest.charAt(0).toLowerCase()}${rest.slice(1)}`);
  }
  return toSecondPerson(t);
}

export function toSecondPerson(text: string): string {
  const t = text.trim();
  if (startsSecondPerson(t)) return capitalizeFirst(t);
  if (/^Принимает/i.test(t)) return capitalizeFirst(`Ты принимаешь${t.slice(9)}`);
  if (/^Силен\b/.test(t)) return `Ты силён${t.slice(5)}`;
  if (/^Сильны\b/.test(t)) return `Ты силён${t.slice(6)}`;
  if (/^Сильна\b/.test(t)) return `Ты сильна${t.slice(6)}`;
  if (/^Слабеет\b/i.test(t)) return capitalizeFirst(`Ты слабеешь${t.slice(7)}`);
  if (/^Слабеют\b/.test(t)) return `Тебе тяжело${t.slice(7)}`;
  if (/^Слаба\b/.test(t)) return `Тебе тяжело${t.slice(5)}`;
  if (/^Ориентирован\b/.test(t)) return `Ты ориентирован${t.slice(11)}`;
  return capitalizeFirst(`Ты ${t.charAt(0).toLowerCase()}${t.slice(1)}`);
}

export function splitSentences(text: string): string[] {
  return text
    .split(/(?<=[.!?…])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function lowerFirstClause(text: string): string {
  const t = text.trim().replace(/[.!?…]+$/, "");
  if (!t) return t;
  return t.charAt(0).toLowerCase() + t.slice(1);
}

export function frameForLens(lens: OnboardingRecognitionLens, raw: string): string {
  const t = raw.trim();

  switch (lens) {
    case "strengthens":
      if (/^ты лучше/i.test(t)) return ensurePeriod(capitalizeFirst(t));
      if (/^ты сильн/i.test(t)) return ensurePeriod(capitalizeFirst(t));
      return ensurePeriod(toSecondPerson(t));
    case "tension":
      if (/^сложнее всего/i.test(t)) return ensurePeriod(capitalizeFirst(t));
      if (/^напряжение/i.test(t)) return ensurePeriod(capitalizeFirst(t));
      if (/^быть /i.test(t)) return ensurePeriod(`Сложнее всего бывает, когда ${lowerFirstClause(t)}`);
      return ensurePeriod(`Сложнее всего бывает, когда ${lowerFirstClause(toSecondPerson(t))}`);
    case "noticed_by_others":
      return ensurePeriod(toSecondPerson(t));
    case "recovery":
      if (/^ты раст/i.test(t)) {
        return polishRussianCopy(ensurePeriod(capitalizeFirst(t)));
      }
      if (startsSecondPerson(t) && /раст/i.test(t)) {
        return polishRussianCopy(ensurePeriod(capitalizeFirst(t)));
      }
      if (startsSecondPerson(t)) {
        return polishRussianCopy(
          ensurePeriod(`Быстрее восстанавливаешься, когда ${lowerFirstClause(stripLeadingTy(t))}`),
        );
      }
      return polishRussianCopy(ensurePeriod(`Тебе помогает помнить: ${lowerFirstClause(t)}`));
    case "today_focus":
      if (/^сегодня/i.test(t)) return ensurePeriod(capitalizeFirst(t));
      if (/^(твоя|твой|твои)\b/i.test(t)) {
        return ensurePeriod(`Сегодня особенно полезно помнить: ${lowerFirstClause(t)}`);
      }
      if (startsSecondPerson(t)) {
        return ensurePeriod(`Сегодня особенно полезно помнить: ${lowerFirstClause(stripLeadingTy(t))}`);
      }
      return ensurePeriod(`Сегодня особенно полезно ${lowerFirstClause(t)}`);
    default:
      return ensurePeriod(t);
  }
}

export function tokenSet(text: string): Set<string> {
  return new Set(
    normText(text)
      .replace(/[^\p{L}\p{N}\s]/gu, " ")
      .split(/\s+/)
      .map((w) => w.trim())
      .filter((w) => w.length > 2),
  );
}

export function textSimilarity(a: string, b: string): number {
  const ta = tokenSet(a);
  const tb = tokenSet(b);
  if (ta.size === 0 || tb.size === 0) return 0;
  let overlap = 0;
  ta.forEach((token) => {
    if (tb.has(token)) overlap += 1;
  });
  return overlap / Math.max(ta.size, tb.size);
}
