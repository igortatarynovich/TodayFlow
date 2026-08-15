import {
  TODAY_SCREEN_FLOW_CAPABILITY,
  resolveTodayCapabilityDepth,
  todayCapabilityAllowsPersonal,
  todayCapabilityShowsTimelineOnToday,
} from "@/lib/todayScreenFlowCapability";

describe("Today ScreenFlow capability matrix", () => {
  it("guest sees TODAY + ritual + evening, never MY DAY", () => {
    const cap = TODAY_SCREEN_FLOW_CAPABILITY.guest;
    expect(cap.today).toBe(true);
    expect(cap.ritual).toBe(true);
    expect(cap.evening).toBe(true);
    expect(cap.myDay).toBe(false);
    expect(cap.personalTimeline).toBe(false);
    expect(todayCapabilityAllowsPersonal("guest")).toBe(false);
  });

  it("never shows a timeline on the Global TODAY screen", () => {
    expect(todayCapabilityShowsTimelineOnToday()).toBe(false);
  });

  it("deep natal unlocks MY DAY + personal timeline", () => {
    const cap = TODAY_SCREEN_FLOW_CAPABILITY.deep;
    expect(cap.myDay).toBe(true);
    expect(cap.personalTimeline).toBe(true);
    expect(todayCapabilityAllowsPersonal("deep")).toBe(true);
  });

  it("light DOB unlocks MY DAY without natal timeline", () => {
    const cap = TODAY_SCREEN_FLOW_CAPABILITY.light;
    expect(cap.myDay).toBe(true);
    expect(cap.personalTimeline).toBe(false);
  });

  it("resolves depth from evidence, not UI wish", () => {
    expect(resolveTodayCapabilityDepth({ authenticated: false })).toBe("guest");
    expect(resolveTodayCapabilityDepth({ authenticated: true })).toBe("general");
    expect(
      resolveTodayCapabilityDepth({ authenticated: true, hasBirthDate: true }),
    ).toBe("light");
    expect(
      resolveTodayCapabilityDepth({
        authenticated: true,
        hasBirthDate: true,
        hasBirthTimePlace: true,
      }),
    ).toBe("deep");
  });
});
