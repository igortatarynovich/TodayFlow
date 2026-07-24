import {
  dayPhaseFromMood,
  moodFromTimeOfDay,
  resolveProductMood,
  themeModeFromMood,
  writeMoodPin,
  readMoodPin,
} from "@/lib/productMoodTheme";
import { resolveDayPhase } from "@/lib/dayPhaseAtmosphere";

describe("productMoodTheme", () => {
  beforeEach(() => {
    writeMoodPin(null);
  });

  it("maps clock to calm/focus/night", () => {
    expect(moodFromTimeOfDay("morning")).toBe("calm");
    expect(moodFromTimeOfDay("day")).toBe("focus");
    expect(moodFromTimeOfDay("evening")).toBe("night");
  });

  it("maps mood to light/dark for legacy data-theme", () => {
    expect(themeModeFromMood("calm")).toBe("light");
    expect(themeModeFromMood("focus")).toBe("light");
    expect(themeModeFromMood("clarity")).toBe("light");
    expect(themeModeFromMood("night")).toBe("dark");
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

describe("mood ↔ day-phase alignment", () => {
  it("maps moods to matching day-phases", () => {
    expect(dayPhaseFromMood("calm")).toBe("morning");
    expect(dayPhaseFromMood("focus")).toBe("day");
    expect(dayPhaseFromMood("night")).toBe("evening");
    expect(dayPhaseFromMood("clarity")).toBe("first");
  });

  it("day-phase follows mood on /today and stays null elsewhere", () => {
    expect(
      resolveDayPhase({ pathname: "/profile", mood: "night", timeOfDay: "morning" }),
    ).toBeNull();
    expect(
      resolveDayPhase({ pathname: "/today", mood: "night", isFirstDay: true, timeOfDay: "morning" }),
    ).toBe("evening");
    expect(
      resolveDayPhase({ pathname: "/today", mood: "clarity", timeOfDay: "evening" }),
    ).toBe("first");
  });

  it("without mood, first-day still wins over clock on /today", () => {
    expect(
      resolveDayPhase({ pathname: "/today", isFirstDay: true, timeOfDay: "evening" }),
    ).toBe("first");
  });
});
