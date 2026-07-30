/**
 * Wave 2 Phase B — VerdictStrip client (top_driver_v1).
 */

import { getJson } from "@/lib/api";

export type DomainKey = "work" | "money" | "relationships" | "energy";
export type VerdictKey = "calm" | "charged" | "friction" | "open";

export type DomainVerdict = {
  domain: DomainKey | string;
  verdict: VerdictKey | string;
  why_short: string;
  driver_ids: string[];
  logic_source: string;
  top_weight?: number | null;
};

export type DomainVerdictsResponse = {
  schema_version: string;
  local_date: string;
  day_facts_id: string;
  logic_source: string;
  domain_verdicts: DomainVerdict[];
  /** @deprecated prefer is_fallback */
  degraded?: boolean;
  is_fallback?: boolean;
};

export const DOMAIN_ORDER: DomainKey[] = ["work", "money", "relationships", "energy"];

export const DOMAIN_LABEL_RU: Record<DomainKey, string> = {
  work: "Работа",
  money: "Деньги",
  relationships: "Отношения",
  energy: "Энергия",
};

export const VERDICT_LABEL_RU: Record<VerdictKey, string> = {
  calm: "спокойно",
  charged: "заряжено",
  friction: "трение",
  open: "открыто",
};

export async function fetchDomainVerdicts(dateISO: string): Promise<DomainVerdictsResponse> {
  const q = dateISO ? `?local_date=${encodeURIComponent(dateISO)}` : "";
  return getJson<DomainVerdictsResponse>(`/today/domain-verdicts${q}`);
}

/** Order API rows by fixed domain sequence. Does **not** invent calm fillers. */
export function orderDomainVerdicts(rows: DomainVerdict[]): DomainVerdict[] {
  const byDomain = new Map(rows.map((r) => [r.domain, r]));
  const ordered: DomainVerdict[] = [];
  for (const domain of DOMAIN_ORDER) {
    const hit = byDomain.get(domain);
    if (hit) ordered.push(hit);
  }
  for (const row of rows) {
    if (!DOMAIN_ORDER.includes(row.domain as DomainKey)) ordered.push(row);
  }
  return ordered;
}

/**
 * Silent / collapsed bank: four domains with identical why_short.
 * Covers empty-driver calm poison and aspect-class formula collapse
 * (e.g. 4× «открыто / Есть опора»). FE must not present as day meaning.
 */
export function isSilentCalmBank(rows: DomainVerdict[] | null | undefined): boolean {
  if (!rows || rows.length < 4) return false;
  const ordered = orderDomainVerdicts(rows);
  if (ordered.length < 4) return false;
  const whys = ordered.map((r) => (r.why_short || "").trim().toLowerCase());
  const first = whys[0];
  if (!first) return whys.every((w) => !w);
  return whys.every((w) => w === first);
}
