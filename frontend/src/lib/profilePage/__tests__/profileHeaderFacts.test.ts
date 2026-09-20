import { emitProfileDisplayFrame } from "@/lib/displayGrammar/emitProfileDisplayFrame";
import { profileHeaderFacts } from "@/lib/profilePage/profileHeaderFacts";
import type { CoreProfile } from "@/lib/types";

const namedBag = {
  expression: 3,
  soul_urge: 9,
  personality: 5,
};

describe("profileHeaderFacts PIC-K13", () => {
  it("reads live Matrix keys expression / soul_urge / personality", () => {
    const facts = profileHeaderFacts({
      profile_matrix_v0: { revealed_slots: { name_numerology: namedBag } },
    } as CoreProfile);
    expect(facts).toEqual([
      {
        slot_id: "P2.name_numerology",
        text: "Числа имени: выражение 3 · душа 9 · образ 5",
      },
    ]);
  });

  it("accepts *_number aliases without inventing missing values", () => {
    const facts = profileHeaderFacts({
      profile_matrix_v0: {
        revealed_slots: {
          name_numerology: {
            expression_number: 8,
            soul_urge_number: 1,
            personality_number: 7,
          },
        },
      },
    } as CoreProfile);
    expect(facts[0]?.text).toBe("Числа имени: выражение 8 · душа 1 · образ 7");
  });

  it("omits when IN.name is missing and does not invent numbers", () => {
    expect(profileHeaderFacts(null)).toEqual([]);
    expect(
      profileHeaderFacts({
        profile_matrix_v0: { revealed_slots: {} },
      } as CoreProfile),
    ).toEqual([]);
    expect(
      profileHeaderFacts({
        profile_matrix_v0: { revealed_slots: { name_numerology: {} } },
      } as CoreProfile),
    ).toEqual([]);
  });

  it("does not leak K13 into Identity Core / recognition", () => {
    const core = {
      profile_contract_v1: {
        contract_version: "v1",
        recognition_line: "Ты строишь через анализ до шага.",
        identity_core: "Ядро без чисел имени.",
        strengths: [],
        growth_zones: [],
        relationship_style: "",
        money_style: "",
        decision_style: "",
        recurring_patterns: [],
      },
      portrait_why_v0: {
        title: "Почему",
        selected_by: [{ id: "life_path", class: "selected_by", label: "7" }],
        portrait_influenced_by: [],
      },
      profile_matrix_v0: { revealed_slots: { name_numerology: namedBag } },
    } as CoreProfile;
    const frame = emitProfileDisplayFrame({ core });
    const name = frame.atoms?.find((a) => a.slot_id === "P2.name_numerology");
    const recognition = frame.atoms?.find((a) => a.slot_id === "P1.recognition_line");
    const identity = frame.atoms?.find((a) => a.slot_id === "P1.identity_core");
    expect(name?.text).toMatch(/выражение 3/);
    expect(recognition?.text).toBe("Ты строишь через анализ до шага.");
    expect(identity?.text).toBe("Ядро без чисел имени.");
    expect(recognition?.text).not.toMatch(/выражение|душа|образ/);
    expect(identity?.text).not.toMatch(/выражение|душа|образ/);
  });
});
