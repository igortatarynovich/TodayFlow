import {
  dayPhaseFromMood,
  moodFromTimeOfDay,
  resolveProductMood,
  themeModeFromMood,
  writeMoodPin,
  readMoodPin,
} from "@/lib/productMoodTheme";
import { resolveDayPhase } from "@/lib/dayPhaseAtmosphere";
import { resolveAppearance } from "@/lib/productAppearance";
import { resolveDayPhaseHeroWash, resolveHeroChromeTone } from "@/lib/dayPhaseHeroWash";

describe("productMoodTheme", () => {
  beforeEach(() => {
    writeMoodPin(null);
  });

  it("maps clock to calm/focus/night", () => {
    expect(moodFromTimeOfDay("morning")).toBe("calm");
    expect(moodFromTimeOfDay("day")).toBe("focus");
    expect(moodFromTimeOfDay("evening")).toBe("night");
  });

  it("does not drive appearance from mood (night mood ≠ dark mode)", () => {
    // Deprecated helper must not flip chrome to dark from mood alone.
    expect(themeModeFromMood("night")).toBe("light");
    expect(themeModeFromMood("calm")).toBe("light");
  });

  it("pin wins over first-day and clock", () => {
    expect(
      resolveProductMood({ pinnedMood: "night", isFirstDay: true, timeOfDay: "morning" }),
    ).toBe("night");
  });

  it("first-day suggests clarity when not pinned", () => {
    expect(resolveProductMood({ isFirstDay: true, timeOfDay: "evening" })).toBe("clarity");
  });

  it("persists pin in localStorage", () => {
    writeMoodPin("focus");
    expect(readMoodPin()).toBe("focus");
    writeMoodPin(null);
    expect(readMoodPin()).toBeNull();
  });
});

describe("appearance × dayPhase × mood independence", () => {
  it("appearance ignores mood", () => {
    expect(resolveAppearance({ mode: "dark" })).toBe("dark");
    expect(resolveAppearance({ mode: "light" })).toBe("light");
    expect(resolveAppearance({ mode: "system", systemDark: true })).toBe("dark");
    expect(resolveAppearance({ mode: "system", systemDark: false })).toBe("light");
  });

  it("day-phase ignores mood pin", () => {
    expect(resolveDayPhase({ pathname: "/today", hour: 14, mood: "night" })).toBe("day");
    expect(resolveDayPhase({ pathname: "/profile", mood: "night", hour: 14 })).toBeNull();
  });

  it("daytime hero plate stays daylight even under dark appearance", () => {
    const wash = resolveDayPhaseHeroWash("day");
    expect(wash.src).not.toContain("moon");
    expect(wash.plate).toBe("daylight");
    expect(resolveHeroChromeTone(wash, "dark")).toBe("dark");
    expect(resolveHeroChromeTone(wash, "light")).toBe("light");
  });

  it("evening/night plates use moon media", () => {
    expect(resolveDayPhaseHeroWash("evening").src).toContain("moon_wash");
    expect(resolveDayPhaseHeroWash("night").src).toContain("moon_wash");
  });

  it("dayPhaseFromMood remains informational only", () => {
    expect(dayPhaseFromMood("night")).toBe("evening");
  });
});
