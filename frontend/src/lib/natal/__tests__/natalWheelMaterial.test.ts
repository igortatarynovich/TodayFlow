import {
  classifyAspectKind,
  natalAspectLegendItems,
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

  it("uses warm vs cool color anchors (not beige-on-beige)", () => {
    const trine = resolveNatalAspectRenderStyle({ aspect_id: "moon_venus_trine" });
    const square = resolveNatalAspectRenderStyle({ aspect_id: "sun_mars_square" });
    const opposition = resolveNatalAspectRenderStyle({ aspect_id: "sun_moon_opposition" });
    // Warm amber family for soft
    expect(trine.color.toLowerCase()).toMatch(/^#[cba]/);
    // Cool slate for hard — must differ from trine
    expect(square.color).not.toBe(trine.color);
    expect(opposition.color).not.toBe(trine.color);
    expect(square.color.toLowerCase()).toMatch(/^#[45]/);
    expect(trine.opacity).toBeGreaterThanOrEqual(0.55);
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

  it("does not treat sesquiquadrate as a major square", () => {
    expect(classifyAspectKind("sun_moon_sesquiquadrate", "Sun Sesquiquadrate Moon")).toBe("other");
    expect(classifyAspectKind(null, "полутораквадрат")).toBe("other");
    expect(resolveNatalAspectRenderStyle({
      aspect_id: "sun_moon_sesquiquadrate",
      label: "Sun Sesquiquadrate Moon",
    }).label).toBe("Связь");
  });

  it("exposes legend items from the same color SoT", () => {
    const items = natalAspectLegendItems();
    expect(items.map((i) => i.label)).toEqual([
      "Соединение",
      "Трин",
      "Секстиль",
      "Квадрат",
      "Оппозиция",
    ]);
    expect(items[1].color).toBe(resolveNatalAspectRenderStyle({ aspect_id: "x_trine" }).color);
  });
});
