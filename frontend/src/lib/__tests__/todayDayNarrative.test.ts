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
    expect(ids).toContain("opening");
    expect(ids).toContain("force");
    expect(ids).toContain("symbols");
    expect(ids).toContain("supports");
    // Without day_foundation, legacy mixed sky chapter remains.
    expect(ids).toContain("sky");
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

  it("splits foundation into Суть дня + astro + lunar when present", () => {
    const withFoundation: TodayContractV1 = {
      ...contract,
      day_story: {
        ...contract.day_story!,
        day_foundation: {
          contract_version: "day_foundation_v1",
          essence: {
            theme: "Смена перспективы: Меркурий → Рак",
            story_ru:
              "Сегодня в небе складывается смена процессов. Меркурий переходит в Рак. Луна сейчас — Убывающая луна: отпускай лишнее. Суть дня рождается на стыке этих двух слоёв.",
          },
          astro: {
            summary_ru: "Меркурий переходит в Рак — меняется тон разговоров.",
            beats: [
              {
                id: "ingress.Mercury",
                kind: "ingress",
                title: "Меркурий → Рак",
                story_ru: "Меркурий переходит в Рак — меняется тон разговоров.",
              },
            ],
          },
          lunar: {
            summary_ru: "Луна сейчас — Убывающая луна: Отпускай лишнее.",
            moon_sign: { sign_ru: "Стрелец" },
            beats: [{ id: "lunar.phase", kind: "phase", title: "Убывающая луна", story_ru: "Отпускай лишнее." }],
          },
          source_inputs: { has_astro: true, has_lunar: true, has_essence: true },
        },
      },
    };
    const narrative = buildTodayDayNarrative({
      contract: withFoundation,
      story,
      morningRitualData,
    });
    const ids = narrative.chapters.map((c) => c.id);
    expect(ids[0]).toBe("opening");
    expect(narrative.chapters[0].kicker).toMatch(/Суть дня/i);
    expect(ids).toContain("astro");
    expect(ids).toContain("lunar");
    expect(ids).not.toContain("sky");
    expect(narrative.theme).toMatch(/перспектив|Меркурий/i);
  });

  it("surfaces soft personal layer from day_personal (rulers / lords / HD)", () => {
    const withPersonal: TodayContractV1 = {
      ...contract,
      day_story: {
        ...contract.day_story!,
        day_foundation: {
          contract_version: "day_foundation_v1",
          essence: { theme: "Ось", story_ru: "Суть дня без личного слоя." },
          astro: { summary_ru: "Небо дня спокойное." },
          lunar: { summary_ru: "Луна в спокойном знаке." },
        },
        day_personal: {
          personal_astrology: {
            house_rulers_chains: {
              summary_ru: "Управители домов: 1-й — Венера, 10-й — Сатурн.",
            },
            time_lords: {
              summary_ru: "Firdaria: мажор Луна, субпериод Сатурн.",
              firdaria: {
                major: { planet_ru: "Луна" },
                sub: { planet_ru: "Сатурн" },
              },
              zodiacal_releasing: {
                level1: { sign_ru: "Рак", lord_ru: "Луна" },
              },
            },
            profections: {
              summary_ru: "Годовая профекция в 10-м доме, управитель Сатурн.",
              annual: { house: 10, lord_ru: "Сатурн", sign_ru: "Козерог" },
            },
          },
          human_design: {
            type_authority: {
              summary_ru: "HD soft: Генератор; авторитет Сакральный; стратегия — Отвечать.",
              type: { id: "generator", name_ru: "Генератор" },
              authority: { id: "sacral", name_ru: "Сакральный" },
            },
            profile_lines_cross: {
              summary_ru: "Профиль 3/5 · Мученик / Еретик; Правый угол (личный путь).",
              profile: { id: "3/5", label_ru: "3/5 · Мученик / Еретик" },
              incarnation_cross: { label: "1/2/13/7" },
            },
            variables: {
              summary_ru: "Variables soft: Пищеварение вправо · Свет; Перспектива влево · Выживание.",
              pattern: "RLRL",
              digestion: { color_name_ru: "Свет", orientation: "right" },
            },
            channels: {
              summary_ru: "Каналы HD (soft): 1-8 (Вдохновение).",
              channels: [{ id: "1-8", name_ru: "Вдохновение", centers_ru: ["G", "Горло"] }],
            },
            bodygraph: {
              activations: [
                {
                  id: "hd-activate-sun-1",
                  title: "Транзит активирует ворота 1",
                  story_ru: "Сегодняшнее Солнце касается ваших ворот 1.",
                },
              ],
            },
            transit_gates: {
              sun: { gate: 1, line: 2, label: "1.2", theme_ru: "творческий импульс" },
            },
          },
        },
      },
    };
    const narrative = buildTodayDayNarrative({
      contract: withPersonal,
      story,
      morningRitualData,
    });
    const personal = narrative.chapters.find((c) => c.id === "personal");
    expect(personal).toBeTruthy();
    expect(personal!.kicker).toMatch(/Личный слой/i);
    const text = [personal!.lead, ...personal!.paragraphs].filter(Boolean).join(" ");
    expect(text).toMatch(/Профиль 3\/5|Variables soft|HD soft|ворот|Firdaria|Управители|Каналы HD/i);
    expect(personal!.signals?.length).toBeGreaterThan(0);
    expect(personal!.signals?.map((s) => s.label).join(" ")).toMatch(
      /HD тип|HD профиль|HD variables|Профекция|Firdaria|HD/i,
    );
    expect(personal!.accent).toBe("sky");
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
