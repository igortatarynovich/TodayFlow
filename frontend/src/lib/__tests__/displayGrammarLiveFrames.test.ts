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
    expect(frame.atoms?.find((a) => a.slot_id === "T3.focus_title")?.text).toMatch(/работ/i);
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
      (a) => a.slot_id?.startsWith("T3.") && a.slot_id !== "T3.unavailable",
    );
    expect(frame.atoms?.some((a) => a.slot_id === "T3.unavailable")).toBe(true);
    expect(meaning).toEqual([]);
    expect(scanDisplayGrammar(frame)).toEqual([]);
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
});
