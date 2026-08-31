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

describe("todayScreenFlow four surfaces", () => {
  it("guest/general: today + ritual + evening, no my_day", () => {
    expect(todayScreenFlowStepCount({ showSymbols: true, showMyDay: false })).toBe(3);
    const idx = todayHandoffIndices({ showSymbols: true, showMyDay: false });
    expect(idx.today).toBe(0);
    expect(idx.ritual).toBe(1);
    expect(idx.myDay).toBe(-1);
    expect(idx.evening).toBe(2);
    expect(idx.orientation).toBe(-1);
  });

  it("does not collapse to a single step when personalized is false", () => {
    expect(
      todayScreenFlowStepCount({
        showSymbols: true,
        showMyDay: false,
        showPersonalized: false,
      }),
    ).toBe(3);
  });

  it("light/deep with symbols: four steps", () => {
    expect(todayScreenFlowStepCount({ showSymbols: true, showMyDay: true })).toBe(4);
    const idx = todayHandoffIndices({ showSymbols: true, showMyDay: true });
    expect(idx.day).toBe(0);
    expect(idx.rituals).toBe(1);
    expect(idx.instruction).toBe(2);
    expect(idx.color).toBe(2);
    expect(idx.tasks).toBe(2);
    expect(idx.loop).toBe(3);
    expect(idx.close).toBe(3);
  });

  it("without symbols still has today + my_day + evening", () => {
    expect(todayScreenFlowStepCount({ showSymbols: false, showMyDay: true })).toBe(3);
    const idx = todayHandoffIndices({ showSymbols: false, showMyDay: true });
    expect(idx.rituals).toBe(-1);
    expect(idx.myDay).toBe(1);
    expect(idx.evening).toBe(2);
  });

  it("maps helpers onto four-screen houses", () => {
    expect(todayScreenFlowSymbolsIndex()).toBe(1);
    expect(todayScreenFlowAttributesIndex(true)).toBe(2);
    expect(todayScreenFlowReadingIndex(true)).toBe(2);
    expect(todayScreenFlowPracticeIndex(true)).toBe(2);
    expect(todayScreenFlowInsightIndex(true)).toBe(3);
    expect(todayScreenFlowCloseIndex(true)).toBe(3);
    expect(todayScreenFlowPracticeIndex(false)).toBe(1);
    expect(todayScreenFlowCloseIndex(true, false)).toBe(2);
  });

  it("hides evening surface when showEvening is false", () => {
    expect(
      todayScreenFlowStepCount({ showSymbols: true, showMyDay: true, showEvening: false }),
    ).toBe(3);
    const idx = todayHandoffIndices({ showSymbols: true, showMyDay: true, showEvening: false });
    expect(idx.today).toBe(0);
    expect(idx.ritual).toBe(1);
    expect(idx.myDay).toBe(2);
    expect(idx.evening).toBe(-1);
    expect(idx.loop).toBe(-1);
    expect(idx.close).toBe(-1);
  });

  it("helpers respect showEvening false", () => {
    expect(todayScreenFlowReadingIndex(true, true, false)).toBe(2);
    expect(todayScreenFlowPracticeIndex(true, true, false)).toBe(2);
    expect(todayScreenFlowInsightIndex(true, true, false)).toBe(-1);
    expect(todayScreenFlowCloseIndex(true, true, false)).toBe(-1);
    expect(todayScreenFlowAttributesIndex(true, true, false)).toBe(2);
  });

  it("hides evening without myDay when showEvening is false", () => {
    expect(
      todayScreenFlowStepCount({ showSymbols: true, showMyDay: false, showEvening: false }),
    ).toBe(2);
    const idx = todayHandoffIndices({ showSymbols: true, showMyDay: false, showEvening: false });
    expect(idx.today).toBe(0);
    expect(idx.ritual).toBe(1);
    expect(idx.evening).toBe(-1);
  });
});
