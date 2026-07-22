import { buildProfileJourneyProjection } from "../buildProfileJourneyProjection";
import type { CoreProfile } from "@/lib/types";

describe("buildProfileJourneyProjection", () => {
  it("maps Steps 1–5 and prefers journey surface when recognition + why exist", () => {
    const core = {
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
          {
            id: "life_path",
            class: "selected_by",
            label: "Число пути 7 → Исследователь",
          },
        ],
        portrait_influenced_by: [
          { id: "sun", class: "portrait_influenced_by", label: "Солнце в Деве" },
        ],
        honesty_line: "Часть картины ещё уточнится с отмеченными днями.",
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

    const journey = buildProfileJourneyProjection(core);
    expect(journey.hasJourneySurface).toBe(true);
    expect(journey.recognitionName).toMatch(/Исследователь/i);
    expect(journey.recognitionLine).toContain("структуру");
    expect(journey.whySelectedBy).toHaveLength(1);
    expect(journey.whyInfluencedBy[0]?.label).toContain("Дев");
    expect(journey.node?.title).toBe("Ясность vs скорость");
    expect(journey.node?.livingEvidence).toEqual(["снова сорвался в спешку"]);
    expect(journey.effortVector).toContain("тихий проход");
    expect(journey.bridgeLeadsTo).toBe("today");
  });

  it("omits null steps and does not invent effort/bridge", () => {
    const journey = buildProfileJourneyProjection({
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
    } as CoreProfile);

    expect(journey.recognitionLine).toBeNull();
    expect(journey.node).toBeNull();
    expect(journey.effortVector).toBeNull();
    expect(journey.bridgeLine).toBeNull();
    expect(journey.hasJourneySurface).toBe(false);
  });
});
