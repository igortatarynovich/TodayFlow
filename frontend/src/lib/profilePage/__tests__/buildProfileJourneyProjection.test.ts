import { buildProfileJourneyProjection } from "../buildProfileJourneyProjection";
import type { CoreProfile } from "@/lib/types";

describe("buildProfileJourneyProjection", () => {
  it("maps Steps 1–5 and prefers journey surface when recognition + why exist", () => {
    const core = {
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
      profile_matrix_v0: {
        revealed_slots: {
          cultural_catalog: { color: "изумрудный", traditions: [], stones: [] },
          natal_structure: {
            angles: { ascendant: { sign: "Leo" } },
            houses: Array.from({ length: 12 }, (_, i) => ({ cusp: i + 1 })),
          },
          tensions_growth: { growth_zones: ["спешка"] },
          helps: ["тишина"],
          emotional_style: "Чувствует глубже.",
        },
      },
    } as CoreProfile;

    const journey = buildProfileJourneyProjection(core);
    expect(journey.hasJourneySurface).toBe(true);
    expect(journey.recognition.name).toMatch(/Исследователь/i);
    expect(journey.recognition.line).toContain("структуру");
    expect(journey.identityMarkers).toEqual(["Дева", "Земля", "Путь 7"]);
    expect(journey.identityMarkers).toHaveLength(3);
    expect(journey.why?.selectedBy).toHaveLength(1);
    expect(journey.why?.influencedBy[0]?.label).toContain("Дев");
    expect(journey.insightNode?.title).toBe("Ясность vs скорость");
    expect(journey.insightNode?.livingEvidence).toEqual(["снова сорвался в спешку"]);
    expect(journey.effortVector).toContain("тихий проход");
    expect(journey.bridge?.leadsTo).toBe("today");

    // Matrix catalog/natal go to progressiveDetails — not Journey IA order.
    expect(journey.progressiveDetails.map((d) => d.id)).toContain("cultural_catalog");
    expect(journey.progressiveDetails.map((d) => d.id)).toContain("natal_structure");
    expect(journey.progressiveDetails.map((d) => d.id)).toContain("emotional_style");
    // Consumed by insight node — omitted from explore lists.
    expect(journey.progressiveDetails.map((d) => d.id)).not.toContain("tensions_growth");
    expect(journey.progressiveDetails.map((d) => d.id)).not.toContain("helps");
    // Natal explore must not dump cusp counts.
    const natal = journey.progressiveDetails.find((d) => d.id === "natal_structure");
    expect(natal?.lines.join(" ")).not.toMatch(/12 куспид/i);
  });

  it("omits null steps and does not invent effort/bridge/markers", () => {
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

    expect(journey.recognition.line).toBeNull();
    expect(journey.insightNode).toBeNull();
    expect(journey.effortVector).toBeNull();
    expect(journey.bridge).toBeNull();
    expect(journey.identityMarkers).toEqual([]);
    expect(journey.hasJourneySurface).toBe(false);
  });

  it("does not treat matrix slot order as journey surface alone", () => {
    const journey = buildProfileJourneyProjection({
      profile_matrix_v0: {
        revealed_slots: {
          cultural_catalog: { color: "золото", traditions: [], stones: [] },
          emotional_style: "Стиль.",
        },
      },
    } as CoreProfile);

    expect(journey.hasJourneySurface).toBe(false);
    expect(journey.progressiveDetails.map((d) => d.id)).toEqual([
      "cultural_catalog",
      "emotional_style",
    ]);
  });
});
