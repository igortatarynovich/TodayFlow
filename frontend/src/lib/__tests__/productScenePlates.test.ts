import {
  compatibilityModePlate,
  landingServicePlate,
  PRODUCT_SCENE_PLATES,
  resolveProductScenePlate,
} from "@/lib/productScenePlates";

describe("productScenePlates", () => {
  it("resolves every registered plate with a public src", () => {
    for (const id of Object.keys(PRODUCT_SCENE_PLATES) as Array<keyof typeof PRODUCT_SCENE_PLATES>) {
      const plate = resolveProductScenePlate(id);
      expect(plate).not.toBeNull();
      expect(plate!.src.startsWith("/images/")).toBe(true);
      expect(plate!.position.length).toBeGreaterThan(0);
    }
  });

  it("maps compatibility modes to distinct plates", () => {
    expect(compatibilityModePlate("love")).toBe("compat_love");
    expect(compatibilityModePlate("family")).toBe("compat_pair");
    expect(compatibilityModePlate("parenting")).toBe("compat_day");
    expect(compatibilityModePlate("office")).toBe("compat_map");
    expect(compatibilityModePlate("unknown")).toBe("compat_night");
  });

  it("keeps tarot and practice plates on different assets", () => {
    expect(PRODUCT_SCENE_PLATES.tarot_cards.src).not.toBe(PRODUCT_SCENE_PLATES.tarot_quiet.src);
    expect(PRODUCT_SCENE_PLATES.practice_body.src).not.toBe(PRODUCT_SCENE_PLATES.practice_still.src);
    expect(PRODUCT_SCENE_PLATES.compat_night.src).not.toBe(PRODUCT_SCENE_PLATES.compat_day.src);
  });

  it("maps landing service blocks to distinct banners", () => {
    expect(landingServicePlate("tarot")).toBe("tarot_cards");
    expect(landingServicePlate("compatibility")).toBe("compat_pair");
    expect(landingServicePlate("practices")).toBe("practice_still");
    expect(PRODUCT_SCENE_PLATES.landing_hero.src).toContain("day_girl_banner");
    expect(PRODUCT_SCENE_PLATES.landing_today.src).toContain("day_banner");
    expect(PRODUCT_SCENE_PLATES.landing_cta.src).toContain("dashboard_hero");
  });
});
