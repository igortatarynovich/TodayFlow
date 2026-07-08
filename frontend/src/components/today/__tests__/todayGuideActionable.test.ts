import {
  guideCanonicalPrimaryStepLine,
  parseDayEngineBriefFromGuide,
  parseDayModelBriefFromGuide,
  parseGuidePipelineFromGuide,
  parseNarrativeHierarchyFromGuide,
} from "@/components/today/todayGuideActionable";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

describe("parseDayEngineBriefFromGuide", () => {
  it("returns null without anchor_summary", () => {
    expect(parseDayEngineBriefFromGuide(null)).toBeNull();
    expect(parseDayEngineBriefFromGuide({ day_engine_brief: {} })).toBeNull();
  });

  it("parses anchor and hints", () => {
    const b = parseDayEngineBriefFromGuide({
      day_engine_brief: {
        anchor_summary: "  Ось дня  ",
        do_hint: "Шаг 1",
        tempo_hint: "Темп",
      },
    });
    expect(b).toEqual({ anchor: "Ось дня", hints: ["Шаг 1", "Темп"] });
  });
});

describe("parseNarrativeHierarchyFromGuide (O2)", () => {
  it("returns null when missing or wrong contract", () => {
    expect(parseNarrativeHierarchyFromGuide(null)).toBeNull();
    expect(parseNarrativeHierarchyFromGuide({})).toBeNull();
    expect(
      parseNarrativeHierarchyFromGuide({
        narrative_hierarchy: { contract_version: "other", primary_anchor: "day_engine_brief" },
      }),
    ).toBeNull();
  });

  it("parses narrative_hierarchy_v0", () => {
    expect(
      parseNarrativeHierarchyFromGuide({
        narrative_hierarchy: { contract_version: "narrative_hierarchy_v0", primary_anchor: "day_engine_brief" },
      }),
    ).toEqual({ contractVersion: "narrative_hierarchy_v0", primaryAnchorKey: "day_engine_brief" });
  });
});

describe("parseGuidePipelineFromGuide (guide_contract_v2)", () => {
  it("returns null without guide_contract_v2", () => {
    expect(parseGuidePipelineFromGuide(null)).toBeNull();
    expect(parseGuidePipelineFromGuide({ guide_pipeline: { contract_version: "guide_pipeline_v0" } })).toBeNull();
  });

  it("parses funnel pipeline with core source", () => {
    expect(
      parseGuidePipelineFromGuide({
        contract_version: "guide_contract_v2",
        guide_pipeline: {
          contract_version: "guide_pipeline_v0",
          generation_mode: "funnel",
          steps: { core_text: { source: "funnel_core_text_v0" } },
        },
      }),
    ).toEqual({
      contractVersion: "guide_pipeline_v0",
      generationMode: "funnel",
      coreSource: "funnel_core_text_v0",
    });
  });
});

describe("parseDayModelBriefFromGuide", () => {
  it("returns null without contract or one_focus", () => {
    expect(parseDayModelBriefFromGuide(null)).toBeNull();
    expect(parseDayModelBriefFromGuide({})).toBeNull();
    expect(parseDayModelBriefFromGuide({ day_model: { contract_version: "other" } })).toBeNull();
    expect(parseDayModelBriefFromGuide({ day_model: { contract_version: "day_model_v0", strategy: {} } })).toBeNull();
  });

  it("parses day_model_v0 strategy.one_focus and vector.summary", () => {
    const dm = parseDayModelBriefFromGuide({
      day_model: {
        contract_version: "day_model_v0",
        vector: { summary: "Вектор дня", direction: "completion" },
        strategy: { one_focus: "Закрыть одну задачу", summary: "x" },
        scales: { tempo: "steady" },
      },
    });
    expect(dm).toEqual({
      contractVersion: "day_model_v0",
      oneFocus: "Закрыть одну задачу",
      vectorSummary: "Вектор дня",
      tensionSummary: undefined,
      riskSummary: undefined,
      tempoLabel: "steady",
    });
  });
});

describe("guideCanonicalPrimaryStepLine (O9)", () => {
  it("prefers structured core_message.best_move when not redundant with body", () => {
    expect(
      guideCanonicalPrimaryStepLine(
        {
          core_message: {
            body: "Сегодня держи фокус на одной задаче.",
            best_move: "Закрой один блок до обеда.",
          },
        },
        [],
        "",
      ),
    ).toBe("Закрой один блок до обеда.");
  });

  it("skips best_move when semantically redundant with body", () => {
    const body = "Сделай один короткий шаг по главному фокусу сегодня.";
    expect(
      guideCanonicalPrimaryStepLine(
        {
          core_message: { body, best_move: body },
          action_options: [{ title: "Первый вариант из списка" }],
        },
        ["Из do_items"],
        "",
      ),
    ).toBe("Первый вариант из списка");
  });

  it("uses first action_options title when no usable best_move", () => {
    expect(
      guideCanonicalPrimaryStepLine(
        { action_options: [{ title: "  Шаг из опций  " }] },
        ["Игнор"],
        "",
      ),
    ).toBe("Шаг из опций");
  });

  it("uses first do_items from payload before fallback array", () => {
    expect(
      guideCanonicalPrimaryStepLine({ do_items: ["Из payload", "Второй"] }, ["Из fallback"], ""),
    ).toBe("Из payload");
  });

  it("uses first non-empty fallback when payload has no do_items", () => {
    expect(guideCanonicalPrimaryStepLine({}, ["  ", "Из фолбэка"], "")).toBe("Из фолбэка");
  });

  it("uses literal then RITUAL_COPY when nothing else", () => {
    expect(guideCanonicalPrimaryStepLine({}, [], "  Явный фолбэк  ")).toBe("Явный фолбэк");
    expect(guideCanonicalPrimaryStepLine({}, [], "")).toBe(RITUAL_COPY.guidePrimaryDoFallback);
  });
});
