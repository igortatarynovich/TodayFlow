/**
 * P0.1.3 — Today Narrative Layer: human story from machine contract.
 * Data contract (DomainLens slots) stays on API; UI renders unified daily narrative.
 */

import type { DomainLensV1, TodayContractDomainId, TodayContractV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";

export type TodayNarrativeManifestation = {
  domainId: TodayContractDomainId;
  label: string;
  line: string;
};

export type TodayNarrativeV1 = {
  version: "today_narrative_v1";
  mainThought: {
    headline: string;
    subline?: string;
  };
  growthPoint: string;
  manifestations: TodayNarrativeManifestation[];
  caution?: string;
  primaryAction: string;
};

const DOMAIN_MANIFEST_LABEL: Record<TodayContractDomainId, string> = {
  relationships: "В отношениях",
  money_work: "В работе",
  family: "Дома",
};

const DOMAIN_ORDER: TodayContractDomainId[] = ["relationships", "money_work", "family"];

const STATUS_PREFIXES = [
  "сегодня в отношениях — ",
  "сегодня в работе и деньгах — ",
  "сегодня в семье — ",
  "сегодня дома ",
  "сегодня в семье ",
];

function normSpace(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

function capitalizeFirst(text: string): string {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function stripStatusPrefix(status: string): string {
  let s = normSpace(status);
  const low = s.toLowerCase();
  for (const prefix of STATUS_PREFIXES) {
    if (low.startsWith(prefix)) {
      s = s.slice(prefix.length).trim();
      break;
    }
  }
  return capitalizeFirst(s.replace(/^[-—]\s*/, ""));
}

function stripTodayLead(text: string): string {
  return normSpace(text.replace(/^сегодня\s+[^.]{0,40}[.:]\s*/i, ""));
}

function normalizeHeadline(period: string): string {
  const t = normSpace(period);
  const liveThrough = t.match(/^проживать день через\s+(.+)$/i);
  if (liveThrough) {
    let theme = liveThrough[1].replace(/[.!?]+$/, "").trim();
    if (/и действовать|и не пытаться/i.test(theme)) {
      const beforeAnd = theme.split(/\s+и\s+/)[0]?.trim();
      if (beforeAnd) theme = beforeAnd;
    }
    if (/устойчивость\s+через\s+понятный\s+ритм/i.test(theme)) {
      return "";
    }
    const normalized = theme.charAt(0).toLowerCase() + theme.slice(1);
    return normalized.endsWith(".") ? `Сегодня ${normalized}` : `Сегодня ${normalized}.`;
  }
  if (/^день\s+/i.test(t) && !t.toLowerCase().startsWith("сегодня")) {
    return `Сегодня ${t.replace(/[.!?]+$/, "")}.`;
  }
  if (!t.toLowerCase().startsWith("сегодня")) {
    return `Сегодня ${t.replace(/[.!?]+$/, "")}.`;
  }
  return t.endsWith(".") || t.endsWith("!") || t.endsWith("?") ? t : `${t}.`;
}

export function splitPeriodNarrative(period: string): { headline: string; subline?: string } {
  const trimmed = normSpace(period);
  if (!trimmed) {
    return { headline: "Сегодня — день навигации." };
  }

  const dashParts = trimmed.split(/\s*[—–]\s+/);
  if (dashParts.length >= 2) {
    return {
      headline: normalizeHeadline(dashParts[0]),
      subline: capitalizeFirst(dashParts.slice(1).join(" ").replace(/[.!?]+$/, "")) + ".",
    };
  }

  const sentenceParts = trimmed.split(/(?<=[.!?])\s+/).filter(Boolean);
  if (sentenceParts.length >= 2) {
    return {
      headline: normalizeHeadline(sentenceParts[0]),
      subline: sentenceParts.slice(1).join(" "),
    };
  }

  return { headline: normalizeHeadline(trimmed) };
}

function pickManifestationBody(lens: DomainLensV1, domainId: TodayContractDomainId): string {
  const opportunity = stripTodayLead(lens.opportunity);
  const statusBody = stripStatusPrefix(lens.status);
  const risk = stripTodayLead(lens.risk);

  const candidates = [opportunity, statusBody, risk].map(normSpace).filter(Boolean);
  const best = candidates[0] ?? "";
  if (!best) return "";

  const label = DOMAIN_MANIFEST_LABEL[domainId].toLowerCase();
  if (best.toLowerCase().startsWith(label)) {
    return capitalizeFirst(best);
  }
  return best;
}

function formatManifestationLine(domainId: TodayContractDomainId, body: string, index: number): string {
  const label = DOMAIN_MANIFEST_LABEL[domainId];
  const clean = body.replace(/[.!?]+$/, "").trim();
  if (!clean) return "";

  const low = clean.toLowerCase();
  if (low.startsWith(label.toLowerCase())) {
    return capitalizeFirst(clean) + (clean.endsWith(".") ? "" : ".");
  }

  const connector = index === 0 ? "" : "Поэтому ";
  const line = `${connector}${label} ${clean.charAt(0).toLowerCase() + clean.slice(1)}`;
  return line.endsWith(".") ? line : `${line}.`;
}

function pickCaution(contract: TodayContractV1): string | undefined {
  const presentIds = DOMAIN_ORDER.filter((id) => isDomainLensPresent(contract.domains[id]));
  const risks = presentIds.map((id) => stripTodayLead(contract.domains[id].risk)).filter(Boolean);
  const manifestations = presentIds.map((id) => pickManifestationBody(contract.domains[id], id));
  for (const risk of risks) {
    const norm = normSpace(risk).toLowerCase();
    const duplicated = manifestations.some((m) => normSpace(m).toLowerCase().includes(norm.slice(0, 24)));
    if (!duplicated && risk.length > 12) {
      return capitalizeFirst(risk.endsWith(".") ? risk : `${risk}.`);
    }
  }
  return undefined;
}

export function buildTodayNarrativeV1(contract: TodayContractV1): TodayNarrativeV1 {
  const { headline, subline } = splitPeriodNarrative(contract.global_context.period);
  const manifestations: TodayNarrativeManifestation[] = [];

  DOMAIN_ORDER.forEach((domainId, index) => {
    if (!isDomainLensPresent(contract.domains[domainId])) return;
    const body = pickManifestationBody(contract.domains[domainId], domainId);
    if (!body) return;
    const line = formatManifestationLine(domainId, body, index);
    manifestations.push({
      domainId,
      label: DOMAIN_MANIFEST_LABEL[domainId],
      line,
    });
  });

  return {
    version: "today_narrative_v1",
    mainThought: { headline, subline },
    growthPoint: contract.personal_growth.development_point,
    manifestations,
    caution: pickCaution(contract),
    primaryAction: contract.primary_action,
  };
}
