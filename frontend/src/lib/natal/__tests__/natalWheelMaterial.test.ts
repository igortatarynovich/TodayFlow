import {
  classifyAspectKind,
  resolveNatalAspectRenderStyle,
} from "@/lib/natal/natalWheelMaterial";

describe("natalWheelMaterial", () => {
  it("marks hard aspects as strong and soft aspects as soft", () => {
    const square = resolveNatalAspectRenderStyle({ aspect_id: "sun_moon_square" });
    const trine = resolveNatalAspectRenderStyle({ aspect_id: "moon_venus_trine" });
    expect(square.weight).toBe("strong");
    expect(trine.weight).toBe("soft");
    expect(square.width).toBeGreaterThan(trine.width);
    expect(square.opacity).toBeGreaterThan(trine.opacity);
    expect(square.stack).toBeGreaterThan(trine.stack);
  });

  it("lets tension_level boost or soften", () => {
    const softConj = resolveNatalAspectRenderStyle({
      aspect_id: "sun_mercury_conjunction",
      tension_level: "low",
    });
    const hardTrine = resolveNatalAspectRenderStyle({
      aspect_id: "moon_venus_trine",
      tension_level: "high",
    });
    expect(softConj.weight).toBe("soft");
    expect(hardTrine.weight).toBe("strong");
  });

  it("classifies RU labels", () => {
    expect(classifyAspectKind(null, "Квадрат")).toBe("square");
    expect(classifyAspectKind(null, "Трин")).toBe("trine");
  });
});
