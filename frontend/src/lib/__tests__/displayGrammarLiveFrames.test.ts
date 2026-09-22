import { emitProfileDisplayFrame } from "@/lib/displayGrammar/emitProfileDisplayFrame";
import { emitTodayDisplayFrame } from "@/lib/displayGrammar/emitTodayDisplayFrame";
import { findingIds, scanDisplayGrammar } from "@/lib/displayGrammar/scanDisplayGrammar";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { CoreProfile } from "@/lib/types";

const baseContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День просит не спешить с резкими жестами." },
  personal_growth: { development_point: "Один шаг на сегодня." },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
  primary_action: "Закрой одну задачу до 13:00",
  progress: {},
  generation_id: "live-frame",
  global_day: {
    primary_energy: "grounded",
    strength: ["deep_work"],
    risk: ["hard_negotiation"],
  },
};

const persistContract: TodayContractV1 = {
  ...baseContract,
  personal_day: { natal_overlay: { focus_axis: "work", activations: [{ id: "a1" }] } },
  day_story: {
    contract_version: "day_story_v1",
    day_personal: {
      summary_ru: "Сегодня твоя ось — одно обещание без лишнего шума.",
    },
    day_scenario: {
      conflict: {
        why_personal: "Тебе обычно проще держать одно слово, чем десять планов.",
      },
    },
    do: ["Назови одно обещание до полудня"],
    avoid: ["Не открывай второй фронт"],
  },
};

const journeyCore = {
  astro: { sun_sign: "virgo", sun_element: "earth" },
  numerology: { life_path: 7 },
  baseline: { archetype_seed: "explorer" },
  profile_contract_v1: {
    contract_version: "v1",
    recognition_line: "Ты первым видишь структуру, пока другие ещё спорят о деталях.",
    identity_core: "Длинное ядро не должно подменять recognition_line.",
    strengths: [],
    growth_zones: [],
    relationship_style: "",
    money_style: "",
    decision_style: "",
    recurring_patterns: [],
  },
  portrait_why_v0: {
    title: "Почему портрет такой",
    selected_by: [
      { id: "life_path", class: "selected_by", label: "Число пути 7 → Исследователь" },
    ],
    portrait_influenced_by: [{ id: "sun", class: "portrait_influenced_by", label: "Солнце в Деве" }],
  },
  insight_nodes_v0: {
    nodes: [
      {
        id: "n1",
        kind: "tension",
        title: "Ясность vs скорость",
        insight: "Сила в точности, а срыв — когда торопишь вывод.",
        grounded_on: [{ id: "g1", label: "Рост: спешка" }],
        help: "Дай себе один тихий проход перед решением.",
        living_evidence: ["снова сорвался в спешку"],
        source_fields: ["growth_zones", "helps"],
      },
    ],
  },
  effort_vector_v0: {
    effort_vector: "Дай себе один тихий проход перед решением.",
    source_node_id: "n1",
  },
  bridge_line_v0: {
    bridge_line:
      "Особенность уже ясна на уровне портрета. Today показывает, как она проявляется в конкретном дне — не как теория.",
    leads_to: "today",
  },
} as CoreProfile;

