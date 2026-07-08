import {
  blockKeyFromEchoTarget,
  buildCompatibilityEchoEvent,
  isCompatibilityDeepBlockKey,
} from "@/lib/compatibilityEcho";

describe("compatibilityEcho", () => {
  it("maps deep targets to block keys", () => {
    expect(blockKeyFromEchoTarget("deep:emotions")).toBe("emotions");
    expect(blockKeyFromEchoTarget("main_thought")).toBeNull();
    expect(isCompatibilityDeepBlockKey("conflicts")).toBe(true);
  });

  it("builds meaning event payload", () => {
    const event = buildCompatibilityEchoEvent(
      { surface: "analyze_dynamics", scenarioId: "love", formatId: "love" },
      "main_thought",
      "partial",
    );
    expect(event.event_type).toBe("compatibility_echo");
    expect(event.event_source).toBe("compatibility");
    expect(event.payload?.target).toBe("main_thought");
    expect(event.payload?.echo).toBe("partial");
  });

  it("builds scenario pass event", () => {
    const event = buildCompatibilityEchoEvent(
      { surface: "hub", scenarioId: "love", formatId: "love" },
      "scenario:love",
      "no",
    );
    expect(event.payload?.target).toBe("scenario:love");
  });
});
