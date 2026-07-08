import {
  parseProfileView,
  PROFILE_CHART_DEEP_PATH,
  PROFILE_SPHERES_DEEP_PATH,
  PROFILE_V0_PATH,
} from "@/lib/profileRoutes";

describe("profileRoutes", () => {
  it("parses portrait view aliases", () => {
    expect(parseProfileView("v0")).toBe("v0");
    expect(parseProfileView("portrait")).toBe("v0");
    expect(parseProfileView(null)).toBe("quickMap");
  });

  it("exposes canonical deep and v0 paths", () => {
    expect(PROFILE_CHART_DEEP_PATH).toBe("/profile?section=chart#profile-chart");
    expect(PROFILE_SPHERES_DEEP_PATH).toBe("/profile?section=spheres#profile-life-spheres");
    expect(PROFILE_V0_PATH).toBe("/profile?view=v0");
  });
});
