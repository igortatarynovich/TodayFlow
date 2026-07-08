import {
  buildInterpretationConfirmPayload,
  interpretationConfirmQuestion,
} from "@/lib/todayInterpretationConfirm";

describe("todayInterpretationConfirm", () => {
  it("builds sphere_feedback payload for post-ritual confirm", () => {
    const payload = buildInterpretationConfirmPayload({
      target: "tarot_impact",
      resonance: "partial",
      headline: "Сегодня — про терпение",
    });
    expect(payload.interpretation_confirm).toBe(true);
    expect(payload.target).toBe("tarot_impact");
    expect(payload.echo).toBe("partial");
    expect(payload.headline_preview).toContain("терпение");
  });

  it("questions per target", () => {
    expect(interpretationConfirmQuestion("tarot_impact")).toContain("про тебя");
    expect(interpretationConfirmQuestion("number_impact")).toContain("Число");
  });
});
