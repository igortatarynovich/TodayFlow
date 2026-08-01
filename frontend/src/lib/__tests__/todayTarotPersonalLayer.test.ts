import { composeTarotPersonalLayer } from "@/lib/todayTarotPersonalLayer";
import { mergeTarotTrapIntoDailyFocus, type DailyFocusModel } from "@/lib/todayDailyFocus";

describe("composeTarotPersonalLayer", () => {
  it("folds daily focus + decision style with BE card meaning", () => {
    const layer = composeTarotPersonalLayer({
      cardId: 12,
      cardMeaning: "пауза меняет угол зрения, а не саму ситуацию.",
      dailyFocusTitle: "День про короткие договорённости и ясный тон.",
      dailyFocusId: "communication",
      decisionStyle: "Сначала чувствую, потом решаю",
      helpsFirst: "Тихая пауза перед ответом",
    });

    expect(layer).not.toBeNull();
    expect(layer!.cardName).toBe("Повешенный");
    expect(layer!.personalized).toBe(true);
    expect(layer!.trapLine).toMatch(/стиле|Повешенный|угол зрения/i);
    expect(layer!.sceneBody).toMatch(/договорённост/i);
    expect(layer!.sceneBody).toMatch(/Повешенный|пауза|угол/i);
    expect(layer!.headline).toMatch(/договорённост/i);
  });

  it("returns name-anchored copy without inventing FE prose when meaning missing", () => {
    const layer = composeTarotPersonalLayer({ cardId: 12 });
    expect(layer).not.toBeNull();
    expect(layer!.personalized).toBe(false);
    expect(layer!.trapLine).toMatch(/Повешенный/);
    expect(layer!.sceneBody).toMatch(/Повешенный/);
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
      "«Повешенный» сегодня задаёт другой угол зрения.",
    );
    expect(merged.lines).toHaveLength(2);
    expect(merged.lines[1]).toMatch(/Повешенный/i);
  });
});
