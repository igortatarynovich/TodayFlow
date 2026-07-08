import { isExperienceSpineComplete } from "@/lib/todayExperienceSpine";

describe("isExperienceSpineComplete", () => {
  it("requires tarot ack and number without mood", () => {
    expect(
      isExperienceSpineComplete({
        tarotMainId: 3,
        tarotContinueAck: true,
        numberRevealed: true,
      }),
    ).toBe(true);

    expect(
      isExperienceSpineComplete({
        tarotMainId: 3,
        tarotContinueAck: false,
        numberRevealed: true,
      }),
    ).toBe(false);
  });
});
