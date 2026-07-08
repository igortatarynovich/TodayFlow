import {
  buildConfidenceSparklineCells,
  formatConfidencePercent,
  formatDelta30dLabel,
  shouldShowCumInsights,
} from "@/lib/profileCumInsights";
import type { CompactUserModel } from "@/lib/types";

describe("profileCumInsights", () => {
  it("formats confidence percent and delta", () => {
    expect(formatConfidencePercent(0.655)).toBe("66%");
    expect(formatDelta30dLabel(0.15)).toBe("+15 за 30 дн");
    expect(formatDelta30dLabel(-0.08)).toBe("-8 за 30 дн");
    expect(formatDelta30dLabel(null)).toBeNull();
  });

  it("builds sparkline cells with normalized heights", () => {
    const cells = buildConfidenceSparklineCells([
      { snapshot_date: "2026-06-01", overall: 0.4 },
      { snapshot_date: "2026-07-01", overall: 0.62 },
    ]);
    expect(cells).toHaveLength(2);
    expect(cells[0].heightPct).toBeLessThan(cells[1].heightPct);
  });

  it("detects when insights should render", () => {
    const cum = {
      contract_version: "compact_user_model_v0",
      confidence: { overall: 0.5 },
    } as CompactUserModel;
    expect(shouldShowCumInsights(cum)).toBe(true);
    expect(shouldShowCumInsights(null)).toBe(false);
  });
});
