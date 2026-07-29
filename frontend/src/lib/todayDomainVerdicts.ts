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
  degraded?: boolean;
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

export function orderDomainVerdicts(rows: DomainVerdict[]): DomainVerdict[] {
  const byDomain = new Map(rows.map((r) => [r.domain, r]));
  return DOMAIN_ORDER.map((domain) => {
    const hit = byDomain.get(domain);
    return (
      hit ?? {
        domain,
        verdict: "calm",
        why_short: "",
        driver_ids: [],
        logic_source: "top_driver_v1",
      }
    );
  });
}
