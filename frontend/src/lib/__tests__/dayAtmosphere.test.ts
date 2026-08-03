import {
  DAY_ATMOSPHERE_DEFAULT,
  DAY_MODE_DECOR_VARIANTS,
  DAY_VISUAL_MODES,
  dayAtmosphereTokens,
  readDayModePin,
  resolveDayAtmosphere,
  writeDayModePin,
} from "@/lib/dayAtmosphere";

describe("resolveDayAtmosphere", () => {
  it("falls back to the neutral default when given nothing", () => {
    expect(resolveDayAtmosphere()).toEqual({
      ...DAY_ATMOSPHERE_DEFAULT,
      decor_variant: DAY_MODE_DECOR_VARIANTS[DAY_ATMOSPHERE_DEFAULT.visual_mode][0],
    });
  });

  it("never returns a visual_mode outside the closed set", () => {
    const result = resolveDayAtmosphere({ visual_mode: "sagittarius-rising" as never });
    expect(DAY_VISUAL_MODES).toContain(result.visual_mode);
    expect(result.visual_mode).toBe(DAY_ATMOSPHERE_DEFAULT.visual_mode);
  });

  it("accepts every mode in the closed set", () => {
    for (const mode of DAY_VISUAL_MODES) {
      expect(resolveDayAtmosphere({ visual_mode: mode }).visual_mode).toBe(mode);
    }
  });

  it("clamps intensity and warmth to 0..1", () => {
    expect(resolveDayAtmosphere({ intensity: 4.2 }).intensity).toBe(1);
    expect(resolveDayAtmosphere({ intensity: -3 }).intensity).toBe(0);
    expect(resolveDayAtmosphere({ warmth: 999 }).warmth).toBe(1);
  });

  it("falls back on NaN/garbage numeric input instead of propagating it", () => {
    expect(resolveDayAtmosphere({ intensity: Number.NaN }).intensity).toBe(DAY_ATMOSPHERE_DEFAULT.intensity);
  });

  it("pin wins over engine-suggested visual_mode", () => {
    const result = resolveDayAtmosphere({ visual_mode: "momentum", pinnedMode: "depth" });
    expect(result.visual_mode).toBe("depth");
  });

  it("rejects an unlisted decor_variant and falls back to the mode's first variant", () => {
    const result = resolveDayAtmosphere({ visual_mode: "tension", decor_variant: "not-a-real-variant" });
    expect(result.decor_variant).toBe(DAY_MODE_DECOR_VARIANTS.tension[0]);
  });

  it("accepts the mode's second decor variant when named explicitly", () => {
    const result = resolveDayAtmosphere({ visual_mode: "tension", decor_variant: DAY_MODE_DECOR_VARIANTS.tension[1] });
    expect(result.decor_variant).toBe(DAY_MODE_DECOR_VARIANTS.tension[1]);
  });

  it("rejects an out-of-range contrast/motion/time_phase and falls back to defaults", () => {
    const result = resolveDayAtmosphere({
      contrast: "extreme" as never,
      motion: "fast" as never,
      time_phase: "midnight-plus" as never,
    });
    expect(result.contrast).toBe(DAY_ATMOSPHERE_DEFAULT.contrast);
    expect(result.motion).toBe(DAY_ATMOSPHERE_DEFAULT.motion);
    expect(result.time_phase).toBe(DAY_ATMOSPHERE_DEFAULT.time_phase);
  });
});

describe("dayAtmosphereTokens", () => {
  it("produces every --day-* key named in FOUNDATION_UI §11.8 for each mode", () => {
    const expectedKeys = [
      "--day-bg-base",
      "--day-bg-glow-primary",
      "--day-bg-glow-secondary",
      "--day-decor-color",
      "--day-decor-opacity",
      "--day-accent-soft",
      "--day-motion-duration",
      "--day-motion-distance",
      "--day-surface-tint",
    ].sort();

    for (const mode of DAY_VISUAL_MODES) {
      const tokens = dayAtmosphereTokens(resolveDayAtmosphere({ visual_mode: mode }));
      expect(Object.keys(tokens).sort()).toEqual(expectedKeys);
    }
  });

  it("is deterministic — same contract in, same tokens out", () => {
    const contract = resolveDayAtmosphere({ visual_mode: "flow", intensity: 0.6, contrast: "strong" });
    expect(dayAtmosphereTokens(contract)).toEqual(dayAtmosphereTokens(contract));
  });

  it("zeroes motion tokens when motion is 'none', regardless of mode/intensity", () => {
    const contract = resolveDayAtmosphere({ visual_mode: "momentum", intensity: 1, motion: "none" });
    const tokens = dayAtmosphereTokens(contract);
    expect(tokens["--day-motion-duration"]).toBe("0s");
    expect(tokens["--day-motion-distance"]).toBe("0px");
  });

  it("keeps motion duration within the 15–40s atmosphere-only range from §11.4", () => {
    for (const mode of DAY_VISUAL_MODES) {
      for (const intensity of [0, 0.5, 1]) {
        const contract = resolveDayAtmosphere({ visual_mode: mode, intensity, motion: "low" });
        const duration = Number.parseFloat(dayAtmosphereTokens(contract)["--day-motion-duration"]);
        expect(duration).toBeGreaterThanOrEqual(15);
        expect(duration).toBeLessThanOrEqual(40);
      }
    }
  });

  it("higher intensity reads as higher decor opacity within the same contrast band", () => {
    const low = dayAtmosphereTokens(resolveDayAtmosphere({ visual_mode: "clarity", intensity: 0, contrast: "medium" }));
    const high = dayAtmosphereTokens(resolveDayAtmosphere({ visual_mode: "clarity", intensity: 1, contrast: "medium" }));
    expect(Number.parseFloat(high["--day-decor-opacity"])).toBeGreaterThan(Number.parseFloat(low["--day-decor-opacity"]));
  });
});

describe("day mode pin", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("round-trips a valid pin", () => {
    writeDayModePin("renewal");
    expect(readDayModePin()).toBe("renewal");
  });

  it("clears the pin when written with null", () => {
    writeDayModePin("renewal");
    writeDayModePin(null);
    expect(readDayModePin()).toBeNull();
  });

  it("ignores corrupted storage instead of throwing", () => {
    window.localStorage.setItem("todayflow_day_mode_pin_v1", "{not json");
    expect(readDayModePin()).toBeNull();
  });

  it("ignores a stored value outside the closed mode set", () => {
    window.localStorage.setItem("todayflow_day_mode_pin_v1", JSON.stringify({ mode: "solar-flare" }));
    expect(readDayModePin()).toBeNull();
  });
});
