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

describe("todayScreenFlow six blocks v3.4.1 indices", () => {
  it("welcome-only when not personalized", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: false })).toBe(1);
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: false })).toBe(1);
  });

  it("counts 7 steps with symbols (day + orientation)", () => {
    expect(todayScreenFlowStepCount({ showSymbols: true, showPersonalized: true })).toBe(7);
    const idx = todayHandoffIndices(true);
    expect(idx.day).toBe(0);
    expect(idx.orientation).toBe(1);
    expect(idx.rituals).toBe(2);
    expect(idx.instruction).toBe(3);
    expect(idx.color).toBe(4);
    expect(idx.tasks).toBe(5);
    expect(idx.loop).toBe(6);
    expect(idx.number).toBe(2);
    expect(idx.card).toBe(2);
    expect(idx.close).toBe(6);
  });

  it("counts 6 steps without symbols", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showPersonalized: true })).toBe(6);
    const idx = todayHandoffIndices(false);
    expect(idx.orientation).toBe(1);
    expect(idx.rituals).toBe(-1);
    expect(idx.instruction).toBe(2);
    expect(idx.loop).toBe(5);
  });

  it("maps helpers onto block houses", () => {
    expect(todayScreenFlowSymbolsIndex()).toBe(2);
    expect(todayScreenFlowAttributesIndex(true)).toBe(4);
    expect(todayScreenFlowReadingIndex(true)).toBe(3);
    expect(todayScreenFlowPracticeIndex(true)).toBe(5);
    expect(todayScreenFlowInsightIndex(true)).toBe(6);
    expect(todayScreenFlowCloseIndex(true)).toBe(6);
    expect(todayScreenFlowPracticeIndex(false)).toBe(4);
  });
});
