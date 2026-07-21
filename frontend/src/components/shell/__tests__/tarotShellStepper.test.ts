import { tarotShellStepFromPath } from "@/components/shell/tarotShellStepper";

describe("tarotShellStepFromPath PR-2 rail gating", () => {
  it("hub path is step -1 (no rail)", () => {
    expect(tarotShellStepFromPath("/tarot")).toBe(-1);
  });

  it("funnel paths are >= 0 (rail allowed)", () => {
    expect(tarotShellStepFromPath("/tarot/question")).toBeGreaterThanOrEqual(0);
    expect(tarotShellStepFromPath("/tarot/spread/abc")).toBeGreaterThanOrEqual(0);
    expect(tarotShellStepFromPath("/tarot/result")).toBeGreaterThanOrEqual(0);
  });
});
