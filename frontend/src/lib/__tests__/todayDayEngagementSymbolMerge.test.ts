import { createEmptyDayEngagement, mergeEngagementWithDaySymbolState } from "@/lib/todayDayEngagement";

describe("mergeEngagementWithDaySymbolState", () => {
  it("hydrates card + number from server reveal", () => {
    const local = createEmptyDayEngagement();
    const merged = mergeEngagementWithDaySymbolState(
      local,
      {
        card: { revealed: true, id: 8, name: "Сила" },
        number: { revealed: true },
      },
      () => "Сила",
    );
    expect(merged.tarotPickedId).toBe(8);
    expect(merged.tarotPickedName).toBe("Сила");
    expect(merged.numberConfirmed).toBe(true);
  });

  it("resolves name from helper when server omits name", () => {
    const local = createEmptyDayEngagement();
    const merged = mergeEngagementWithDaySymbolState(
      local,
      { card: { revealed: true, id: 0, name: null }, number: { revealed: false } },
      (id) => (id === 0 ? "Шут" : null),
    );
    expect(merged.tarotPickedName).toBe("Шут");
    expect(merged.numberConfirmed).toBe(false);
  });

  it("does not clear local picks when server has nothing revealed", () => {
    const local = {
      ...createEmptyDayEngagement(),
      tarotPickedId: 3,
      tarotPickedName: "Императрица",
      numberConfirmed: true,
    };
    const merged = mergeEngagementWithDaySymbolState(local, {
      card: { revealed: false },
      number: { revealed: false },
    });
    expect(merged.tarotPickedId).toBe(3);
    expect(merged.tarotPickedName).toBe("Императрица");
    expect(merged.numberConfirmed).toBe(true);
  });
});
