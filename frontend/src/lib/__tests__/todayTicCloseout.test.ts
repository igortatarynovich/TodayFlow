/**
 * TIC close-out — independent 20/20 re-audit of locked Today surfaces.
 * Does not treat coverage-table COMPLETE as proof.
 * Canon: TODAY_INFORMATION_CONTRACT_V1 §12
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { emitTodayDisplayFrame } from "@/lib/displayGrammar/emitTodayDisplayFrame";
import { matchInventorySlot } from "@/lib/displayGrammar/inventoryCatalog";
import { pickInstructionPersonalBridge } from "@/lib/todayInstructionBridge";
import {
  SHARED_DAY_HUMAN_LINES,
  formulateSharedDayHumanLine,
} from "@/lib/todayK01HumanLine";
import { pickMyDayCautionLines, pickMyDayPriorityLines } from "@/lib/todayMyDayPriority";
import { pickPersonalFocusAxisLabel } from "@/lib/todayPersonalFocusAxis";
import { pickRitualCardLens, pickRitualNumberLens } from "@/lib/ritualRevealCopy";
import {
  contentClassFromFocusAxis,
  needQueryFromFocusAxis,
} from "@/lib/todayPracticeSelect";
import { pickLockedSupportSlot } from "@/lib/todaySupportXor";
import { buildTodayDayBriefModel } from "@/lib/todayDayBrief";
import { buildGratitudeMemorySlot } from "@/lib/todayEveningGratitude";
import { TODAY_UNAVAILABLE_COPY } from "@/lib/todaySlotAvailability";
import type { TodayContractV1 } from "@/lib/todayContract";
import { DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";
import { TODAY_SCREEN_FLOW_CAPABILITY } from "@/lib/todayScreenFlowCapability";
import { buildTodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import { buildTodayCompositionViewModel } from "@/lib/todayCompositionModel";
import { createEmptyDayEngagement } from "@/lib/todayDayEngagement";

const FE_ROOT = join(__dirname, "../../..");

const domains = {
  work: { status: "s", opportunity: "o", risk: "r", action: "a" },
  money: { status: "s", opportunity: "o", risk: "r", action: "a" },
  relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
  energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
} as const;

function contract(extra: Partial<TodayContractV1> = {}): TodayContractV1 {
  return {
    contract_version: "today_contract_v1",
    global_context: { period: "Период спокойной ясности" },
    personal_growth: { development_point: "d" },
    domains,
    primary_action: "a",
    progress: {},
    generation_id: "closeout",
    global_day: { primary_energy: "clarity", strength: ["deep_work"], risk: ["hard_negotiation"] },
    ...extra,
  };
}

const persisted = {
  personal_day: { natal_overlay: { focus_axis: "work", activations: [{ id: "a1" }] } },
} as const;

function readRel(rel: string): string {
  return readFileSync(join(FE_ROOT, rel), "utf8");
}

describe("TIC close-out 20/20 executable re-audit", () => {
  it("K01 formulates primary_energy and omits greeting/unknown", () => {
    const greeting = "Доброе утро";
    const model = buildTodayDayBriefModel({
      contract: contract(),
      dateLabel: "21 сентября",
      salutation: greeting,
      headline: greeting,
      energyLine: "хор энергии не human_line",
    });
    expect(model.atmosphereLine).toBe(SHARED_DAY_HUMAN_LINES.clarity);
    expect(model.atmosphereLine).not.toBe(greeting);
    expect(model.atmosphereLine).not.toBe("хор энергии не human_line");
    expect(formulateSharedDayHumanLine("calm")).toBeNull();
    expect(DAY_VISUAL_MODES.map((id) => formulateSharedDayHumanLine(id)).filter(Boolean)).toHaveLength(8);
  });

  it("K02–K05 paint Engine drivers/windows/chips, not natal as TODAY SoT", () => {
    const model = buildTodayDayBriefModel({
      contract: contract({
        global_day: {
          primary_energy: "clarity",
          strength: ["deep_work"],
          risk: ["hard_negotiation"],
          drivers: [
            { id: "moon-1", kind: "moon_ingress", fact_ru: "Луна вошла в Рыбы" },
            { id: "sky-1", kind: "sky_aspect", fact_ru: "Марс в квадрате" },
          ],
          windows: [
            { time: "09:00", intensity: 0.8 },
            { time: "14:00", intensity: 0.4 },
          ],
        },
      }),
      dateLabel: "21 сентября",
      salutation: "",
    });
    expect(model.strengthChips.some((c) => c.label.length > 0)).toBe(true);
    expect(model.riskChips.some((c) => c.label.length > 0)).toBe(true);
    expect(model.dayWindow?.start).toBe("09:00");
    expect(model.transits.length).toBeGreaterThan(0);
  });

  it("K06 headline is overlay thesis; kitchen mash does not fill", () => {
    const overlay = "Личная энергия давит на самопрезентацию.";
    const withThesis = buildTodayDayBriefModel({
      contract: contract({
        ...persisted,
        day_story: { contract_version: "day_story_v1", day_personal: { summary_ru: overlay } },
      }),
      dateLabel: "d",
      salutation: "",
    });
    expect(withThesis.personalLine).toBe(overlay);
    const kitchen = buildTodayDayBriefModel({
      contract: contract({
        ...persisted,
        day_story: {
          contract_version: "day_story_v1",
          day_personal: { summary_ru: "Firdaria и управители. Генератор. Ба-цзы." },
        },
      }),
      dateLabel: "d",
      salutation: "",
    });
    expect(kitchen.personalLine).toBeNull();
  });

  it("K07/K08 omit without overlay; axis is map_label not scene sphere", () => {
    expect(pickPersonalFocusAxisLabel(contract())).toBeNull();
    expect(
      pickPersonalFocusAxisLabel(
        contract({
          personal_day: { natal_overlay: { focus_axis: "work" } },
          day_story: {
            contract_version: "day_story_v1",
            day_scenario: { scenes: [{ sphere: "relationships", sphere_label_ru: "Отношения" }] },
          },
        }),
      ),
    ).toBe("Работа");
    expect(
      pickInstructionPersonalBridge(
        contract({ day_story: { contract_version: "day_story_v1" } }),
      ),
    ).toBeNull();
  });

  it("K09/K10 omit Global scene action/caution and empty personal lists", () => {
    const rec = "Назови одну вещь прямо.";
    const scene = contract({
      ...persisted,
      day_story: {
        contract_version: "day_story_v1",
        do: [rec],
        avoid: ["Не делай вид, что всё нормально."],
        day_scenario: {
          scenes: [{ recommended_action: rec, do_not: "Не делай вид, что всё нормально." }],
        },
      },
    });
    expect(pickMyDayPriorityLines({ contract: scene, doItems: [rec], glancePrioritize: rec })).toEqual([]);
    expect(
      pickMyDayCautionLines({
        contract: scene,
        avoidItems: ["Не делай вид, что всё нормально."],
      }),
    ).toEqual([]);
    expect(
      pickMyDayPriorityLines({
        contract: contract({ ...persisted }),
        doItems: [],
        glancePrioritize: "День просит не спешить с резкими жестами.",
      }),
    ).toEqual([]);
  });

  it("K11–K14 catalog stays catalog; chorus bridge is not the personal lens", () => {
    const chorus = "архетип описывает сегодняшний конфликт";
    expect(pickRitualCardLens({ bridge_to_day: chorus, personal_angle: chorus, base: { meaning: "база" } }, true)).toBeNull();
    expect(pickRitualNumberLens({ bridge_to_day: chorus, personal_angle: chorus, base: { meaning: "база" } }, true)).toBeNull();
    expect(pickRitualCardLens({ personal_angle: "omit" }, true)).toBeNull();
    expect(pickRitualCardLens({ personal_angle: "Личная окраска карты." }, false)).toBeNull();
    const personal = "Эта карта окрашивает уже собранный личный день.";
    expect(pickRitualCardLens({ personal_angle: personal, bridge_to_day: chorus }, true)).toBe(personal);
  });

  it("K15 omits catalog/talisman leftover without color_guide nest", () => {
    const story = buildTodayDayStoryViewModel({
      base: buildTodayCompositionViewModel({
        contract: contract({ color_guide: null }),
        cardName: null,
        cardMeaning: null,
        numerologyValue: null,
        numerologyMeaning: null,
        morningRitualData: {
          celestial_events: { daily_symbols: { color: { name: "Янтарный", benefit_ru: "тёплая поддержка" } } },
        } as never,
      }),
      contract: contract({
        color_guide: null,
        day_story: {
          contract_version: "day_story_v1",
          interpretation_status: "ok",
          talisman: { color: "Янтарный" },
          day_scenario: { props: { color: null } },
        },
      }),
      dateISO: "2026-09-21",
      cardName: null,
      cardMeaning: null,
      numerologyValue: null,
      numerologyMeaning: null,
      morningRitualData: {
        celestial_events: { daily_symbols: { color: { name: "Янтарный", benefit_ru: "тёплая поддержка" } } },
      } as never,
      yesterdayClosed: false,
      todayOpened: true,
      engagement: createEmptyDayEngagement(),
    });
    expect(story.colorGuide).toBeNull();
  });

  it("K16/K17 XOR is F10 practice class; empty branch does not switch", () => {
    expect(needQueryFromFocusAxis("clarity")).toBeNull();
    expect(needQueryFromFocusAxis("work")?.purpose).toBe("decision_making");
    expect(contentClassFromFocusAxis("work")).toBe("practice");
    expect(
      pickLockedSupportSlot({
        contract: contract({ ...persisted }),
        practiceReady: false,
      }),
    ).toBeNull();
    expect(
      pickLockedSupportSlot({
        contract: contract({
          ...persisted,
          day_story: {
            contract_version: "day_story_v1",
            practice_recommendation: { kind: "affirmation", text: "Я справлюсь." },
            day_scenario: { props: { affirmations: [{ text: "Я справлюсь." }] } },
          },
        }),
        practiceReady: true,
      }),
    ).toBe("practice");
  });

  it("K18 guest cannot mint MY DAY; K19 empty gratitude omits; K20 unavailable is honesty copy", () => {
    expect(TODAY_SCREEN_FLOW_CAPABILITY.guest.myDay).toBe(false);
    expect(buildGratitudeMemorySlot(null).body).toBe("");
    expect(TODAY_UNAVAILABLE_COPY).toBe("Не удалось загрузить.");
    const frame = emitTodayDisplayFrame({
      contract: contract({
        day_story: { contract_version: "day_story_v1", interpretation_status: "unavailable" },
      }),
      capability: "deep",
    });
    const slots = frame.atoms.map((a) => a.slot_id);
    expect(slots).toContain("T3.unavailable");
    expect(slots.filter((id) => id.startsWith("T3.") && id !== "T3.unavailable")).toEqual([]);
  });
});

describe("TIC close-out Inventory last-authority", () => {
  it("locked emit atoms are Inventory slots; payload leftovers do not paint", () => {
    const frame = emitTodayDisplayFrame({
      contract: contract({
        ...persisted,
        day_story: {
          contract_version: "day_story_v1",
          day_personal: { summary_ru: "Одно обещание без лишнего шума." },
          do: ["Назови одну вещь прямо."],
          day_scenario: {
            scenes: [{ recommended_action: "Назови одну вещь прямо." }],
            conflict: { why_personal: "Тебе обычно проще держать одно слово." },
          },
        },
      }),
      capability: "deep",
      ritual: {
        cardHook: { bridge_to_day: "хор карты", personal_angle: "omit", base: { meaning: "каталог карты" } },
        numberHook: { bridge_to_day: "хор числа", personal_angle: "omit", base: { meaning: "каталог числа" } },
      },
    });
    for (const atom of frame.atoms) {
      expect(matchInventorySlot(atom.slot_id)).toBeDefined();
    }
    const bySlot = new Map(frame.atoms.map((a) => [a.slot_id, a.text]));
    expect(bySlot.get("T3.priority")).toBeUndefined();
    expect(bySlot.get("T2.lens_card")).toBeUndefined();
    expect(bySlot.get("T2.lens_number")).toBeUndefined();
    expect(bySlot.get("T2.catalog_card")).toBe("каталог карты");
  });
});

describe("TIC close-out forbidden-source + Glance scope", () => {
  const locked = [
    "src/app/today/page.tsx",
    "src/components/today/composition/TodayProductScreenFlow.tsx",
    "src/components/today/composition/TodayDayBrief.tsx",
    "src/components/today/composition/TodayMyDayPane.tsx",
    "src/components/today/composition/TodayRitualLensPair.tsx",
    "src/lib/todayK01HumanLine.ts",
    "src/lib/todayPersonalFocusAxis.ts",
    "src/lib/todayMyDayPriority.ts",
    "src/lib/todaySupportXor.ts",
    "src/lib/todayPracticeSelect.ts",
    "src/lib/ritualRevealCopy.ts",
  ];

  it("locked surfaces do not mount Glance leftover or PIC identity", () => {
    for (const rel of locked) {
      const text = readRel(rel);
      expect(text).not.toMatch(/TodayGlanceAct/);
      expect(text).not.toMatch(/P1\.recognition_line/);
      expect(text).not.toMatch(/compose_k01_identity/);
    }
    const surface = readRel("src/components/today/composition/TodayCompositionSurface.tsx");
    expect(surface).not.toMatch(/TodayGlanceAct/);
    expect(surface).not.toContain("{glanceSection}");
    expect(readRel("src/lib/todayPracticeSelect.ts")).not.toMatch(/GLOBAL_ENERGY_NEED/);
    expect(readRel("src/lib/todayPracticeSelect.ts")).toMatch(/PERSONAL_FOCUS_NEED/);
    expect(readRel("src/lib/todayPersonalFocusAxis.ts")).not.toMatch(/scenes/);
  });
});
