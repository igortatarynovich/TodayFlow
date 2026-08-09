import {
  todayHandoffIndices,
  todayScreenFlowAttributesIndex,
  todayScreenFlowCloseIndex,
  todayScreenFlowInsightIndex,
  todayScreenFlowPracticeIndex,
  todayScreenFlowReadingIndex,
  todayScreenFlowStepCount,
  todayScreenFlowSymbolsIndex,
} from "@/components/today/composition/TodayProductScreenFlow";

describe("todayScreenFlow handoff v3.3 indices", () => {
  it("welcome-only when not personalized", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: false })).toBe(1);
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: false })).toBe(1);
  });

  it("counts 12 steps with symbols", () => {
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: true })).toBe(12);
    const idx = todayHandoffIndices(true);
    expect(idx.welcome).toBe(0);
    expect(idx.priority).toBe(1);
    expect(idx.number).toBe(5);
    expect(idx.card).toBe(6);
    expect(idx.close).toBe(11);
  });

  it("counts 10 steps without symbols", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: true })).toBe(10);
    const idx = todayHandoffIndices(false);
    expect(idx.number).toBe(-1);
    expect(idx.color).toBe(5);
    expect(idx.close).toBe(9);
  });

  it("maps legacy helpers onto handoff houses", () => {
    expect(todayScreenFlowSymbolsIndex()).toBe(5);
    expect(todayScreenFlowAttributesIndex(true)).toBe(7);
    expect(todayScreenFlowReadingIndex(true)).toBe(8);
    expect(todayScreenFlowPracticeIndex(true)).toBe(9);
    expect(todayScreenFlowInsightIndex(true)).toBe(10);
    expect(todayScreenFlowCloseIndex(true)).toBe(11);
    expect(todayScreenFlowPracticeIndex(false)).toBe(7);
  });
});
