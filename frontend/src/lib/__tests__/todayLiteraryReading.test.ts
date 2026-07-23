import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import { buildTodayLiteraryReading, pickSoftWhyLine } from "@/lib/todayLiteraryReading";

const contract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День коротких договорённостей." },
  personal_growth: { development_point: "Не торопить ответ." },
  domains: {
    relationships: {
      status: "",
      opportunity: "Одно короткое сообщение иногда меняет больше длинного разговора.",
      risk: "",
      action: "",
    },
    money_work: {
      status: "",
      opportunity: "Одно маленькое улучшение в процессе важнее попытки разгрести всё.",
      risk: "",
      action: "",
    },
    family: {
      status: "",
      opportunity: "",
      risk: "Лишние домашние обязательства сегодня легко перегружают.",
      action: "Оставь минимум — без чувства вины.",
    },
  },
  primary_action: "Если успеешь закрыть одну важную вещь до обеда, остаток дня пойдёт легче.",
  progress: {},
  generation_id: "t",
  day_story: {
    contract_version: "day_story_v1",
    theme: "Точность важнее объёма",
    direction: "Многое решается не количеством слов, а их точностью.",
    story:
      "Сегодня многое решается не количеством слов, а их точностью. Иногда одно короткое сообщение меняет больше, чем длинный разговор. Если день тянет в разные стороны, полезнее выбрать одну нить и не рвать остальные.",
    advantage: "Короткий контакт с близким человеком сегодня работает лучше долгих объяснений.",
    abstain: "Домашние обязательства лучше не раздувать — минимум без чувства вины.",
    today_move: "Если успеешь закрыть одну важную вещь до обеда, остаток дня пойдёт легче.",
    practice_recommendation: {
      kind: "practice",
      text: "Две минуты тишины перед ответом.",
      reason: "Пауза сохраняет точность в коротких договорённостях.",
    },
    trace: {
      derived_claims: [
        {
          id: "claim.day_axis",
          kind: "axis",
          text: "День держится на коротких договорённостях, а не на длинных объяснениях.",
        },
        {
          id: "claim.day_card",
          kind: "symbol",
          text: "Карта дня учтена как дополнение: Отшельник",
        },
      ],
      limitations: ["Сфера «family» без личного сигнала сегодня — блок отсутствует."],
    },
  },
};

const story = {
  pulse: contract.day_story!.story!,
  hero: { themeHeadline: contract.day_story!.theme! },
  sphereFocus: {
    cards: [
      {
        id: "peak-relationships",
        sphere: "Отношения",
        role: "peak" as const,
        headline: "Отношения",
        body: contract.domains.relationships.opportunity,
      },
      {
        id: "caution-family",
        sphere: "Дом и семья",
        role: "caution" as const,
        headline: "Дом и семья",
        body: contract.domains.family.risk,
        releaseLine: contract.domains.family.action,
      },
    ],
    neutralNote: "",
  },
} as unknown as TodayDayStoryViewModel;

describe("buildTodayLiteraryReading", () => {
  it("builds prose without checklist wrappers or duplicate meaning spam", () => {
    const reading = buildTodayLiteraryReading(story, contract);
    expect(reading.opening).toMatch(/точностью|сообщение/i);
    expect(reading.opening).not.toMatch(/опирайся|сегодня сильнее|направить внимание/i);
    const blob = [reading.opening, reading.why, reading.lean, reading.ease, reading.anchor, reading.close].join(" ");
    expect(blob).not.toMatch(/→/);
    expect(reading.close).toBeTruthy();
  });

  it("weaves talisman into anchor prose without inventing catalog lecture", () => {
    const withTalisman: TodayContractV1 = {
      ...contract,
      day_story: {
        ...contract.day_story!,
        talisman: { color: "лазурь", stone: "аквамарин", note: "Один спокойный акцент." },
      },
    };
    const reading = buildTodayLiteraryReading(story, withTalisman);
    expect(reading.anchor).toMatch(/лазурь|аквамарин/i);
  });

  it("uses meaning-facing derived_claims for soft why, never kitchen limitations", () => {
    const reading = buildTodayLiteraryReading(story, contract);
    expect(reading.why).toMatch(/коротких договорённостях/i);
    expect(reading.why).not.toMatch(/учтена как|блок отсутствует|limitations/i);
    expect(pickSoftWhyLine(contract)).toMatch(/коротких договорённостях/i);
  });

  it("hides soft why when derived_claims are absent (no reason/advantage fallback)", () => {
    const noClaims: TodayContractV1 = {
      ...contract,
      day_story: {
        ...contract.day_story!,
        practice_recommendation: {
          kind: "practice",
          text: "Две минуты тишины перед ответом.",
          reason: "Пауза сохраняет точность в коротких договорённостях.",
        },
        trace: { derived_claims: [], limitations: ["kitchen only"] },
      },
    };
    expect(pickSoftWhyLine(noClaims)).toBeNull();
    expect(buildTodayLiteraryReading(story, noClaims).why).toBeNull();
  });
});
