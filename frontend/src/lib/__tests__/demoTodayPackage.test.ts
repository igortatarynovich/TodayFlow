import { buildGuestTodayPackage } from "@/lib/demoTodayPackage";
import type { ColdState } from "@/lib/coldStart";

const FIXTURE_STATE: ColdState = {
  id: "test_state",
  keyPhrase: "желание ясности",
  explanation: "Сегодня может быть сильнее запрос на ясность.",
  microAction: {
    instruction: "Обрати внимание на то, где ты ищешь ясность",
    completionMessage: "Ты начал замечать понимание",
  },
  hookMessage: "Завтра продолжим",
};

describe("buildGuestTodayPackage", () => {
  it("maps cold state into theme, action, and guest progress", () => {
    const pkg = buildGuestTodayPackage(FIXTURE_STATE);

    expect(pkg.coldStateId).toBe("test_state");
    expect(pkg.theme.headline).toContain("Желание ясности");
    expect(pkg.theme.body).toBe(FIXTURE_STATE.explanation);
    expect(pkg.action.primary).toBe(FIXTURE_STATE.microAction.instruction);
    expect(pkg.progress.statusLabel).toMatch(/Демо/);
    expect(pkg.insight.body).toMatch(/без даты рождения/i);
  });

  it("capitalizes theme headline from key phrase", () => {
    const pkg = buildGuestTodayPackage({
      ...FIXTURE_STATE,
      keyPhrase: "рассеянное внимание",
    });
    expect(pkg.theme.headline).toContain("Рассеянное внимание");
  });
});
