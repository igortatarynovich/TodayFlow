/** Soft sphere accents from contract prose — no checklist wrappers. */

import type { TodayContractV1, TodayContractDomainId } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
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
  /** Empty when we should not announce “neutral spheres”. */
  neutralNote: string;
};

const DOMAIN_ORDER: TodayContractDomainId[] = ["money_work", "relationships", "family"];

const SPHERE_LABEL: Record<TodayContractDomainId, string> = {
  money_work: "Работа и деньги",
  relationships: "Отношения",
  family: "Дом и семья",
};

function stripTodayLead(text: string): string {
  return text.replace(/^сегодня\s+[^.]{0,40}[.:]\s*/i, "").replace(/[.!?]+$/, "").trim();
}

function capitalizeFirst(text: string): string {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function scoreOpportunity(text: string): number {
  const t = stripTodayLead(text).toLowerCase();
  if (!t || !isRuUserFacingText(t)) return 0;
  let score = Math.min(t.length, 80);
  if (/ясност|план|разговор|спокойн|поддерж|возможност|закры|заверш|сообщен|жест/i.test(t)) score += 24;
  return score;
}

function scoreRisk(text: string): number {
  const t = stripTodayLead(text).toLowerCase();
  if (!t || !isRuUserFacingText(t)) return 0;
  let score = Math.min(t.length, 80);
  if (/конфликт|спеш|импульс|перегруз|риск|давлен|срыв|контрол|тревог/i.test(t)) score += 28;
  return score;
}

/** Use contract prose as-is — never wrap with «Опирайся / Сегодня сильнее / Зона риска». */
function proseOrEmpty(text: string | null | undefined): string {
  const cleaned = stripTodayLead(text ?? "");
  if (!cleaned || !isRuUserFacingText(cleaned)) return "";
  return capitalizeFirst(cleaned);
}

export function buildTodaySphereFocus(contract: TodayContractV1): TodaySphereFocus {
  const ranked = DOMAIN_ORDER.map((id) => {
    const domain = contract.domains[id];
    if (!isDomainLensPresent(domain)) {
      return { id, oppScore: -1, riskScore: -1, present: false as const };
    }
    return {
      id,
      oppScore: scoreOpportunity(domain.opportunity ?? ""),
      riskScore: scoreRisk(domain.risk ?? ""),
      present: true as const,
    };
  }).filter((r) => r.present);

  if (!ranked.length) {
    return { cards: [], neutralNote: "" };
  }

  const peakId = [...ranked].sort((a, b) => b.oppScore - a.oppScore)[0]?.id ?? ranked[0].id;
  const cautionCandidates = ranked.filter((r) => r.id !== peakId).sort((a, b) => b.riskScore - a.riskScore);
  let cautionId: TodayContractDomainId | null = cautionCandidates[0]?.id ?? null;
  if (cautionId && (cautionCandidates[0]?.riskScore ?? 0) < 12) {
    cautionId = null;
  }

  const cards: TodaySphereFocusCard[] = [];
  const peakBody = proseOrEmpty(contract.domains[peakId].opportunity);
  if (peakBody) {
    cards.push({
      id: `peak-${peakId}`,
      sphere: SPHERE_LABEL[peakId],
      role: "peak",
      headline: SPHERE_LABEL[peakId],
      body: peakBody,
    });
  }

  if (cautionId) {
    const cautionBody = proseOrEmpty(contract.domains[cautionId].risk);
    const release = proseOrEmpty(contract.domains[cautionId].action);
    if (cautionBody || release) {
      cards.push({
        id: `caution-${cautionId}`,
        sphere: SPHERE_LABEL[cautionId],
        role: "caution",
        headline: SPHERE_LABEL[cautionId],
        body: cautionBody || release,
        releaseLine: cautionBody && release && release !== cautionBody ? release : undefined,
      });
    }
  }

  return {
    cards: cards.slice(0, 2),
    // Do not announce “other spheres are neutral” — that is product chrome, not voice.
    neutralNote: "",
  };
}
