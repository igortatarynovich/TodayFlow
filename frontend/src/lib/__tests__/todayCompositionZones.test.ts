import { todayCompositionZones, todayEveningStoryZones, resolveTodayCompositionZones } from "@/lib/todayCompositionZones";

describe("todayCompositionZones", () => {
  it("firstToday shows foundation and ritual gates before personalization", () => {
    const z = todayCompositionZones("firstToday");
    expect(z.continuity).toBe(false);
    expect(z.greeting).toBe(true);
    expect(z.pulse).toBe(true);
    expect(z.glance).toBe(false);
    expect(z.astroContext).toBe(false);
    expect(z.ritualTarot).toBe(true);
    expect(z.whyStory).toBe(false);
    expect(z.strengthen).toBe(false);
    expect(z.promise).toBe(false);
    expect(z.actions).toBe(false);
    expect(z.growthPromise).toBe(false);
    expect(z.evening).toBe(false);
  });

  it("unlocks personalized zones after card and number", () => {
    const z = todayCompositionZones("default", {
      tarotPickedName: "Отшельник",
      numberConfirmed: true,
    });
    expect(z.whyStory).toBe(true);
    expect(z.strengthen).toBe(true);
    expect(z.promise).toBe(true);
    expect(z.actions).toBe(true);
    expect(z.growthPromise).toBe(true);
    expect(z.evening).toBe(true);
    expect(z.ritualNumber).toBe(true);
  });

  it("shows number gate only after tarot", () => {
    const beforeNumber = todayCompositionZones("default", { tarotPickedName: "Сила", numberConfirmed: false });
    expect(beforeNumber.ritualNumber).toBe(true);
    expect(beforeNumber.strengthen).toBe(true);

    const beforeTarot = todayCompositionZones("default", { tarotPickedName: null, numberConfirmed: false });
    expect(beforeTarot.ritualNumber).toBe(false);
  });

  it("evening story hides forward blocks but keeps promise", () => {
    const z = todayEveningStoryZones("default");
    expect(z.astroContext).toBe(false);
    expect(z.ritualTarot).toBe(false);
    expect(z.strengthen).toBe(false);
    expect(z.actions).toBe(false);
    expect(z.promise).toBe(true);
    expect(z.pulse).toBe(true);
    expect(z.growthPromise).toBe(true);
  });

  it("keeps ritual at evening when day is not personalized yet", () => {
    const z = resolveTodayCompositionZones({
      variant: "default",
      engagement: { tarotPickedName: null, numberConfirmed: false, dayGoal: null },
      isEveningSurface: true,
      personalizedReady: false,
    });
    expect(z.ritualTarot).toBe(true);
    expect(z.growthPromise).toBe(false);
    expect(z.evening).toBe(false);
  });

  it("switches to evening zones after ritual complete", () => {
    const z = resolveTodayCompositionZones({
      variant: "default",
      engagement: { tarotPickedName: "Сила", numberConfirmed: true, dayGoal: null },
      isEveningSurface: true,
      personalizedReady: true,
    });
    expect(z.ritualTarot).toBe(false);
    expect(z.growthPromise).toBe(true);
    expect(z.evening).toBe(true);
    expect(z.promise).toBe(true);
  });
});
