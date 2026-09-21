import {
  formatRitualTarotPersonalToday,
  pickRitualCardLens,
  pickRitualHookLine,
  pickRitualNumberLens,
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

  it("omits number lens without Personal Day capability and never uses catalog as lens", () => {
    const hook = {
      bridge_to_day: "замедляет давление в этом конфликте",
      personal_angle: "лично",
      base: { meaning: "база" },
    };
    expect(pickRitualNumberLens(hook, false)).toBeNull();
    expect(pickRitualNumberLens({ base: { meaning: "база" } }, true)).toBeNull();
  });

  it("uses Personal×number angle for T2.lens_number and ignores Global chorus", () => {
    expect(
      pickRitualNumberLens(
        {
          bridge_to_day: "замедляет давление в этом конфликте",
          personal_angle: "Это число окрашивает уже собранный личный день.",
          base: { meaning: "Семёрка — пауза перед решением." },
        },
        true,
      ),
    ).toBe("Это число окрашивает уже собранный личный день.");
  });

  it("omits Global chorus packaged as number lens even with persist", () => {
    const chorus = "замедляет давление в этом конфликте";
    expect(
      pickRitualNumberLens(
        {
          bridge_to_day: chorus,
          personal_angle: chorus,
          base: { meaning: "Семёрка — пауза перед решением." },
        },
        true,
      ),
    ).toBeNull();
    expect(
      pickRitualNumberLens(
        {
          bridge_to_day: chorus,
          base: { meaning: "Семёрка — пауза перед решением." },
        },
        true,
      ),
    ).toBeNull();
    expect(
      pickRitualNumberLens(
        {
          bridge_to_day: "сначала понять; потом говорить",
          personal_angle: "omit",
          base: { meaning: "Семёрка — пауза перед решением." },
        },
        true,
      ),
    ).toBeNull();
  });

  it("does not invert catalog meaning or omit-token into a number lens", () => {
    expect(
      pickRitualNumberLens(
        {
          personal_angle: "Семёрка — пауза перед решением.",
          base: { meaning: "Семёрка — пауза перед решением." },
        },
        true,
      ),
    ).toBeNull();
    expect(pickRitualNumberLens({ personal_angle: "omit" }, true)).toBeNull();
    expect(pickRitualNumberLens({ personal_angle: "лично" }, false)).toBeNull();
  });

  it("uses Personal×card angle for T2.lens_card and ignores Global chorus", () => {
    expect(
      pickRitualCardLens(
        {
          bridge_to_day: "архетип описывает сегодняшний конфликт",
          personal_angle: "Эта карта окрашивает уже собранный личный день.",
          base: { meaning: "Сила — внутренняя опора." },
        },
        true,
      ),
    ).toBe("Эта карта окрашивает уже собранный личный день.");
  });

  it("omits Global chorus packaged as card lens even with persist", () => {
    const chorus = "архетип описывает сегодняшний конфликт";
    expect(
      pickRitualCardLens(
        {
          bridge_to_day: chorus,
          personal_angle: chorus,
          base: { meaning: "Сила — внутренняя опора." },
        },
        true,
      ),
    ).toBeNull();
    expect(
      pickRitualCardLens(
        {
          bridge_to_day: chorus,
          base: { meaning: "Сила — внутренняя опора." },
        },
        true,
      ),
    ).toBeNull();
  });

  it("does not invert catalog meaning or omit-token into a card lens", () => {
    expect(
      pickRitualCardLens(
        { personal_angle: "Сила — внутренняя опора.", base: { meaning: "Сила — внутренняя опора." } },
        true,
      ),
    ).toBeNull();
    expect(pickRitualCardLens({ personal_angle: "omit" }, true)).toBeNull();
    expect(pickRitualCardLens({ personal_angle: "лично" }, false)).toBeNull();
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
