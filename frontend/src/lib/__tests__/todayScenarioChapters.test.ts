/** Phase C2 — scenario story chapters tests. */

import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodayDayNarrative } from "@/lib/todayDayNarrative";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import {
  buildScenarioStoryChapters,
  isDayScenarioReadyForChapters,
} from "@/lib/todayScenarioChapters";

const baseContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День коротких договорённостей." },
  personal_growth: { development_point: "Не торопить ответ." },
  domains: {
    relationships: {
      status: "",
      opportunity: "Одно короткое сообщение.",
      risk: "",
      action: "",
      evidence_status: "present",
    },
    money_work: {
      status: "",
      opportunity: "",
      risk: "",
      action: "",
      evidence_status: "absent",
    },
    family: {
      status: "",
      opportunity: "",
      risk: "",
      action: "",
      evidence_status: "absent",
    },
  },
  primary_action: "Закрой одну важную вещь до обеда.",
  progress: {},
  generation_id: "t",
};

const storyStub = {
  pulse: "pulse",
  hero: { themeHeadline: "Точность", themeShort: "Точность" },
  skyCards: [],
  colorGuide: null,
  tarotImpact: null,
  numberImpact: null,
  sphereFocus: { cards: [], neutralNote: "" },
} as unknown as TodayDayStoryViewModel;

function scenarioContract(): TodayContractV1 {
  return {
    ...baseContract,
    day_story: {
      contract_version: "day_story_v1",
      interpretation_status: "ok",
      theme: "Прояснение против сглаживания",
      primary_conflict: "Прояснение против сглаживания",
      events_lead: "Луна вошла в Рыбы. Меркурий разворачивается в директ.",
      expect: "projected expect",
      trap: "projected trap",
      do: ["projected do"],
      avoid: ["projected avoid"],
      vibe_closing: "К вечеру яснее, где сказали точно.",
      evening_closure: "Если удержали прояснение — день закрывается спокойнее.",
      talisman: {
        color: "Лазурь",
        note: "Держит ясность в коротких решениях.",
        avoid_color: "кислотный жёлтый",
        avoid_why: "Разгоняет спешку.",
      },
      practice_recommendation: {
        kind: "affirmation",
        text: "Я могу сказать коротко и остаться в контакте.",
        reason: "Компенсирует сглаживание.",
      },
      interpretive_chorus: {
        astrology_lead: "Луна в Рыбах",
        astrology_meaning: "Эмоции сильнее логики.",
        day_card: {
          named: "Карта дня — Отшельник",
          role: "Архетип паузы перед ответом.",
        },
        day_number: {
          named: "Число дня — 7",
          for_conflict: "Сначала понять, потом говорить.",
        },
        natal_lead: "Личная чувствительность усиливает соблазн сгладить.",
        parallel_forecast_forbidden: true,
      },
      day_scenario: {
        runtime_sot: true,
        ready: true,
        generation_source: "native_llm_c1",
        conflict: {
          short_name: "Прояснение против сглаживания",
          why_arose: "Луна в Рыбах и Меркурий direct собирают одну линию.",
          why_personal: "Привычка сглаживать делает конфликт узнаваемым.",
          opposing_forces: { a: "сгладить ради тишины", b: "сказать коротко и честно" },
        },
        scenes: [
          {
            scene_id: "scene.relationships",
            sphere: "relationships",
            sphere_label_ru: "Отношения",
            role_in_story: "primary",
            what_happens: "В отношениях проявляется тот же сюжет.",
            opportunity: "Одно короткое сообщение вместо длинного оправдания.",
            trap: "Согласиться сразу, чтобы не тревожить.",
            recommended_action: "Написать черновик и отправить после паузы.",
            do_not: "Сглаживать смысл ради мгновенного мира.",
            domestic_example: "Ответ близкому: сначала смысл, потом скорость.",
          },
          {
            scene_id: "scene.work_decisions",
            sphere: "work_decisions",
            sphere_label_ru: "Работа и решения",
            role_in_story: "support",
            what_happens: "В работе тот же конфликт точности.",
            opportunity: "Закрыть одну задачу ясным решением.",
            trap: "Откладывать, чтобы никого не задеть.",
            recommended_action: "Одно письмо с точной формулировкой.",
            do_not: "Размывать ответ общими фразами.",
            domestic_example: "Письмо коллеге: один абзац, один запрос.",
          },
        ],
        props: {
          color: { name: "Лазурь", link_to_conflict: "Держит ясность", origin_scene_id: "scene.relationships" },
          goals: [{ text: "Одно точное сообщение до обеда.", origin_scene_id: "scene.relationships" }],
        },
      },
    },
  };
}

describe("isDayScenarioReadyForChapters", () => {
  it("requires conflict + scenes and rejects unavailable", () => {
    expect(isDayScenarioReadyForChapters(scenarioContract())).toBe(true);
    const unavailable = scenarioContract();
    unavailable.day_story!.interpretation_status = "unavailable";
    expect(isDayScenarioReadyForChapters(unavailable)).toBe(false);
    const empty = scenarioContract();
    empty.day_story!.day_scenario!.scenes = [];
    expect(isDayScenarioReadyForChapters(empty)).toBe(false);
  });
});