describe("live Today frames", () => {
  it("guest TODAY + ritual catalog has no T3 meaning and no lens", () => {
    const frame = emitTodayDisplayFrame({
      contract: baseContract,
      capability: "guest",
      dateLabel: "31 августа 2026",
      ritual: {
        cardCatalog: "Сила — внутренняя опора.",
        cardHook: { personal_angle: "якорь дня", base: { meaning: "Сила — внутренняя опора." } },
        numberCatalog: "8 — устойчивость.",
      },
    });
    expect(frame.atoms?.some((a) => a.slot_id?.startsWith("T3.") && a.text_class !== "chrome")).toBe(false);
    expect(frame.atoms?.some((a) => a.slot_id?.startsWith("T2.lens_"))).toBe(false);
    expect(frame.atoms?.some((a) => a.slot_id === "T2.catalog_card")).toBe(true);
    const humanLine = frame.atoms?.find((a) => a.slot_id === "T1-hero.human_line");
    expect(humanLine?.text).toMatch(/заземлен/i);
    expect(humanLine?.text).not.toMatch(/не спешить/);
    expect(humanLine?.json_field).toBeUndefined();
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("light + persisted Personal Day paints legal T3 and optional lens", () => {
    const frame = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      dateLabel: "31 августа 2026",
      ritual: {
        cardCatalog: "Сила — внутренняя опора.",
        cardHook: { personal_angle: "якорь дня", base: { meaning: "Сила — внутренняя опора." } },
      },
    });
    const ids = (frame.atoms ?? []).map((a) => a.slot_id);
    expect(ids).toContain("T3.headline");
    expect(ids).toContain("T3.focus_title");
    expect(ids).toContain("T3.focus_body");
    expect(ids).toContain("T3.priority");
    expect(ids).toContain("T2.lens_card");
    expect(frame.atoms?.find((a) => a.slot_id === "T2.lens_card")?.text).toBe("якорь дня");
    expect(frame.atoms?.find((a) => a.slot_id === "T3.focus_title")?.text).toMatch(/работ/i);
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("omits T2.lens_card when only Global chorus bridge is present", () => {
    const frame = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      dateLabel: "31 августа 2026",
      ritual: {
        cardCatalog: "Сила — внутренняя опора.",
        cardHook: {
          bridge_to_day: "архетип описывает сегодняшний конфликт",
          base: { meaning: "Сила — внутренняя опора." },
        },
      },
    });
    expect(frame.atoms?.some((a) => a.slot_id === "T2.lens_card")).toBe(false);
    expect(frame.atoms?.some((a) => a.slot_id === "T2.catalog_card")).toBe(true);
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("omits T2.lens_number when only Global number chorus bridge is present", () => {
    const frame = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      dateLabel: "31 августа 2026",
      ritual: {
        numberCatalog: "Семёрка — пауза перед решением.",
        numberHook: {
          bridge_to_day: "замедляет давление в этом конфликте",
          base: { meaning: "Семёрка — пауза перед решением." },
        },
      },
    });
    expect(frame.atoms?.some((a) => a.slot_id === "T2.lens_number")).toBe(false);
    expect(frame.atoms?.some((a) => a.slot_id === "T2.catalog_number")).toBe(true);
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("paints T2.lens_number from Personal×number angle, not chorus", () => {
    const frame = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      dateLabel: "31 августа 2026",
      ritual: {
        numberCatalog: "Семёрка — пауза перед решением.",
        numberHook: {
          bridge_to_day: "замедляет давление в этом конфликте",
          personal_angle: "Это число окрашивает уже собранный личный день.",
          base: { meaning: "Семёрка — пауза перед решением." },
        },
      },
    });
    expect(frame.atoms?.find((a) => a.slot_id === "T2.lens_number")?.text).toBe(
      "Это число окрашивает уже собранный личный день.",
    );
    expect(frame.atoms?.find((a) => a.slot_id === "T2.lens_number")?.json_field).toBe(
      "number.hook_reveal.personal_angle",
    );
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("unavailable MY DAY emits T3.unavailable only", () => {
    const frame = emitTodayDisplayFrame({
      contract: {
        ...baseContract,
        day_story: { contract_version: "day_story_v1", interpretation_status: "unavailable" },
      },
      capability: "light",
    });
    const meaning = (frame.atoms ?? []).filter(
      (a) => a.slot_id?.startsWith("T3.") && a.slot_id !== "T3.unavailable" && a.slot_id !== "T3.tracker",
    );
    expect(frame.atoms?.some((a) => a.slot_id === "T3.unavailable")).toBe(true);
    expect(meaning).toEqual([]);
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("emits T1.continuity from yesterday gratitude and omits when empty", () => {
    const filled = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      continuityBody: "Вчера ты отметил(а) благодарность: за спокойный момент.",
    });
    const slot = filled.atoms?.find((a) => a.slot_id === "T1.continuity");
    expect(slot?.text_class).toBe("user");
    expect(slot?.text).toMatch(/благодарност/i);
    expect(scanDisplayGrammar(filled)).toEqual([]);

    const empty = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
    });
    expect(empty.atoms?.some((a) => a.slot_id === "T1.continuity")).toBe(false);
  });

  it("continuity GET failure emits TF chrome instead of T1.continuity", () => {
    const frame = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      continuityBody: "Вчера ты отметил(а) благодарность: за спокойный момент.",
      continuityFailure: "no_connection",
    });
    expect(frame.atoms?.some((a) => a.slot_id === "T1.continuity")).toBe(false);
    expect(frame.atoms?.some((a) => a.slot_id === "TF.no_connection")).toBe(true);
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("emits T3.tracker from habit rows only and keeps it on unavailable MY DAY", () => {
    const withHabits: TodayContractV1 = {
      ...persistContract,
      today_progress: {
        rows: [
          {
            id: "habit:1",
            kind: "habit",
            kind_label: "Привычка",
            name: "Стакан воды",
            streak_days: 3,
            days_bool: [false, false, false, false, false, false, true],
          },
          {
            id: "practice",
            kind: "practice",
            kind_label: "Практика",
            name: "Дыхание 4-7-8",
            streak_days: 1,
            days_bool: [false, false, false, false, false, false, true],
          },
        ],
      },
    };
    const frame = emitTodayDisplayFrame({
      contract: withHabits,
      capability: "light",
    });
    const trackers = (frame.atoms ?? []).filter((a) => a.slot_id === "T3.tracker");
    expect(trackers.map((a) => a.text)).toEqual(["Стакан воды"]);
    expect(scanDisplayGrammar(frame)).toEqual([]);

    const unavailable = emitTodayDisplayFrame({
      contract: {
        ...withHabits,
        day_story: { contract_version: "day_story_v1", interpretation_status: "unavailable" },
      },
      capability: "light",
    });
    expect(unavailable.atoms?.some((a) => a.slot_id === "T3.unavailable")).toBe(true);
    expect(unavailable.atoms?.find((a) => a.slot_id === "T3.tracker")?.text).toBe("Стакан воды");
    expect(unavailable.atoms?.some((a) => a.slot_id === "T3.headline")).toBe(false);
  });

  it("unknown filled would_render field on a live frame is still finding 2", () => {
    const frame = emitTodayDisplayFrame({
      contract: baseContract,
      capability: "guest",
    });
    const findings = scanDisplayGrammar({
      ...frame,
      vm_fields: [
        ...(frame.vm_fields ?? []),
        { field: "vm.brandNewHeroTagline", filled: true, would_render: true },
      ],
    });
    expect(findingIds(findings)).toContain(2);
  });
});

