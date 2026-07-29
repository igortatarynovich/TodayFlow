import {
  minPlanetDiscDistance,
  resolveNatalPlanetLayout,
} from "@/lib/natal/natalWheelLayout";

/** Radii matching NatalChartWheel (size 720, inner 0.22, houses in zodiac). */
const WHEEL = {
  baseRadius: 174,
  minRadius: 91,
  maxRadius: 257,
  discRadius: 15,
  gap: 9,
};

describe("natalWheelLayout", () => {
  it("separates a dense stellium so discs do not stack", () => {
    const angles = [10, 12, 14, 15.5, 17].map((lon) => (270 - lon + 360) % 360);
    const layout = resolveNatalPlanetLayout(
      angles.map((angle) => ({ angle })),
      WHEEL,
    );
    const minDist = minPlanetDiscDistance(layout);
    expect(layout).toHaveLength(5);
    expect(minDist).toBeGreaterThanOrEqual(WHEEL.discRadius * 2 + 4);
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
      WHEEL,
    );
    expect(minPlanetDiscDistance(layout)).toBeGreaterThanOrEqual(WHEEL.discRadius * 2 + 2);
  });

  it("separates a seven-body pile without collapsing to one ring", () => {
    const longs = [0, 2, 4, 6, 8, 10, 12];
    const angles = longs.map((lon) => (270 - lon + 360) % 360);
    const layout = resolveNatalPlanetLayout(
      angles.map((angle) => ({ angle })),
      WHEEL,
    );
    expect(minPlanetDiscDistance(layout)).toBeGreaterThanOrEqual(WHEEL.discRadius * 2);
    const radii = layout.map((p) => p.radius);
    expect(Math.max(...radii) - Math.min(...radii)).toBeGreaterThan(40);
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
