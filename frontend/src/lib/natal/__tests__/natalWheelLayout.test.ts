import {
  minPlanetDiscDistance,
  resolveNatalPlanetLayout,
} from "@/lib/natal/natalWheelLayout";

describe("natalWheelLayout", () => {
  it("separates a dense stellium so discs do not stack", () => {
    const angles = [10, 12, 14, 15.5, 17].map((lon) => (270 - lon + 360) % 360);
    const layout = resolveNatalPlanetLayout(
      angles.map((angle) => ({ angle })),
      {
        baseRadius: 200,
        minRadius: 140,
        maxRadius: 280,
        discRadius: 16,
        gap: 8,
      },
    );
    const minDist = minPlanetDiscDistance(layout);
    expect(layout).toHaveLength(5);
    expect(minDist).toBeGreaterThanOrEqual(16 * 2 + 4);
    const radii = new Set(layout.map((p) => Math.round(p.radius / 10)));
    expect(radii.size).toBeGreaterThanOrEqual(2);
    expect(layout.some((p) => p.leader)).toBe(true);
  });

  it("separates a Capricorn-like pile near one house cusp", () => {
    // Five bodies within ~9° — matches the “near house 1” screenshot failure mode.
    const longs = [278, 280.5, 282, 284, 286.5];
    const angles = longs.map((lon) => (270 - lon + 360) % 360);
    const layout = resolveNatalPlanetLayout(
      angles.map((angle) => ({ angle })),
      {
        baseRadius: 210,
        minRadius: 150,
        maxRadius: 290,
        discRadius: 16,
        gap: 8,
      },
    );
    expect(minPlanetDiscDistance(layout)).toBeGreaterThanOrEqual(16 * 2 + 2);
  });

  it("leaves isolated planets near the base ring", () => {
    const layout = resolveNatalPlanetLayout(
      [{ angle: 0 }, { angle: 90 }, { angle: 180 }, { angle: 270 }],
      {
        baseRadius: 200,
        minRadius: 150,
        maxRadius: 260,
        discRadius: 16,
      },
    );
    for (const p of layout) {
      expect(Math.abs(p.radius - 200)).toBeLessThan(14);
      expect(Math.abs(p.angleOffset)).toBeLessThan(1.5);
      expect(p.discScale).toBe(1);
    }
  });
});
