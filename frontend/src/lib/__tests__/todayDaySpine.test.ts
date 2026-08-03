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
    work: { status: "ясность", opportunity: "планирование", risk: "импульс", action: "Одна задача." },
    money: { status: "ясность", opportunity: "планирование", risk: "импульс", action: "Одна задача." },
    relationships: { status: "слушать", opportunity: "глубокие разговоры", risk: "конфликты", action: "Напиши близкому." },
    energy: { status: "тишина", opportunity: "разговор", risk: "перегруз", action: "10 минут семье." },
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
      numerologyValue: "2",
      numerologyMeaning: "Путь жизни",
      ritualComplete: true,
      tarotPicked: true,
    });

    expect(spine.thesis).toMatch(/спеш|пауз|ритм/i);
    expect(spine.thesis.split(/[.!?]/).filter(Boolean)).toHaveLength(1);
    expect(spine.tarotBody).toMatch(/Повешенный/);
    expect(spine.numberBody).toMatch(/баланс|договорённ/i);
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

  it("builds tarot symbol from name label only (no FE prose bank)", () => {
    const registry = new SpineRegistry();
    const body = buildTarotSymbolFacet(12, registry);
    expect(body).toMatch(/Повешенный/);
    expect(body).toMatch(/архетип дня/i);
  });

  it("builds number rhythm for weak numerology meaning from number_base", () => {
    const registry = new SpineRegistry();
    const line = buildNumberRhythmFacet("2", "Путь жизни", registry);
    expect(line).toMatch(/баланс|договорённ/i);
    expect(line).not.toMatch(/Путь жизни/i);
  });

  it("does not invent rhythm for bogus value 20", () => {
    const registry = new SpineRegistry();
    const line = buildNumberRhythmFacet("20", "Путь жизни", registry);
    expect(line).toBeNull();
  });

  it("adjusts thesis for anxious mood", () => {
    const thesis = buildDayThesis(contract, "anxious");
    expect(thesis).toMatch(/перестаёт спешить/i);
  });

  it("prefers day_thesis label over mood heuristics", () => {
    const withThesis: TodayContractV1 = {
      ...contract,
      day_story: {
        day_thesis: {
          family: "clarity",
          variant: "clarity_returns_after_delay",
          mode: "transition",
          label_ru: "День возвращения ясности",
          driver_ids: ["merc-direct"],
          composition_ids: [],
        },
      },
    };
    const thesis = buildDayThesis(withThesis, "anxious");
    expect(thesis).toMatch(/возвращения ясности/i);
    expect(thesis).not.toMatch(/перестаёт спешить/i);
  });

  it("prefers ready day_scenario conflict over registry day_thesis slogan", () => {
    const withScenario: TodayContractV1 = {
      ...contract,
      day_story: {
        day_thesis: {
          family: "truth",
          variant: "truth_without_filter",
          mode: "pressure",
          label_ru: "Прямота без фильтра",
          driver_ids: ["moon-pisces"],
          composition_ids: [],
        },
        day_scenario: {
          ready: true,
          runtime_sot: true,
          generation_source: "native_llm_c1",
          conflict: {
            short_name: "Сказать правду в переписке, не сгладить «нормально»",
          },
          scenes: [
            {
              scene_id: "scene.communication",
              sphere: "communication",
              what_happens: "Сообщение просит ответа, а хочется закрыться.",
            },
          ],
        },
      },
    };
    const thesis = buildDayThesis(withScenario, "anxious");
    expect(thesis).toMatch(/переписке/i);
    expect(thesis).not.toMatch(/Прямота без фильтра/i);
  });

  it("suppresses ritual unlock hint when day_scenario is ready", () => {
    const withScenario: TodayContractV1 = {
      ...contract,
      day_story: {
        day_scenario: {
          ready: true,
          runtime_sot: true,
          conflict: { short_name: "Пауза перед ответом" },
          scenes: [{ scene_id: "scene.communication", what_happens: "…" }],
          props: { affirmations: [{ text: "Я отвечаю коротко и честно." }] },
        },
      },
    };
    const spine = buildTodayDaySpine({
      contract: withScenario,
      morningRitualData: null,
      cardId: null,
      cardName: null,
      numerologyValue: null,
      numerologyMeaning: null,
      ritualComplete: false,
    });
    expect(spine.ritualUnlockHint).toBeNull();
    expect(spine.themeShort).toMatch(/Пауза перед ответом/i);
  });
});
