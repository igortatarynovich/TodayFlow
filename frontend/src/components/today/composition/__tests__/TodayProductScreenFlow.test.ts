import {
  todayScreenFlowReadingIndex,
  todayScreenFlowStepCount,
} from "@/components/today/composition/TodayProductScreenFlow";
import { TODAY_SCREEN_FLOW_AXIS } from "@/design-system/primitives/ScreenFlow";

describe("todayScreenFlow Phase 2b indices", () => {
  it("counts Glance+Plot only when symbols and personal are off", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: false })).toBe(2);
  });

  it("adds Symbols and three personal acts when both on", () => {
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: true })).toBe(6);
  });

  it("shifts Reading left when Symbols omitted", () => {
    expect(todayScreenFlowReadingIndex(true)).toBe(3);
    expect(todayScreenFlowReadingIndex(false)).toBe(2);
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: true })).toBe(5);
  });

  it("locks Today axis to x", () => {
    expect(TODAY_SCREEN_FLOW_AXIS).toBe("x");
  });
});
