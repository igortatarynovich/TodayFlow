import {
  todayScreenFlowAttributesIndex,
  todayScreenFlowCloseIndex,
  todayScreenFlowInsightIndex,
  todayScreenFlowPracticeIndex,
  todayScreenFlowReadingIndex,
  todayScreenFlowStepCount,
} from "@/components/today/composition/TodayProductScreenFlow";
import { TODAY_SCREEN_FLOW_AXIS } from "@/design-system/primitives/ScreenFlow";

describe("todayScreenFlow story-deck indices", () => {
  it("counts greeting (+symbols) when personal is off", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: false })).toBe(1);
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: false })).toBe(2);
  });

  it("counts full mockup deck with symbols", () => {
    // greeting, energy, symbols, attributes, practice, insight, close
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: true })).toBe(7);
  });

  it("counts deck without symbols", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: true })).toBe(6);
  });

  it("maps practice / insight / close indices", () => {
    expect(todayScreenFlowAttributesIndex(true)).toBe(3);
    expect(todayScreenFlowPracticeIndex(true)).toBe(4);
    expect(todayScreenFlowInsightIndex(true)).toBe(5);
    expect(todayScreenFlowCloseIndex(true)).toBe(6);
    expect(todayScreenFlowReadingIndex(true)).toBe(3);
    expect(todayScreenFlowPracticeIndex(false)).toBe(3);
  });

  it("locks Today axis to x", () => {
    expect(TODAY_SCREEN_FLOW_AXIS).toBe("x");
  });
});