describe("live Profile frames", () => {
  it("path acts scan clean and do not emit Character warehouse", () => {
    const frame = emitProfileDisplayFrame({ core: journeyCore });
    const ids = (frame.atoms ?? []).map((a) => a.slot_id);
    expect(ids).toContain("P1.recognition_line");
    expect(ids).toContain("P1.identity_core");
    expect(ids).toContain("P3.insight");
    expect(ids).toContain("P4.effort_vector");
    expect(ids).toContain("P5.bridge_line");
    expect(ids.some((id) => id?.startsWith("P6."))).toBe(false);
    expect(frame.atoms?.find((a) => a.slot_id === "P3.help")).toBeUndefined();
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("emits compact K13/K14 header facts when Matrix revealed", () => {
    const frame = emitProfileDisplayFrame({
      core: {
        ...journeyCore,
        profile_matrix_v0: {
          revealed_slots: {
            cultural_catalog: {
              color: "оливковый",
              stones: [{ label: "сапфир" }],
              traditions: [{ value: "год Металлической Лошади" }],
            },
            name_numerology: {
              expression: 3,
              soul_urge: 9,
              personality: 5,
            },
          },
        },
      } as CoreProfile,
    });
    const correspondence = frame.atoms?.find((a) => a.slot_id === "P2.correspondence");
    const name = frame.atoms?.find((a) => a.slot_id === "P2.name_numerology");
    expect(correspondence?.text).toMatch(/оливковый/);
    expect(correspondence?.text_class).toBe("catalog");
    expect(name?.text).toMatch(/выражение 3/);
    expect(name?.text_class).toBe("calc");
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("does not paint identity_core as the recognition line", () => {
    const frame = emitProfileDisplayFrame({
      core: {
        baseline: { archetype_seed: "explorer" },
        profile_contract_v1: {
          contract_version: "v1",
          identity_core: "Ядро без recognition_line.",
          strengths: [],
          growth_zones: [],
          relationship_style: "",
          money_style: "",
          decision_style: "",
          recurring_patterns: [],
        },
      } as CoreProfile,
    });
    expect(frame.atoms?.find((a) => a.slot_id === "P1.recognition_line")).toBeUndefined();
    expect(frame.atoms?.find((a) => a.slot_id === "P1.identity_core")?.text).toContain("Ядро");
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("PIC-K02 natal anchors keep P2.anchor.* and occupancy does not dump to rhythm", () => {
    const frame = emitProfileDisplayFrame({
      core: {
        ...journeyCore,
        portrait_why_v0: {
          title: "Почему портрет такой",
          selected_by: [
            {
              id: "life_path",
              class: "selected_by",
              label: "Число пути 7 · Искатель",
              contribution: "Семёрка — пауза и глубина: ответы приходят через наблюдение, не через давление.",
              life_path: 7,
            },
            {
              id: "ce_claim:builds_through_analysis",
              class: "selected_by",
              label: "Ты строишь через анализ",
            },
          ],
          portrait_influenced_by: [
            { id: "sun", class: "portrait_influenced_by", label: "Солнце в Деве" },
            { id: "moon", class: "portrait_influenced_by", label: "Луна в Тельце" },
            { id: "asc", class: "portrait_influenced_by", label: "Асцендент в Близнецах" },
            {
              id: "ce_claim:planet_in_sign:mars:cancer",
              class: "portrait_influenced_by",
              label: "Марс в Раке — qualifier",
            },
          ],
        },
      } as CoreProfile,
    });
    const ids = (frame.atoms ?? []).map((a) => a.slot_id);
    expect(ids).toContain("P2.anchor.sun");
    expect(ids).toContain("P2.anchor.moon");
    expect(ids).toContain("P2.anchor.asc");
    expect(ids).toContain("P2.selected_life_path");
    const selected = frame.atoms?.find((a) => a.slot_id === "P2.selected_life_path");
    expect(selected?.text).toMatch(/число пути 7/i);
    expect(selected?.text).toMatch(/глубин|наблюден/i);
    expect(selected?.text).not.toMatch(/строишь через анализ/i);
    expect(frame.atoms?.find((a) => a.slot_id === "P2.anchor.rhythm")).toBeUndefined();
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("PIC-K12 omits selected_life_path without grounded number_base contribution", () => {
    const frame = emitProfileDisplayFrame({
      core: {
        ...journeyCore,
        portrait_why_v0: {
          selected_by: [{ id: "life_path", class: "selected_by", label: "Число пути 7" }],
          portrait_influenced_by: [],
        },
      } as CoreProfile,
    });
    expect(frame.atoms?.find((a) => a.slot_id === "P2.selected_life_path")).toBeUndefined();
  });

  it("PIC-K07 emits at most two path spheres from contract F06 projection", () => {
    const frame = emitProfileDisplayFrame({
      core: {
        ...journeyCore,
        profile_contract_v1: {
          ...journeyCore.profile_contract_v1,
          life_spheres: {
            family: {
              how: "act / pursue — home, family, roots.",
              need: "home, family, roots, private-base",
            },
            money: {
              how: "feel / respond — possessions, money.",
              need: "possessions, money, personal-resources",
            },
          },
        },
      } as CoreProfile,
    });
    const titles = (frame.atoms ?? []).filter((a) => a.slot_id === "P4.sphere.title");
    const teasers = (frame.atoms ?? []).filter((a) => a.slot_id === "P4.sphere.teaser");
    const expands = (frame.atoms ?? []).filter((a) => a.slot_id === "P4.sphere.expand");
    expect(titles.length).toBe(0);
    expect(teasers.length).toBe(2);
    expect(expands.length).toBe(2);
    expect(teasers.some((a) => /home|family/.test(a.text || ""))).toBe(true);
    expect(teasers.every((a) => a.text !== journeyCore.effort_vector_v0?.effort_vector)).toBe(true);
    expect(scanDisplayGrammar(frame)).toEqual([]);
  });

  it("PIC-K15 emits P6.natal_decode on Explore, not as a path act", () => {
    const path = emitProfileDisplayFrame({ core: journeyCore });
    expect(path.atoms?.some((a) => a.slot_id === "P6.natal_decode")).toBe(false);
    expect(path.atoms?.some((a) => a.slot_id?.startsWith("P6."))).toBe(false);

    const explore = emitProfileDisplayFrame({
      core: journeyCore,
      natalDecode: {
        patternThesis: "Карта объясняет уже известное ядро через квадрат.",
        sections: [{ thesis: "Точность держится, пока не торопишь вывод." }],
      },
    });
    const decode = explore.atoms?.find((a) => a.slot_id === "P6.natal_decode");
    expect(decode?.surface).toBe("explore");
    expect(decode?.text).toMatch(/уже известное ядро/);
    expect(decode?.text_class).toBe("generated");
    expect(scanDisplayGrammar(explore)).toEqual([]);
  });

  it("PIC-K16 emits P6.practical_tips on Explore, not as a path act", () => {
    const path = emitProfileDisplayFrame({ core: journeyCore });
    expect(path.atoms?.some((a) => a.slot_id === "P6.practical_tips")).toBe(false);

    const explore = emitProfileDisplayFrame({
      core: journeyCore,
      practicalTips: [
        "Сделай это так: act / pursue — possessions, money.",
        "Один проверяемый шаг в этой зоне: possessions, money, personal-resources",
      ],
    });
    const tips = explore.atoms?.find((a) => a.slot_id === "P6.practical_tips");
    expect(tips?.surface).toBe("explore");
    expect(tips?.text).toMatch(/possessions, money/);
    expect(tips?.text_class).toBe("generated");
    expect(scanDisplayGrammar(explore)).toEqual([]);
  });

  it("PIC-K03 emits P6.applied.* on Explore, not as a path act", () => {
    const path = emitProfileDisplayFrame({ core: journeyCore });
    expect(path.atoms?.some((a) => String(a.slot_id).startsWith("P6.applied."))).toBe(false);

    const explore = emitProfileDisplayFrame({
      core: journeyCore,
      appliedHowDo: {
        asc: {
          how: "doorway-meeting / how-met — questions, options.",
          do: "В первом контакте учитывай: doorway-meeting, how-met.",
        },
        houses: {
          "4": {
            how: "act / pursue — home, family, roots.",
            do: "В этой зоне учитывай: home, family, roots.",
          },
        },
      },
    });
    const asc = explore.atoms?.find((a) => a.slot_id === "P6.applied.asc");
    const house = explore.atoms?.find((a) => a.slot_id === "P6.applied.house");
    expect(asc?.surface).toBe("explore");
    expect(asc?.text).toMatch(/doorway-meeting/);
    expect(house?.surface).toBe("explore");
    expect(house?.text).toMatch(/home, family/);
    expect(scanDisplayGrammar(explore)).toEqual([]);
  });
});
