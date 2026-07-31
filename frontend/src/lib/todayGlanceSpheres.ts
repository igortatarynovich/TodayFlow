/**
 * Glance Screen 0 — domain strip compression.
 * Data SoT remains Wave2 fixed-4 `domain_verdicts`; this is presentation only:
 * collapse majority same-verdict into one line; full card only for outliers.
 * Algorithm is N-domain ready if the contract later expands past 4.
 */

import {
  DOMAIN_LABEL_RU,
  VERDICT_LABEL_RU,
  type DomainKey,
  type DomainVerdict,
  type VerdictKey,
} from "@/lib/todayDomainVerdicts";

export type GlanceSphereCard = {
  kind: "card";
  row: DomainVerdict;
};

export type GlanceSphereCompact = {
  kind: "compact";
  verdict: VerdictKey;
  domains: DomainKey[];
  /** True when every row shares this verdict. */
  allSame: boolean;
  label: string;
};

export type GlanceSphereBlock = GlanceSphereCard | GlanceSphereCompact;

const UNANIMOUS_COPY: Record<VerdictKey, string> = {
  open: "День ровный по всем направлениям — ничего не требует особого внимания",
  calm: "Тихий фон по всем сферам — без острого сигнала",
  charged: "День заряжен по всем направлениям — держи один фокус",
  friction: "Трение по всем сферам — короче шаг везде",
};

const MAJORITY_MIN = 3;

function domainLabel(domain: string): string {
  return DOMAIN_LABEL_RU[domain as DomainKey] ?? domain;
}

function verdictLabel(verdict: string): string {
  return VERDICT_LABEL_RU[verdict as VerdictKey] ?? verdict;
}

function compactLabel(domains: DomainKey[], verdict: VerdictKey, allSame: boolean): string {
  if (allSame) {
    return UNANIMOUS_COPY[verdict] ?? `${domains.map(domainLabel).join(" · ")} — ${verdictLabel(verdict)}`;
  }
  return `${domains.map(domainLabel).join(" · ")} — ${verdictLabel(verdict)}`;
}

/**
 * Compress domain_verdicts for Glance:
 * - 3+ same verdict → one compact line for that group
 * - all same → single unanimous line (no cards)
 * - outliers (size < 3 when a majority exists) → full cards
 * - no majority of 3+ → keep full cards (mixed day)
 */
export function compressGlanceDomainVerdicts(rows: DomainVerdict[]): GlanceSphereBlock[] {
  if (rows.length === 0) return [];

  const byVerdict = new Map<VerdictKey, DomainVerdict[]>();
  for (const row of rows) {
    const v = row.verdict as VerdictKey;
    const list = byVerdict.get(v) ?? [];
    list.push(row);
    byVerdict.set(v, list);
  }

  const groups = Array.from(byVerdict.entries()).map(([verdict, items]) => ({
    verdict,
    items,
    domains: items.map((r) => r.domain as DomainKey),
  }));

  const hasMajority = groups.some((g) => g.items.length >= MAJORITY_MIN);
  if (!hasMajority) {
    return rows.map((row) => ({ kind: "card" as const, row }));
  }

  const blocks: GlanceSphereBlock[] = [];
  const domainOrder = rows.map((r) => r.domain);
  groups.sort((a, b) => b.items.length - a.items.length);

  for (const g of groups) {
    if (g.items.length >= MAJORITY_MIN) {
      const allSame = g.items.length === rows.length;
      blocks.push({
        kind: "compact",
        verdict: g.verdict,
        domains: g.domains,
        allSame,
        label: compactLabel(g.domains, g.verdict, allSame),
      });
    }
  }

  for (const domain of domainOrder) {
    const row = rows.find((r) => r.domain === domain);
    if (!row) continue;
    const g = groups.find((x) => x.verdict === (row.verdict as VerdictKey));
    if (g && g.items.length < MAJORITY_MIN) {
      blocks.push({ kind: "card", row });
    }
  }

  return blocks;
}
