import { composeTarotPersonalLayer } from "@/lib/todayTarotPersonalLayer";
import { mergeTarotTrapIntoDailyFocus, type DailyFocusModel } from "@/lib/todayDailyFocus";

describe("composeTarotPersonalLayer", () => {
  it("uses card risk as trap and folds daily focus + decision style into one scene", () => {
    const layer = composeTarotPersonalLayer({
      cardId: 12,
      dailyFocusTitle: "День про короткие договорённости и ясный тон.",
      dailyFocusId: "communication",
      decisionStyle: "Сначала чувствую, потом решаю",
      helpsFirst: "Тихая пауза перед ответом",
    });

    expect(layer).not.toBeNull();
    expect(layer!.cardName).toBe("Повешенный");
    expect(layer!.personalized).toBe(true);
    expect(layer!.trapLine).toMatch(/стиле|Повешенный|застревание|жертве/i);
    expect(layer!.sceneBody).toMatch(/договорённост/i);
    expect(layer!.sceneBody).toMatch(/Повешенный|пауза|застревание/i);
    expect(layer!.sceneBody).toMatch(/паузу|поворот/i);
    expect(layer!.headline).toMatch(/договорённост/i);
  });

  it("still returns card-quality copy without profile (personalized false)", () => {
    const layer = composeTarotPersonalLayer({ cardId: 12 });
    expect(layer).not.toBeNull();
    expect(layer!.personalized).toBe(false);
    expect(layer!.trapLine).toMatch(/Повешенный|застревание/i);
    expect(layer!.sceneBody.length).toBeGreaterThan(40);
  });

  it("returns null for unknown card id", () => {
    expect(composeTarotPersonalLayer({ cardId: 999 })).toBeNull();
  });
});

describe("mergeTarotTrapIntoDailyFocus", () => {
  it("appends trap as last line inside focus, not a separate block", () => {
    const focus: DailyFocusModel = {
      dailyFocusId: "communication",
      title: "О чём этот день.",
      lines: ["Тема — ясный тон в разговорах."],
    };
    const merged = mergeTarotTrapIntoDailyFocus(
      focus,
      "Ловушка «Повешенный»: застревание в жертве и ожидании спасения.",
    );
    expect(merged.lines).toHaveLength(2);
    expect(merged.lines[1]).toMatch(/Повешенный|застревание/i);
  });
});
