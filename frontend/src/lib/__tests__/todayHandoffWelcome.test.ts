import { buildHandoffWelcomeGlass } from "@/lib/todayHandoffWelcome";

describe("buildHandoffWelcomeGlass", () => {
  it("maps visual_mode to mood pills and composes lunar reason", () => {
    const glass = buildHandoffWelcomeGlass({
      visualMode: "clarity",
      lunarName: "Убывающая Луна",
      lunarThemes: "снижает импульсивность.",
      activityTags: ["Планирование", "Финансы", "Разговоры", "Extra"],
    });
    expect(glass.moodPills).toEqual(["Ясная", "Собранная"]);
    expect(glass.reasonLine).toMatch(/Убывающая Луна/);
    expect(glass.reasonLine).toMatch(/импульсивность/i);
    expect(glass.activityTags).toEqual(["Планирование", "Финансы", "Разговоры"]);
  });

  it("honest-omits when signals missing", () => {
    const glass = buildHandoffWelcomeGlass({});
    expect(glass.moodPills).toEqual([]);
    expect(glass.reasonLine).toBeNull();
    expect(glass.activityTags).toEqual([]);
  });
});
