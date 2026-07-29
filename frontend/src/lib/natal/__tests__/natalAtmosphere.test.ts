import { resolveNatalAtmosphereElement } from "@/lib/natal/natalAtmosphere";

describe("natalAtmosphere", () => {
  it("maps Sun signs to elements for stage tint", () => {
    expect(resolveNatalAtmosphereElement("Leo")).toBe("fire");
    expect(resolveNatalAtmosphereElement("Virgo")).toBe("earth");
    expect(resolveNatalAtmosphereElement("Aquarius")).toBe("air");
    expect(resolveNatalAtmosphereElement("Pisces")).toBe("water");
  });

  it("falls back to earth when unknown", () => {
    expect(resolveNatalAtmosphereElement(null)).toBe("earth");
    expect(resolveNatalAtmosphereElement("")).toBe("earth");
  });
});
