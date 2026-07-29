import {
  minPlanetDiscDistance,
  resolveNatalPlanetLayout,
} from "@/lib/natal/natalWheelLayout";

describe("natalWheelLayout", () => {
  it("separates a dense stellium so discs do not stack", () => {
    // 5 planets within ~8° — classic Capricorn-style pile
    const angles = [10, 12, 14, 15.5, 17].map((lon) => (270 - lon + 360) % 360);
    const layout = resolveNatalPlanetLayout(
      angles.map((angle) => ({ angle })),
      {
        baseRadius: 200,
        minRadius: 150,
        maxRadius: 260,
        discRadius: 18,
        gap: 5,
      },
    );
    const minDist = minPlanetDiscDistance(layout);
    expect(layout).toHaveLength(5);
    expect(minDist).toBeGreaterThanOrEqual(18 * 2 + 2);
    // Uses more than one radius band
    const radii = new Set(layout.map((p) => Math.round(p.radius / 8)));
    expect(radii.size).toBeGreaterThanOrEqual(2);
    // Leaders for offset discs
    expect(layout.some((p) => p.leader)).toBe(true);
  });

  it("leaves isolated planets near the base ring", () => {
    const layout = resolveNatalPlanetLayout(
      [{ angle: 0 }, { angle: 90 }, { angle: 180 }, { angle: 270 }],
      {
        baseRadius: 200,
        minRadius: 150,
        maxRadius: 260,
        discRadius: 18,
      },
    );
    for (const p of layout) {
      expect(Math.abs(p.radius - 200)).toBeLessThan(12);
      expect(Math.abs(p.angleOffset)).toBeLessThan(1.5);
    }
  });
});
