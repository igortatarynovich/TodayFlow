import { buildDailyFocusModel } from "@/lib/todayDailyFocus";
import { isDailyFocusGuidanceLeak, filterDailyFocusLines } from "@/lib/todayDailyFocusBoundary";
import type { TodayContractV1 } from "@/lib/todayContract";

const minimalContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "день ясности" },
  personal_growth: { development_point: "Точка роста — ясность в общении." },
  domains: {
    relationships: {
      status: "сегодня в отношениях — ясность",
      opportunity: "открытый контакт",
      risk: "догадки",
      action: "одна честная фраза",
    },
    money_work: {
      status: "сегодня в работе — один вектор",
      opportunity: "завершение",
      risk: "распыление",
      action: "один приоритет",
    },
    family: {
      status: "сегодня дома — спокойный тон",
      opportunity: "поддержка",
      risk: "давление",
      action: "тепло без контроля",
    },
  },
  primary_action: "Сделай один шаг",
  progress: {},
  generation_id: "test",
};

describe("PR1 S5 boundary — Daily Focus", () => {
  it("rejects user bad-example guidance phrasing", () => {
    const bad =
      "Сегодня стоит сосредоточиться на разговорах. Если хочешь продвинуть проект — обсуди его до обеда.";
    expect(isDailyFocusGuidanceLeak(bad)).toBe(true);
    expect(filterDailyFocusLines([bad])).toEqual([]);
  });

  it("keeps user good-example descriptive phrasing", () => {
    const good =
      "Сегодня внимание смещается в сторону общения и обмена информацией. Разговоры могут оказаться важнее привычных планов.";
    expect(isDailyFocusGuidanceLeak(good)).toBe(false);
    const model = buildDailyFocusModel(minimalContract, {
      core_message: { body: good },
      daily_focus_id: "communication",
    });
    const joined = [model.title, ...model.lines].join(" ");
    expect(joined).toMatch(/общен|разговор/i);
    expect(joined).not.toMatch(/до обеда/i);
  });

  it("does not surface best_move or do_hint from guide payload", () => {
    const model = buildDailyFocusModel(minimalContract, {
      daily_focus_id: "communication",
      headline: "День про общение",
      core_message: {
        body: "Сегодня внимание смещается в сторону общения.",
        best_move: "Обсуди проект до обеда",
        risk: "Распыление",
      },
      day_engine_brief: {
        anchor_summary: "Сегодня внимание смещается в сторону общения.",
        do_hint: "Сделай один звонок до обеда",
        avoid_hint: "Не бери новые задачи",
      },
    });
    const joined = [model.title, ...model.lines].join(" ");
    expect(joined).not.toMatch(/до обеда/i);
    expect(joined).not.toMatch(/один звонок/i);
    expect(joined).not.toMatch(/лучший ход/i);
    expect(joined).toMatch(/общен/i);
  });

  it("uses day_engine_brief anchor when core_message is guidance-only", () => {
    const model = buildDailyFocusModel(minimalContract, {
      core_message: {
        body: "Сосредоточься на разговорах. Обсуди проект до обеда.",
        best_move: "Позвони коллеге",
      },
      day_engine_brief: {
        anchor_summary:
          "Сегодня внимание смещается в сторону общения и обмена информацией.",
      },
    });
    expect(model.lines[0]).toMatch(/общен/i);
    expect(model.lines.join(" ")).not.toMatch(/обсуди/i);
  });

  it("prefers day_story over guide payload when authoritative", () => {
    const contract: TodayContractV1 = {
      ...minimalContract,
      day_story: {
        contract_version: "day_story_v1",
        theme: "Один фокус без суеты.",
        direction: "Сегодня выигрывает ясность одного выбора.",
        story: "Утром лучше не распыляться. Выбери одну линию и держи её до вечера.",
      },
    };
    const model = buildDailyFocusModel(contract, {
      headline: "Чужой guide headline",
      core_message: { body: "Чужой guide body про обсуждение до обеда." },
    });
    expect(model.dailyFocusId).toBe("day_story_v1");
    expect(model.title).toMatch(/один фокус/i);
    expect(model.lines.join(" ")).toMatch(/ясность|линию/i);
    expect(model.title).not.toMatch(/чужой guide/i);
  });
});
