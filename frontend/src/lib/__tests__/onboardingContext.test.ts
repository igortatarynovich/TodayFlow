import {
  buildOnboardingEventIdempotencyKey,
  buildOnboardingRitualContext,
  hasOnboardingIntent,
  hasOnboardingReality,
  readOnboardingContext,
  saveIntentTheme,
  saveRealityState,
  todayDayKey,
} from "@/lib/onboardingContext";

describe("onboardingContext", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("persists intent and reality for the same day", () => {
    const dayKey = "2026-06-23";
    saveIntentTheme("focus", dayKey);
    saveRealityState("stable", dayKey);

    const ctx = readOnboardingContext();
    expect(ctx.intent_theme).toBe("focus");
    expect(ctx.reality_state).toBe("stable");
    expect(ctx.day_key).toBe(dayKey);
    expect(hasOnboardingIntent(ctx, dayKey)).toBe(true);
    expect(hasOnboardingReality(ctx, dayKey)).toBe(true);
  });

  it("builds ritual_context from onboarding picks", () => {
    saveIntentTheme("clarity", "2026-06-23");
    saveRealityState("tired", "2026-06-23");

    expect(buildOnboardingRitualContext()).toEqual({
      head_topic: "clarity",
      mood: "tired",
      day_events: ["onboarding intent: clarity", "onboarding state: tired"],
    });
  });

  it("creates stable idempotency keys", () => {
    expect(buildOnboardingEventIdempotencyKey("onboarding_intent_selected", "money", "2026-06-23")).toBe(
      "onboarding_intent_selected:2026-06-23:money",
    );
  });

  it("formats todayDayKey as ISO date", () => {
    expect(todayDayKey(new Date("2026-06-23T15:00:00"))).toBe("2026-06-23");
  });
});
