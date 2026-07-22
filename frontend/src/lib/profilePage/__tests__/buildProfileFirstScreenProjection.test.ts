import { buildProfileFirstScreenProjection } from "@/lib/profilePage/buildProfileFirstScreenProjection";

describe("buildProfileFirstScreenProjection", () => {
  it("maps recognition, three traits, contradiction, and helps without kitchen fields", () => {
    const first = buildProfileFirstScreenProjection({
      baseline: { archetype_seed: "explorer" },
      profile_contract_v1: {
        contract_version: "v1",
        recognition_line: "Ты первым видишь структуру.",
        identity_core: "Ядро.",
        strengths: ["система"],
        growth_zones: ["спешка ломает точность"],
        relationship_style: "Сначала доверие, потом открытость.",
        money_style: "",
        decision_style: "Сначала тело, потом структура.",
        recurring_patterns: ["нужна ясность"],
        helps: ["тишина"],
      },
      insight_nodes_v0: {
        nodes: [
          {
            id: "n1",
            kind: "tension",
            title: "Ясность vs скорость",
            insight: "Сила в точности.",
            help: "Один тихий проход.",
          },
        ],
      },
      effort_vector_v0: { effort_vector: "Один тихий проход." },
      bridge_line_v0: { bridge_line: "Дальше — Today.", leads_to: "today" },
    } as never);

    expect(first.whoLine).toContain("структуру");
    expect(first.traits.map((t) => t.id)).toEqual(["decisions", "intimacy", "self_friction"]);
    expect(first.contradiction?.title).toBe("Ясность vs скорость");
    expect(first.helpsLine).toContain("тихий");
    expect(first.bridgeLine).toContain("Today");
  });
});
