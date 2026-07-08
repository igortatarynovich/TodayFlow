import { resolveTodayRitualPhase, isTodayPersonalized } from "@/lib/todayRitualGate";

describe("todayRitualGate", () => {
  it("starts at tarot_pending", () => {
    expect(resolveTodayRitualPhase({ tarotPickedName: null, numberConfirmed: false })).toBe("tarot_pending");
    expect(isTodayPersonalized({ tarotPickedName: null, numberConfirmed: false })).toBe(false);
  });

  it("moves to number_pending after tarot", () => {
    expect(resolveTodayRitualPhase({ tarotPickedName: "Отшельник", numberConfirmed: false })).toBe("number_pending");
  });

  it("completes after number", () => {
    expect(resolveTodayRitualPhase({ tarotPickedName: "Отшельник", numberConfirmed: true })).toBe("complete");
    expect(isTodayPersonalized({ tarotPickedName: "Отшельник", numberConfirmed: true })).toBe(true);
  });
});
