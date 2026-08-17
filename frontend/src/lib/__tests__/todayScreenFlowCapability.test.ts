import {
  TODAY_SCREEN_FLOW_CAPABILITY,
  profileHasBirthDate,
  profileHasBirthTimePlace,
  resolveTodayCapabilityDepth,
  resolveTodayCapabilityFromProfile,
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

  it("never shows a natal personal timeline on the Global TODAY screen", () => {
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

  it("reads DOB / time+place from Core Profile", () => {
    expect(profileHasBirthDate({ astro: { birth_date: "1990-01-01" } })).toBe(true);
    expect(
      profileHasBirthTimePlace({
        astro: {
          birth_date: "1990-01-01",
          birth_time: "12:00",
          location_name: "Москва",
        },
      }),
    ).toBe(true);
    expect(
      profileHasBirthTimePlace({
        astro: {
          birth_date: "1990-01-01",
          birth_time: "12:00",
          time_unknown: true,
          location_name: "Москва",
        },
      }),
    ).toBe(false);
    expect(
      resolveTodayCapabilityFromProfile({
        authenticated: true,
        coreProfile: { astro: { birth_date: "1990-01-01" } },
      }),
    ).toBe("light");
  });
});
