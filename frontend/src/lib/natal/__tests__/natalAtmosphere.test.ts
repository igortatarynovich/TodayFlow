import {
  resolveNatalAtmosphereElement,
  resolveNatalPlanetJewel,
  sunSignFromPositions,
} from "@/lib/natal/natalAtmosphere";

describe("natalAtmosphere jewels", () => {
  it("resolves sun sign element for stage tint", () => {
    expect(resolveNatalAtmosphereElement("Leo")).toBe("fire");
    expect(resolveNatalAtmosphereElement("Pisces")).toBe("water");
    expect(resolveNatalAtmosphereElement(null)).toBe("earth");
  });

  it("tints planet jewels by occupied sign element", () => {
    const fire = resolveNatalPlanetJewel("Aries");
    const water = resolveNatalPlanetJewel("Cancer");
    const air = resolveNatalPlanetJewel("Aquarius");
    expect(fire?.element).toBe("fire");
    expect(water?.element).toBe("water");
    expect(air?.element).toBe("air");
    expect(fire?.stroke).not.toBe(water?.stroke);
    expect(resolveNatalPlanetJewel(null)).toBeNull();
  });

  it("finds sun sign from positions", () => {
    expect(
      sunSignFromPositions([
        { body: "Moon", sign: "Taurus" },
        { body: "Sun", sign: "Leo" },
      ]),
    ).toBe("Leo");
  });
});
