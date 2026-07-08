import { PROFILE_INSIGHT_BUDGET, type ProfileInsightLayer } from "./profileInsightBudget";
import { PROFILE_LAYER_TAXONOMY } from "./profileInsightTaxonomy";
import type {
  ProfileInsightAuditRow,
  ProfileInsightAuditStatus,
  ProfileInsightCoverageReport,
  ProfileTaxonomyInsightSlot,
} from "./profileInsightTypes";
import {
  findCrossLayerDuplicate,
  findSameLayerSemanticDuplicates,
  formatSlotSource,
  isWeakSlot,
} from "./profileInsightSlotRegistry";

export function buildProfileInsightCoverageReport(
  profileLabel: string,
  slots: ProfileTaxonomyInsightSlot[],
): ProfileInsightCoverageReport {
  const sameLayerDup = findSameLayerSemanticDuplicates(slots);
  const slotByKey = new Map<string, ProfileTaxonomyInsightSlot>(
    slots.map((s) => [`${s.layer}:${s.categoryId}`, s]),
  );

  const rows: ProfileInsightAuditRow[] = [];

  for (const layerSpec of PROFILE_LAYER_TAXONOMY) {
    for (const cat of layerSpec.categories) {
      const key = `${layerSpec.layer}:${cat.id}`;
      const slot = slotByKey.get(key) ?? null;

      if (!slot) {
        rows.push({
          layer: layerSpec.layer,
          categoryId: cat.id,
          text: null,
          source: null,
          status: "missing",
        });
        continue;
      }

      let status: ProfileInsightAuditStatus = "unique";
      let duplicateOf: string | undefined;

      if (isWeakSlot(slot)) {
        status = "weak";
      } else if (sameLayerDup.has(key)) {
        status = "duplicate";
        duplicateOf = sameLayerDup.get(key);
      } else {
        const cross = findCrossLayerDuplicate(slot, slots);
        if (cross) {
          status = "duplicate";
          duplicateOf = `${cross.layer}:${cross.categoryId}`;
        }
      }

      rows.push({
        layer: layerSpec.layer,
        categoryId: cat.id,
        text: slot.text,
        source: formatSlotSource(slot),
        status,
        duplicateOf,
      });
    }
  }

  const gaps = rows.filter((r) => r.status === "missing").map((r) => ({ layer: r.layer, categoryId: r.categoryId }));

  const summary = {
    filled: rows.filter((r) => r.status !== "missing").length,
    missing: rows.filter((r) => r.status === "missing").length,
    duplicate: rows.filter((r) => r.status === "duplicate").length,
    weak: rows.filter((r) => r.status === "weak").length,
    unique: rows.filter((r) => r.status === "unique").length,
  };

  return { profileLabel, rows, gaps, summary };
}

export function formatCoverageReportMarkdown(report: ProfileInsightCoverageReport): string {
  const totalRequired = Object.values(PROFILE_INSIGHT_BUDGET).reduce((a, b) => a + b, 0);
  const lines: string[] = [
    `# Profile taxonomy audit · ${report.profileLabel}`,
    "",
    `**Generated:** ${new Date().toISOString().slice(0, 10)}`,
    "",
    "## Summary",
    "",
    "| Metric | Count |",
    "|--------|-------|",
    `| Required categories | ${totalRequired} |`,
    `| Filled | ${report.summary.filled} |`,
    `| Unique | ${report.summary.unique} |`,
    `| Duplicate | ${report.summary.duplicate} |`,
    `| Weak | ${report.summary.weak} |`,
    `| Missing (gaps) | ${report.summary.missing} |`,
    "",
    "## Table",
    "",
    "| layer | categoryId | text | source | status | duplicateOf |",
    "|-------|------------|------|--------|--------|-------------|",
  ];

  for (const row of report.rows) {
    const text = row.text ? row.text.replace(/\|/g, "\\|").replace(/\n/g, " ") : "—";
    const source = row.source ?? "—";
    const dup = row.duplicateOf ?? "—";
    lines.push(`| ${row.layer} | ${row.categoryId} | ${text} | ${source} | ${row.status} | ${dup} |`);
  }

  if (report.gaps.length) {
    lines.push("", "## Gaps (honest empty)", "");
    for (const g of report.gaps) {
      lines.push(`- \`${g.layer}.${g.categoryId}\``);
    }
  }

  lines.push(
    "",
    "## Pass criteria",
    "",
    "- All layers answer different user questions",
    "- Each filled category = distinct dimension (not paraphrase)",
    "- No literal duplicates across layers",
    "- Gaps visible, no filler water",
    "",
  );

  return lines.join("\n");
}

export function layerCoveragePass(layer: ProfileInsightLayer, report: ProfileInsightCoverageReport): boolean {
  const layerRows = report.rows.filter((r) => r.layer === layer);
  const required = layerRows.length;
  const unique = layerRows.filter((r) => r.status === "unique").length;
  return unique >= Math.min(3, required);
}
