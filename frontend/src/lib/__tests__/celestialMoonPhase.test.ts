import {
  celestialPhaseFromCycleDay,
  celestialPhaseFromUtcDate,
  resolveCelestialMoonPhase,
  SYNODIC_PERIOD_DAYS,
} from "@/lib/celestialMoonPhase";

describe("celestialMoonPhase", () => {
  it("maps cycle_day continuously (new → full → new)", () => {
    expect(celestialPhaseFromCycleDay(0)).toBeCloseTo(0, 5);
    expect(celestialPhaseFromCycleDay(SYNODIC_PERIOD_DAYS / 2)).toBeCloseTo(0.5, 5);
    expect(celestialPhaseFromCycleDay(SYNODIC_PERIOD_DAYS)).toBeCloseTo(0, 5);
  });

  it("prefers cycle_day over discrete id/name", () => {
    expect(
      resolveCelestialMoonPhase({
        cycleDay: SYNODIC_PERIOD_DAYS * 0.25,
        phaseId: "full",
        phaseName: "Полнолуние",
      }),
    ).toBeCloseTo(0.25, 5);
  });

  it("falls back to phase id then Russian name", () => {
    expect(resolveCelestialMoonPhase({ phaseId: "full" })).toBe(0.5);
    expect(resolveCelestialMoonPhase({ phaseId: "new" })).toBe(0);
    expect(resolveCelestialMoonPhase({ phaseName: "Убывающая луна" })).toBe(0.625);
    expect(resolveCelestialMoonPhase({ phaseName: "Новолуние" })).toBe(0);
    expect(resolveCelestialMoonPhase({})).toBeNull();
  });

  it("maps UTC date through the synodic month (known new moon ≈ 0)", () => {
    const nearNew = new Date("2000-01-07T12:00:00Z");
    const waxing = new Date("2000-01-14T12:00:00Z");
    const nearNewPhase = celestialPhaseFromUtcDate(nearNew);
    expect(nearNewPhase).toBeGreaterThanOrEqual(0);
    expect(nearNewPhase).toBeLessThan(1);
    expect(celestialPhaseFromUtcDate(waxing)).toBeGreaterThan(nearNewPhase);
    expect(celestialPhaseFromUtcDate(new Date("2000-01-21T12:00:00Z"))).toBeCloseTo(0.5, 1);
  });
});
