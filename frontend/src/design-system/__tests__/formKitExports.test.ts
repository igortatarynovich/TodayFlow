/**
 * Form Kit closed-set smoke — every §15.8 export must resolve from @/design-system.
 */
import * as DS from "@/design-system";

const FORM_KIT_EXPORTS = [
  "DsSurface",
  "DsCard",
  "DsChip",
  "DsChipCluster",
  "DsFab",
  "DsRadialMeter",
  "DsDotMeter",
  "DsSpectrum",
  "DsMetric",
  "DsStarDivider",
  "DsAvatar",
  "DsOverlaySheet",
  "DsContentCard",
  "DsListPanel",
  "DsHeroBlock",
  "DsWindowCard",
  "DsMetricCard",
  "DsActionCard",
  "DsListRow",
  "DsPlanet",
  "DsZodiac",
  "DsNumber",
  "DsTarotFace",
  "DsAngle",
] as const;

describe("Form Kit exports", () => {
  it("exposes the closed Form Kit set", () => {
    for (const name of FORM_KIT_EXPORTS) {
      expect(typeof (DS as Record<string, unknown>)[name]).toBe("function");
    }
  });
});
