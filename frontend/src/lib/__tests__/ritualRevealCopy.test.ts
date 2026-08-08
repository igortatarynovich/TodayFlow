import {
  formatRitualTarotPersonalToday,
  pickRitualHookLine,
} from "@/lib/ritualRevealCopy";
import { ritualRevealCtaReady } from "@/lib/ritualRevealCascade";

describe("ritualRevealCopy", () => {
  it("cross-references day number when present", () => {
    expect(
      formatRitualTarotPersonalToday({
        personalLine: "про силу результата без нажима.",
        dayNumber: "8",
        dayNumberTitle: "Управленец",
      }),
    ).toBe("При числе дня 8 (Управленец) эта карта — про силу результата без нажима.");
  });

  it("falls back to personal line without number", () => {
    expect(
      formatRitualTarotPersonalToday({
        personalLine: "День поддерживает то, что выращиваешь.",
        dayNumber: null,
      }),
    ).toBe("День поддерживает то, что выращиваешь.");
  });

  it("picks bridge before personal_angle before meaning", () => {
    expect(
      pickRitualHookLine({
        bridge_to_day: "якорь дня",
        personal_angle: "лично",
        base: { meaning: "база" },
      }),
    ).toBe("якорь дня");
    expect(pickRitualHookLine({ personal_angle: "лично", base: { meaning: "база" } })).toBe("лично");
    expect(pickRitualHookLine({ base: { meaning: "база" } }, "fallback")).toBe("база");
    expect(pickRitualHookLine(null, "fallback")).toBe("fallback");
  });
});

describe("ritualRevealCtaReady", () => {
  it("waits for the deepest available cascade layer", () => {
    expect(
      ritualRevealCtaReady({
        showMeaning: true,
        showContext: false,
        hasMeaning: true,
        hasContext: true,
      }),
    ).toBe(false);
    expect(
      ritualRevealCtaReady({
        showMeaning: true,
        showContext: true,
        hasMeaning: true,
        hasContext: true,
      }),
    ).toBe(true);
    expect(
      ritualRevealCtaReady({
        showMeaning: true,
        showContext: false,
        hasMeaning: true,
        hasContext: false,
      }),
    ).toBe(true);
  });
});
