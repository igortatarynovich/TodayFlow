import {
  TODAY_SCREEN_FLOW_CAPABILITY,
  resolveTodayCapabilityDepth,
  todayCapabilityAllowsPersonal,
} from "@/lib/todayScreenFlowCapability";

describe("Today ScreenFlow capability matrix", () => {
  it("guest sees Global + ritual, never Personal Day", () => {
    const cap = TODAY_SCREEN_FLOW_CAPABILITY.guest;
    expect(cap.globalDay).toBe(true);
    expect(cap.rituals).toBe(true);
    expect(cap.personalDay).toBe(false);
    expect(cap.natalTimeline).toBe(false);
    expect(cap.whyPersonal).toBe(false);
    expect(todayCapabilityAllowsPersonal("guest")).toBe(false);
  });

  it("deep natal unlocks personal + timeline", () => {
    const cap = TODAY_SCREEN_FLOW_CAPABILITY.deep;
    expect(cap.personalDay).toBe(true);
    expect(cap.natalTimeline).toBe(true);
    expect(todayCapabilityAllowsPersonal("deep")).toBe(true);
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
