import type { TodayContractV1 } from "@/lib/todayContract";
import {
  buildDayThesis,
  buildNumberRhythmFacet,
  buildTarotSymbolFacet,
  buildTodayDaySpine,
  SpineRegistry,
} from "@/lib/todayDaySpine";

const contract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День паузы — когда ускорение идёт из тревоги." },
  personal_growth: { development_point: "Замедлиться и услышать себя." },
  domains: {
    relationships: { status: "слушать", opportunity: "глубокие разговоры", risk: "конфликты", action: "Напиши близкому." },
    money_work: { status: "ясность", opportunity: "планирование", risk: "импульс", action: "Одна задача." },
    family: { status: "тишина", opportunity: "разговор", risk: "перегруз", action: "10 минут семье." },
  },
  primary_action: "Сделай одну главную задачу.",
  progress: {},
  generation_id: "test",
};

describe("todayDaySpine", () => {
  it("builds one thesis without repeating in tarot and number facets", () => {
    const spine = buildTodayDaySpine({
      contract,
      morningRitualData: {
        date: "2026-06-23",
        celestial_events: {
          lunar_phase: { name: "Убывающая луна", themes: "отпускание лишнего" },
          personal_transits: [
            {
              id: "pt-1",
              title: "Марс — квадрат — Сатурн",
              story_ru: "Создаёт напряжение, которое просит осознанного выбора.",
            },
          ],
          sky_aspects: [
            {
              id: "sky-1",
              title: "Sun — Square — Moon",
              story_ru: "День подсвечивает разрыв между намерением и настроением.",
            },
          ],
          daily_symbols: {
            totem: { id: "wolf", name: "Волк", emoji: "🐺", story_ru: "Волк — про верность своему ритму." },
          },
        },
      },
      cardId: 12,
      cardName: "Повешенный",
      numerologyValue: "20",
      numerologyMeaning: "Путь жизни",
      ritualComplete: true,
      tarotPicked: true,
    });

    expect(spine.thesis).toMatch(/спеш|пауз|ритм/i);
    expect(spine.thesis.split(/[.!?]/).filter(Boolean)).toHaveLength(1);
    expect(spine.tarotBody).toMatch(/Повешенный|угол зрения/i);
    expect(spine.numberBody).toMatch(/20|терпен/i);
    expect(spine.numberBody).not.toMatch(/Путь жизни/i);
    expect(spine.skyCards.some((c) => c.id === "personal-transit")).toBe(true);
    expect(spine.skyCards.some((c) => c.id === "totem")).toBe(true);
  });

  it("deduplicates overlapping text in registry", () => {
    const registry = new SpineRegistry();
    const first = registry.claim("Иногда пауза — это ход, который меняет траекторию.");
    const second = registry.claim("Иногда пауза — это ход, который меняет направление.");
    expect(first).toBeTruthy();
    expect(second).toBeNull();
  });

  it("builds tarot symbol from bodyRu not leadRu", () => {
    const registry = new SpineRegistry();
    const body = buildTarotSymbolFacet(12, registry);
    expect(body).toMatch(/Повешенный|угол зрения/i);
    expect(body).not.toMatch(/^Иногда пауза — это ход\./);
  });

  it("builds number rhythm for weak numerology meaning", () => {
    const registry = new SpineRegistry();
    const line = buildNumberRhythmFacet("20", "Путь жизни", registry);
    expect(line).toMatch(/20|терпен/i);
    expect(line).not.toMatch(/Путь жизни/i);
  });

  it("adjusts thesis for anxious mood", () => {
    const thesis = buildDayThesis(contract, "anxious");
    expect(thesis).toMatch(/перестаёт спешить/i);
  });
});