describe("buildScenarioStoryChapters", () => {
  it("builds five product chapters from scenario + chorus", () => {
    const chapters = buildScenarioStoryChapters({ contract: scenarioContract() });
    expect(chapters).toBeTruthy();
    const ids = chapters!.map((c) => c.id);
    expect(ids).toEqual(["opening", "chorus", "scenes", "supports", "vibe"]);
    expect(chapters!.find((c) => c.id === "opening")?.kicker).toBe("Что изменилось сегодня");
    expect(chapters!.find((c) => c.id === "chorus")?.kicker).toBe("Почему именно так");
    expect(chapters!.find((c) => c.id === "scenes")?.kicker).toBe("Где это проявится");
    expect(chapters!.find((c) => c.id === "supports")?.kicker).toBe("Что поможет пройти день");
    expect(chapters!.find((c) => c.id === "vibe")?.kicker).toBe("Чем закончится день");
    const scenes = chapters!.find((c) => c.id === "scenes")!;
    expect(scenes.dual?.strengthen.join(" ")).toMatch(/короткое сообщение/i);
    expect(scenes.dual?.soften.join(" ")).toMatch(/согласиться/i);
    const supports = chapters!.find((c) => c.id === "supports")!;
    expect([supports.lead, ...supports.paragraphs].join(" ")).toMatch(/Лазурь|черновик/i);
  });

  it("does not repeat force-paste opportunity/trap under every sphere", () => {
    const c = scenarioContract();
    const scenes = c.day_story!.day_scenario!.scenes!;
    scenes[0]!.opportunity = "Шанс выбрать «сказать прямо» именно здесь — один конкретный жест.";
    scenes[0]!.trap = "Ловушка — скатиться в «сгладить» и сделать вид, что выбора не было.";
    scenes[0]!.what_happens = "В сфере «Отношения» тот же выбор — «сгладить» или «сказать прямо».";
    scenes[1]!.opportunity = scenes[0]!.opportunity;
    scenes[1]!.trap = scenes[0]!.trap;
    scenes[1]!.what_happens = "В сфере «Работа» тот же выбор — «сгладить» или «сказать прямо».";
    const chapters = buildScenarioStoryChapters({ contract: c });
    const block = chapters!.find((ch) => ch.id === "scenes")!;
    const text = [block.lead, ...block.paragraphs, ...(block.dual?.strengthen ?? []), ...(block.dual?.soften ?? [])].join(
      "\n",
    );
    expect(text).not.toMatch(/тот же выбор — «/);
    expect(text).not.toMatch(/Шанс выбрать «/);
    expect(text).not.toMatch(/— возможность:/);
    expect(text).toMatch(/Ответ близкому|Письмо коллеге/i);
  });

  it("does not invent chapters when scenario missing", () => {
    expect(
      buildScenarioStoryChapters({
        contract: {
          ...baseContract,
          day_story: {
            contract_version: "day_story_v1",
            theme: "X",
            expect: "legacy only",
            trap: "legacy",
            do: ["a", "b"],
          },
        },
      }),
    ).toBeNull();
  });
});

describe("buildTodayDayNarrative C2 preference", () => {
  it("prefers scenario chapters over Day Map when scenario ready", () => {
    const narrative = buildTodayDayNarrative({
      contract: scenarioContract(),
      story: storyStub,
    });
    expect(narrative.composition).toBe("scenario_chapters");
    expect(narrative.chapters.map((c) => c.id)).toEqual([
      "opening",
      "chorus",
      "scenes",
      "supports",
      "vibe",
    ]);
    expect(narrative.chapters.find((c) => c.id === "force")).toBeUndefined();
    expect(narrative.chapters.find((c) => c.id === "opening")?.kicker).toMatch(/изменилось/i);
  });

  it("keeps revealed card and number in scenario chapters after open", () => {
    const chapters = buildScenarioStoryChapters({
      contract: scenarioContract(),
      tarotImpact: {
        title: "Сила",
        headline: "Мягкая сила без давления",
        body: "Держи темп, не форсируй разговор.",
      },
      numberImpact: {
        title: "Число 4",
        headline: "Ритм дня",
        body: "Короткие циклы и одна опора.",
      },
    });
    const symbols = chapters?.find((c) => c.id === "symbols");
    expect(symbols?.kicker).toMatch(/карта и число/i);
    const blob = [symbols?.lead, ...(symbols?.paragraphs ?? [])].join(" ");
    expect(blob).toMatch(/Сила/);
    expect(blob).toMatch(/Число 4|4/);
    expect(blob).toMatch(/Короткие циклы/);
  });

  it("drops calendar DOY from opening (date lives in greeting chrome)", () => {
    const base = scenarioContract();
    const ds = base.day_story!;
    const chapters = buildScenarioStoryChapters({
      contract: {
        ...base,
        day_story: {
          ...ds,
          events_lead: "Календарный день 2026-07-28 — 209-й день года.",
          day_scenario: {
            ...ds.day_scenario!,
            conflict: {
              ...ds.day_scenario!.conflict!,
              why_arose: "Календарный день 2026-07-28 — 209-й день года.",
            },
          },
        },
      },
    });
    const opening = chapters?.find((c) => c.id === "opening");
    const blob = [opening?.lead, ...(opening?.paragraphs ?? [])].join(" ");
    expect(blob).not.toMatch(/календарн/i);
    expect(blob).not.toMatch(/209-й день года/i);
  });

  it("keeps Day Map path when scenario absent", () => {
    const narrative = buildTodayDayNarrative({
      contract: {
        ...baseContract,
        day_story: {
          contract_version: "day_story_v1",
          theme: "Точность важнее объёма",
          events_lead: "Меркурий держит тон коротких договорённостей.",
          expect: "Короткий контакт сегодня работает лучше долгих объяснений.",
          trap: "Домашние обязательства лучше не раздувать.",
          do: ["Одно точное сообщение", "Пауза перед ответом"],
          avoid: ["Длинные разборы на бегу"],
          today_move: "Закрой одну важную вещь до обеда.",
        },
      },
      story: storyStub,
    });
    expect(narrative.composition).toBe("day_map");
    expect(narrative.chapters.map((c) => c.id)).toContain("force");
    expect(narrative.chapters.map((c) => c.id)).not.toContain("scenes");
  });
});
