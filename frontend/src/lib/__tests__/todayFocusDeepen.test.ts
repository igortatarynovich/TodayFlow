import {
  canOfferFocusDeepen,
  readingSphereChapterId,
  resolveFocusDeepenTarget,
} from "@/lib/todayFocusDeepen";

describe("todayFocusDeepen", () => {
  it("maps morning focus topics to Reading + depth homes", () => {
    expect(resolveFocusDeepenTarget("work", ["career", "money", "full_day"])).toEqual({
      focusTopicId: "work",
      readingSphere: "work",
      depthTopic: "career",
    });
    expect(resolveFocusDeepenTarget("relations", ["love", "family"])).toEqual({
      focusTopicId: "relations",
      readingSphere: "relationships",
      depthTopic: "love",
    });
    expect(resolveFocusDeepenTarget("health", ["full_day"])).toEqual({
      focusTopicId: "health",
      readingSphere: "energy",
      depthTopic: "full_day",
    });
  });

  it("falls back when preferred depth topic is absent from menu", () => {
    expect(resolveFocusDeepenTarget("work", ["money", "full_day"]).depthTopic).toBe("full_day");
    expect(resolveFocusDeepenTarget("work", []).depthTopic).toBeNull();
  });

  it("builds Reading chapter ids for scroll/expand", () => {
    expect(readingSphereChapterId("work")).toBe("sphere-work");
    expect(readingSphereChapterId("sphere-money")).toBe("sphere-money");
  });

  it("offers CTA when Reading or depth menu exists", () => {
    expect(canOfferFocusDeepen({ hasReading: true })).toBe(true);
    expect(canOfferFocusDeepen({ hasReading: false, depthMenuTopics: ["career"] })).toBe(true);
    expect(canOfferFocusDeepen({ hasReading: false, depthMenuTopics: [] })).toBe(false);
  });
});
