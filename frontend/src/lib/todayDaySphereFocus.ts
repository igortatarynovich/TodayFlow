/** Pick 2–3 sphere highlights: peak + caution; rest neutral. */

import type { TodayContractV1, TodayContractDomainId } from "@/lib/todayContract";
import { isRuUserFacingText } from "@/lib/todaySynthesisTextPolicy";

export type TodaySphereFocusCard = {
  id: string;
  sphere: string;
  role: "peak" | "caution";
  headline: string;
  body: string;
  releaseLine?: string;
};

export type TodaySphereFocus = {
  cards: TodaySphereFocusCard[];
  neutralNote: string;
};

const DOMAIN_ORDER: TodayContractDomainId[] = ["money_work", "relationships", "family"];

const SPHERE_LABEL: Record<TodayContractDomainId, string> = {
  money_work: "Работа и деньги",
  relationships: "Отношения",
  family: "Дом и семья",
};

const PEAK_HEADLINE: Record<TodayContractDomainId, string> = {
  money_work: "Сегодня сильнее всего — дела и ресурсы",
  relationships: "Сегодня сильнее всего — общение",
  family: "Сегодня сильнее всего — дом и близкие",
};

const CAUTION_HEADLINE: Record<TodayContractDomainId, string> = {
  money_work: "Сегодня лучше отпустить — давление в работе",
  relationships: "Сегодня лучше отпустить — острые разговоры",
  family: "Сегодня лучше отпустить — перегруз дома",
};

function stripTodayLead(text: string): string {
  return text.replace(/^сегодня\s+[^.]{0,40}[.:]\s*/i, "").replace(/[.!?]+$/, "").trim();
}

function scoreOpportunity(text: string): number {
  const t = stripTodayLead(text).toLowerCase();
  if (!t || !isRuUserFacingText(t)) return 0;
  let score = Math.min(t.length, 80);
  if (/ясност|план|разговор|спокойн|поддерж|возможност|закры|заверш/i.test(t)) score += 24;
  return score;
}

function scoreRisk(text: string): number {
  const t = stripTodayLead(text).toLowerCase();
  if (!t || !isRuUserFacingText(t)) return 0;
  let score = Math.min(t.length, 80);
  if (/конфликт|спеш|импульс|перегруз|риск|давлен|срыв|контрол|тревог/i.test(t)) score += 28;
  return score;
}

function capitalizeFirst(text: string): string {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function buildPeakBody(id: TodayContractDomainId, domain: TodayContractV1["domains"][TodayContractDomainId]): string {
  const opp = stripTodayLead(domain.opportunity ?? "");
  if (opp && isRuUserFacingText(opp)) {
    return `Опирайся на это: ${opp.charAt(0).toLowerCase() + opp.slice(1)}. Не распыляйся — один шаг здесь даст больше, чем три в других темах.`;
  }
  switch (id) {
    case "money_work":
      return "Хороший день для одного конкретного результата в делах — без попытки закрыть всё сразу.";
    case "relationships":
      return "Разговоры и договорённости сегодня дают отдачу — если говорить спокойно и по сути.";
    default:
      return "Домашний ритм поддерживает — короткий честный контакт лучше длинной драмы.";
  }
}

function buildCautionBody(id: TodayContractDomainId, domain: TodayContractV1["domains"][TodayContractDomainId]): string {
  const risk = stripTodayLead(domain.risk ?? "");
  if (risk && isRuUserFacingText(risk)) {
    return `Зона риска: ${risk.charAt(0).toLowerCase() + risk.slice(1)}.`;
  }
  return "Лишнее давление и попытка контролировать всё сразу сегодня не помогут.";
}

function buildReleaseLine(id: TodayContractDomainId, domain: TodayContractV1["domains"][TodayContractDomainId]): string {
  const risk = stripTodayLead(domain.risk ?? "").toLowerCase();
  if (/спеш|импульс/i.test(risk)) return "Сегодня лучше не форсировать и не принимать решений на эмоциях.";
  if (/конфликт/i.test(risk)) return "Сегодня лучше не выяснять отношения «до победного» — отложи острый разговор, если можно.";
  if (/перегруз/i.test(risk)) return "Сегодня лучше не брать на себя лишнее дома — минимум обязательств.";
  switch (id) {
    case "money_work":
      return "Сегодня лучше не раздувать список задач и не обещать сроки «на эмоциях».";
    case "relationships":
      return "Сегодня лучше не требовать ответа немедленно — дай разговору воздух.";
    default:
      return "Сегодня лучше не тащить на себе всё семейное — выбери одну маленькую заботу.";
  }
}

export function buildTodaySphereFocus(contract: TodayContractV1): TodaySphereFocus {
  const ranked = DOMAIN_ORDER.map((id) => {
    const domain = contract.domains[id];
    return {
      id,
      oppScore: scoreOpportunity(domain.opportunity ?? ""),
      riskScore: scoreRisk(domain.risk ?? ""),
    };
  });

  const peakId = [...ranked].sort((a, b) => b.oppScore - a.oppScore)[0]?.id ?? "money_work";
  const cautionCandidates = ranked.filter((r) => r.id !== peakId).sort((a, b) => b.riskScore - a.riskScore);
  let cautionId: TodayContractDomainId | null = cautionCandidates[0]?.id ?? null;
  if (cautionId && (cautionCandidates[0]?.riskScore ?? 0) < 12) {
    cautionId = null;
  }

  const cards: TodaySphereFocusCard[] = [];

  cards.push({
    id: `peak-${peakId}`,
    sphere: SPHERE_LABEL[peakId],
    role: "peak",
    headline: PEAK_HEADLINE[peakId],
    body: buildPeakBody(peakId, contract.domains[peakId]),
  });

  if (cautionId) {
    cards.push({
      id: `caution-${cautionId}`,
      sphere: SPHERE_LABEL[cautionId],
      role: "caution",
      headline: CAUTION_HEADLINE[cautionId],
      body: capitalizeFirst(buildCautionBody(cautionId, contract.domains[cautionId])),
      releaseLine: buildReleaseLine(cautionId, contract.domains[cautionId]),
    });
  }

  const peakScore = ranked.find((r) => r.id === peakId)?.oppScore ?? 0;
  const secondPeak = ranked
    .filter((r) => r.id !== peakId && r.id !== cautionId && r.oppScore >= 20)
    .sort((a, b) => b.oppScore - a.oppScore)[0];

  if (secondPeak && cards.length < 3 && secondPeak.oppScore >= peakScore * 0.75) {
    const id = secondPeak.id;
    cards.push({
      id: `peak2-${id}`,
      sphere: SPHERE_LABEL[id],
      role: "peak",
      headline: `Также поддержано — ${SPHERE_LABEL[id].toLowerCase()}`,
      body: buildPeakBody(id, contract.domains[id]),
    });
  }

  return {
    cards: cards.slice(0, 3),
    neutralNote: "Остальные сферы сегодня скорее нейтральны — не требуют отдельного внимания.",
  };
}
