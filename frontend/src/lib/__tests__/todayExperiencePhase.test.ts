import { todayExperiencePhase } from "@/lib/todayExperiencePhase";

const baseSnap = {
  dayOpened: true,
  tarotContinueAck: true,
  numberRevealed: true,
};

describe("todayExperiencePhase PR1 spine", () => {
  it("starts at entry when day not opened (S0)", () => {
    expect(
      todayExperiencePhase({
        dayOpened: false,
        tarotContinueAck: false,
        numberRevealed: false,
      }),
    ).toBe("entry");
  });

  it("moves S0 → tarot → number → synthesis", () => {
    expect(
      todayExperiencePhase({
        dayOpened: true,
        tarotContinueAck: false,
        numberRevealed: false,
      }),
    ).toBe("tarot_reveal");

    expect(
      todayExperiencePhase({
        dayOpened: true,
        tarotContinueAck: true,
        numberRevealed: false,
      }),
    ).toBe("number_reveal");

    expect(todayExperiencePhase(baseSnap)).toBe("day_synthesis");
  });
});
