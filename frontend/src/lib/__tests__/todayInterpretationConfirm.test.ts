import {
  buildInterpretationConfirmPayload,
  interpretationConfirmQuestion,
  proximityOptionsForTarget,
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

  it("one universal proximity question; options differ per target", () => {
    // Post-ritual confirm moved to a single proximity question — learning
    // signal without test-like UX; per-target meaning lives in the options.
    expect(interpretationConfirmQuestion("tarot_impact")).toBe("Что сейчас ближе?");
    expect(interpretationConfirmQuestion("number_impact")).toBe("Что сейчас ближе?");
    expect(proximityOptionsForTarget("tarot_impact").map((o) => o.label)).toContain("Сделать первый шаг");
    expect(proximityOptionsForTarget("number_impact").map((o) => o.label)).toContain("Замечаю закономерность");
  });
});
