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

  it("maps day_story into Day Map chapters (opening / glance / move) — not a sky fact wall", () => {
    const narrative = buildTodayDayNarrative({ contract, story, morningRitualData });
    expect(narrative.dayMap).toBeTruthy();
    expect(narrative.dayMap?.source).toBe("day_story");
    const ids = narrative.chapters.map((c) => c.id);
    expect(ids).toEqual(["opening", "force", "supports"]);
    expect(ids).not.toContain("sky");
    expect(ids).not.toContain("personal");
    expect(ids).not.toContain("symbols");
    const opening = narrative.chapters.find((c) => c.id === "opening")!;
    expect(opening.lead || opening.paragraphs.join(" ")).toMatch(/точност|сообщен/i);
    const force = narrative.chapters.find((c) => c.id === "force")!;
    expect(force.kicker).toMatch(/одном взгляде/i);
    expect(force.dual?.strengthen.join(" ")).toMatch(/Короткий контакт/i);
    expect(force.dual?.soften.join(" ")).toMatch(/обязательств|перегруж/i);
    const supports = narrative.chapters.find((c) => c.id === "supports")!;
    expect(supports.lead).toMatch(/Закрой одну важную/i);
  });

  it("prefers Day Map over foundation dumps when day_story slots are present", () => {
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
    expect(ids).not.toContain("astro");
    expect(ids).not.toContain("lunar");
    expect(ids).not.toContain("sky");
    expect(narrative.dayMap?.whyLayers.some((l) => /Меркурий|Луна/i.test(l))).toBe(true);
  });

  it("does not dump day_personal into chapters when Day Map is available", () => {
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
    expect(narrative.chapters.find((c) => c.id === "personal")).toBeUndefined();
    expect(narrative.dayMap).toBeTruthy();
  });

  it("keeps electional chapter even when Day Map is available", () => {
    const withElectional: TodayContractV1 = {
      ...contract,
      day_story: {
        ...contract.day_story!,
        day_personal: {
          electional_horary: {
            mode: "electional",
            verdict: "caution",
            verdict_ru: "Момент рабочий с оговорками.",
            summary_ru: "Электив 2026-07-24 16:00: ASC Весы, Луна Рак.",
            notes_ru: "Электив soft: чеклист момента.",
            moment: { date: "2026-07-24", time: "16:00" },
            ascendant: { sign_ru: "Весы", degree_in_sign: 12 },
            moon: { sign_ru: "Рак", dignity: { name_ru: "обитель" } },
            planetary_hour: {
              matched: true,
              ruler_planet_ru: "Венера",
              period: "day",
            },
            checklist: [
              {
                id: "asc_late",
                status: "caution",
                title: "ASC слишком поздний",
                story_ru: "Асцендент в последних градусах.",
              },
              {
                id: "moon_dignity",
                status: "pass",
                title: "Луна — обитель",
                story_ru: "Луна в Раке.",
              },
            ],
          },
        },
      },
    };
    const narrative = buildTodayDayNarrative({
      contract: withElectional,
      story,
      morningRitualData,
    });
    expect(narrative.dayMap).toBeTruthy();
    const electional = narrative.chapters.find((c) => c.id === "electional");
    expect(electional).toBeTruthy();
    expect(electional?.kicker).toMatch(/Электив/i);
    expect(electional?.lead).toMatch(/оговорк/i);
    expect(electional?.checklist?.length).toBeGreaterThan(0);
    expect(electional?.checklist?.[0]?.status).toBe("caution");
  });

  it("surfaces holiday and name numbers on Day Map supports", () => {
    const withContext: TodayContractV1 = {
      ...contract,
      day_story: {
        ...contract.day_story!,
        day_foundation: {
          contract_version: "day_foundation_v1",
          seasonal: {
            season: "spring",
            season_ru: "весна",
            holidays: {
              is_holiday: true,
              today: [{ id: "womens_day", name_ru: "Международный женский день" }],
            },
          },
        },
        day_personal: {
          name_numbers: {
            status: "ok",
            summary_ru: "Числа имени (soft): Expression 7, Soul Urge 5.",
            expression: { value: 7 },
            soul_urge: { value: 5 },
          },
        },
      },
    };
    const narrative = buildTodayDayNarrative({
      contract: withContext,
      story,
      morningRitualData,
    });
    expect(narrative.dayMap).toBeTruthy();
    const supports = narrative.chapters.find((c) => c.id === "supports");
    const body = [supports?.lead, ...(supports?.paragraphs ?? [])].filter(Boolean).join(" ");
    expect(body).toMatch(/женск/i);
    expect(body).toMatch(/Expression|Числа имени/i);
  });

  it("expands supports as Твой ход with concrete move + color", () => {
    const narrative = buildTodayDayNarrative({ contract, story, morningRitualData });
    const supports = narrative.chapters.find((c) => c.id === "supports")!;
    expect(supports.kicker).toMatch(/Твой ход/i);
    expect(supports.accent).toBe("support");
    expect(supports.lead).toMatch(/Закрой одну важную/i);
    const body = [supports.lead, ...supports.paragraphs].filter(Boolean).join(" ");
    expect(body).toMatch(/Цвет дня|синий|Сдерживает спешку/i);
  });
});
