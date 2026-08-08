import { calloutLabelForChapterId } from "@/lib/todayReadingCallout";

describe("calloutLabelForChapterId", () => {
  it("maps sphere domains to life-theme capsules", () => {
    expect(calloutLabelForChapterId("sphere-relationships")).toBe("relations");
    expect(calloutLabelForChapterId("sphere-money")).toBe("money");
    expect(calloutLabelForChapterId("sphere-energy")).toBe("emotions");
    expect(calloutLabelForChapterId("sphere-work")).toBe("thought");
    expect(calloutLabelForChapterId("sphere-work_decisions")).toBe("thought");
  });

  it("defaults non-sphere chapters to help", () => {
    expect(calloutLabelForChapterId("opening")).toBe("help");
    expect(calloutLabelForChapterId("force")).toBe("help");
  });
});
