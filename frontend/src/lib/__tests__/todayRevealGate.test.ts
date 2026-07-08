import {
  canShowDayNumber,
  canShowTarotCardName,
  canShowTodaySynthesis,
} from "@/lib/todayRevealGate";

describe("todayRevealGate", () => {
  it("hides card name until pick commits", () => {
    expect(canShowTarotCardName(null)).toBe(false);
    expect(canShowTarotCardName(16)).toBe(true);
  });

  it("hides day number until number reveal completes", () => {
    expect(canShowDayNumber(false)).toBe(false);
    expect(canShowDayNumber(true)).toBe(true);
  });

  it("unlocks synthesis only after both ritual reveals", () => {
    expect(canShowTodaySynthesis({ tarotContinueAck: false, numberRevealed: false })).toBe(false);
    expect(canShowTodaySynthesis({ tarotContinueAck: true, numberRevealed: false })).toBe(false);
    expect(canShowTodaySynthesis({ tarotContinueAck: true, numberRevealed: true })).toBe(true);
  });
});
