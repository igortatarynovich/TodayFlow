import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodaySkyCard } from "@/lib/todayDaySpine";
import { buildTodayDayNarrative } from "@/lib/todayDayNarrative";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import { buildTodayLiteraryReading } from "@/lib/todayLiteraryReading";

describe("buildTodayDayNarrative", () => {
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
        risk: "Лишние домашние обязательства сегодня легко перегружают.",
        action: "Оставь минимум — без чувства вины.",
        evidence_status: "present",
      },
    },
    primary_action: "Если успеешь закрыть одну важную вещь до обеда, остаток дня пойдёт легче.",
    progress: {},
    generation_id: "t",
    day_story: {
      contract_version: "day_story_v1",
      theme: "Точность важнее объёма",
      story:
        "Сегодня многое решается не количеством слов, а их точностью. Иногда одно короткое сообщение меняет больше, чем длинный разговор.",
      advantage: "Короткий контакт сегодня работает лучше долгих объяснений.",
      abstain: "Домашние обязательства лучше не раздувать.",
      today_move: "Закрой одну важную вещь до обеда.",
      do: ["Одно точное сообщение", "Пауза перед ответом"],
      avoid: ["Длинные разборы на бегу"],
      talisman: { color: "синий", stone: "лазурит", note: "Держит ясность в коротких решениях." },
      practice_recommendation: {
        kind: "practice",
        text: "Две минуты тишины перед ответом.",
        reason: "Пауза сохраняет точность.",
      },
      symbolic_note: "Карта и число уточняют ритм, а не отменяют фон дня.",
      trace: {
        derived_claims: [
          {
            id: "claim.day_axis",
            kind: "axis",
            text: "День держится на коротких договорённостях.",
          },
        ],
      },
    },
  };

  const morningRitualData = {
    date: "2026-06-23",
    celestial_events: {
      lunar_phase: {
        name: "Убывающая луна",
        themes: "отпускание лишнего",
        guidance: "Отпускай лишнее, чтобы осталось главное.",
        next_phase: { name: "Новолуние", in_days: 3 },
      },
      ingresses: [
        {
          planet_ru: "Меркурий",
          sign_ru: "Рак",
          story_ru: "Меркурий переходит в Рак — меняется тон тем, которые он подсвечивает.",
        },
      ],
      personal_transits: [
        {
          id: "t1",
          title: "Марс — квадрат — Сатурн",
          story_ru: "Создаёт напряжение, которое просит осознанного выбора.",
        },
      ],
      sky_aspects: [
        {
          id: "a1",
          title: "Солнце — квадрат — Луна",
          story_ru: "День подсвечивает разрыв между намерением и настроением.",
        },
      ],
    },
  } as MorningRitualData;

  const story = {
    pulse: contract.day_story!.story!,
    hero: { themeHeadline: contract.day_story!.theme!, themeShort: contract.day_story!.theme! },
    skyCards: [] as TodaySkyCard[],
    colorGuide: {
      name: "синий",
      benefit: "Сдерживает спешку и помогает говорить точнее.",
      clothing: "В деталях одежды или аксессуаре.",
      accessory: "Браслет.",
      amount: "Один акцент.",
      avoidColor: "Яркий красный",
      avoidWhy: "Разгоняет темп в переговорах.",
    } as TodayDayColorGuide,
    tarotImpact: {
      title: "Сила",
      headline: "Мягкая сила важнее давления.",
      body: "Карта просит держать тон без резкости.",
    },
    numberImpact: {
      title: "22",
      headline: "Ритм коротких циклов.",
      body: "Десять параллельных входов сегодня скорее шумят, чем помогают.",
    },
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

  it("tells sky → force → symbols as narrative chapters, not empty", () => {
    const narrative = buildTodayDayNarrative({ contract, story, morningRitualData });
    const ids = narrative.chapters.map((c) => c.id);
    expect(ids).toEqual(["opening", "sky", "force", "symbols", "supports"]);
    const sky = narrative.chapters.find((c) => c.id === "sky")!;
    const skyText = [sky.lead, ...sky.paragraphs].filter(Boolean).join(" ");
    expect(skyText).toMatch(/Луна|Меркурий|Марс/i);
    expect(skyText).toMatch(/Рак|напряжение|намерение/i);
    const force = narrative.chapters.find((c) => c.id === "force")!;
    expect(force.accent).toBe("dual");
    const forceText = [
      ...(force.dual?.strengthen ?? []),
      ...(force.dual?.soften ?? []),
      ...force.paragraphs,
    ].join(" ");
    expect(forceText).toMatch(/усилит|ослабит|сильнее|слабее|не дожимать|Короткий|обязательств/i);
    const symbols = narrative.chapters.find((c) => c.id === "symbols")!;
    const symbolsText = [symbols.lead, ...symbols.paragraphs].filter(Boolean).join(" ");
    expect(symbolsText).toMatch(/Карта дня|Число дня|Сила|22/i);
  });

  it("keeps literary opening meaning without inventing checklist chrome", () => {
    const narrative = buildTodayDayNarrative({ contract, story, morningRitualData });
    const opening = narrative.chapters.find((c) => c.id === "opening")!;
    const openingText = [opening.lead, ...opening.paragraphs].filter(Boolean).join(" ");
    expect(openingText).toMatch(/точностью|договорённостях/i);
    expect(openingText).not.toMatch(/опирайся|сегодня сильнее/i);
    expect(buildTodayLiteraryReading(story, contract).opening).toBeTruthy();
  });

  it("expands supports as Твой ход with color why from guide + talisman note", () => {
    const narrative = buildTodayDayNarrative({ contract, story, morningRitualData });
    const supports = narrative.chapters.find((c) => c.id === "supports")!;
    expect(supports.kicker).toMatch(/Твой ход/i);
    expect(supports.accent).toBe("support");
    expect(supports.colorHex).toBeTruthy();
    const body = [supports.lead, ...supports.paragraphs].filter(Boolean).join(" ");
    expect(body).toMatch(/Цвет дня|синий|Сдерживает спешку/i);
    expect(body).toMatch(/Пауза сохраняет точность|Две минуты/i);
  });
});
