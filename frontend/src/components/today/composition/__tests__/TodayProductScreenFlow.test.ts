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

describe("todayScreenFlow six blocks v3.4 indices", () => {
  it("welcome-only when not personalized", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: false })).toBe(1);
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: false })).toBe(1);
  });

  it("counts 6 steps with symbols", () => {
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: true })).toBe(6);
    const idx = todayHandoffIndices(true);
    expect(idx.day).toBe(0);
    expect(idx.rituals).toBe(1);
    expect(idx.instruction).toBe(2);
    expect(idx.color).toBe(3);
    expect(idx.tasks).toBe(4);
    expect(idx.loop).toBe(5);
    expect(idx.number).toBe(1);
    expect(idx.card).toBe(1);
    expect(idx.close).toBe(5);
  });

  it("counts 5 steps without symbols", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: true })).toBe(5);
    const idx = todayHandoffIndices(false);
    expect(idx.rituals).toBe(-1);
    expect(idx.instruction).toBe(1);
    expect(idx.loop).toBe(4);
  });

  it("maps helpers onto six-block houses", () => {
    expect(todayScreenFlowSymbolsIndex()).toBe(1);
    expect(todayScreenFlowAttributesIndex(true)).toBe(3);
    expect(todayScreenFlowReadingIndex(true)).toBe(2);
    expect(todayScreenFlowPracticeIndex(true)).toBe(4);
    expect(todayScreenFlowInsightIndex(true)).toBe(5);
    expect(todayScreenFlowCloseIndex(true)).toBe(5);
    expect(todayScreenFlowPracticeIndex(false)).toBe(3);
  });
});
