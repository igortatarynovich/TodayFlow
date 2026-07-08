import { buildProfileV0ViewModel } from "../buildProfileV0Data";
import {
  buildProfileChartFrameworkInput,
  buildProfileQuickMapViewModel,
} from "../buildProfileQuickMapData";
import { buildProfileFrameworkCards } from "../buildProfileFrameworkCards";
import { IGOR_SAGE_7_FIXTURE } from "../fixtures/igorSage7ProfileFixture";

describe("buildProfileQuickMapViewModel", () => {
  it("maps taxonomy slots into Quick Map sections", () => {
    const v0 = buildProfileV0ViewModel({
      core: IGOR_SAGE_7_FIXTURE,
      displayName: "Igor",
    });

    const frameworkCards = buildProfileFrameworkCards({
      sunLayer: { bullets: ["Системное мышление и независимость."] } as never,
      moonLayer: { bullets: ["Восстановление через тишину."] } as never,
      risingLayer: { bullets: ["Сдержанный первый контакт."] } as never,
      risingSign: "Дева",
      risingHint: "Асцендент уточняется по времени рождения.",
      mcSign: "Близнецы",
      sunSignDisplay: "Водолей",
      lifePath: 7,
      lifePathBody: "Поиск смысла и глубины.",
      archetypeLabel: "Sage",
      archetypeBody: "Архетип мудреца.",
    });

    const quickMap = buildProfileQuickMapViewModel(
      v0,
      buildProfileChartFrameworkInput({
        sunSignDisplay: "Водолей",
        risingSign: "Дева",
        mcSign: "Близнецы",
        lifePath: 7,
        archetypeLabel: "Sage",
        chartCards: frameworkCards,
      }),
    );

    expect(quickMap.archetype).toBe("Sage");
    expect(quickMap.identitySummary).toBeTruthy();
    expect(quickMap.strengthens.length).toBeGreaterThan(0);
    expect(quickMap.frameworkAnchors.map((item) => item.label)).toEqual(
      expect.arrayContaining(["Солнце в Водолей", "Архетип Sage", "Число пути 7"]),
    );
    expect(quickMap.frameworkCards.some((card) => card.id === "sun")).toBe(true);
  });

  it("merges CUM identity strengths and summary into Quick Map", () => {
    const v0 = buildProfileV0ViewModel({
      core: { ...IGOR_SAGE_7_FIXTURE, interpretation: undefined },
      displayName: "Igor",
    });

    const quickMap = buildProfileQuickMapViewModel(
      v0,
      buildProfileChartFrameworkInput({
        sunSignDisplay: "Водолей",
        risingSign: null,
        mcSign: null,
        lifePath: 7,
        archetypeLabel: "",
        chartCards: [],
      }),
      {
        contract_version: "compact_user_model_v0",
        as_of: "2026-07-03",
        generated_at: "2026-07-03T12:00:00",
        identity: {
          archetype: "Sage",
          summary: "Из CUM: короткое резюме личности.",
          strengths: ["ясность структуры"],
          constraints: ["хаос без правил"],
        },
        current_state: {},
        active_themes: [],
        behavioral_patterns: {},
        knowledge_atoms_top_k: [],
        confidence: { overall: 0.5, uncertainty_flags: [] },
      },
    );

    expect(quickMap.archetype).toBe("Sage");
    expect(quickMap.strengthens[0]).toBe("ясность структуры");
    expect(quickMap.drains[0]).toBe("хаос без правил");
  });

  it("merges CUM behavioral patterns and atoms into Quick Map", () => {
    const v0 = buildProfileV0ViewModel({
      core: IGOR_SAGE_7_FIXTURE,
      displayName: "Igor",
    });

    const quickMap = buildProfileQuickMapViewModel(
      v0,
      buildProfileChartFrameworkInput({
        sunSignDisplay: "Водолей",
        risingSign: "Дева",
        mcSign: "Близнецы",
        lifePath: 7,
        archetypeLabel: "Sage",
        chartCards: [],
      }),
      {
        contract_version: "compact_user_model_v0",
        as_of: "2026-07-03",
        generated_at: "2026-07-03T12:00:00",
        identity: {},
        current_state: {},
        active_themes: [],
        behavioral_patterns: {
          works: ["evening_reflection"],
          does_not_work: ["morning_overload"],
        },
        knowledge_atoms_top_k: [
          {
            knowledge_id: "profile-strength-0",
            claim_summary: "спокойствие под давлением",
          },
        ],
        confidence: { overall: 0.5, uncertainty_flags: [] },
      },
    );

    expect(quickMap.strengthens[0]).toBe("evening_reflection");
    expect(quickMap.drains[0]).toBe("morning_overload");
  });

  it("adds moon and rising anchors from CUM identity when missing", () => {
    const v0 = buildProfileV0ViewModel({
      core: IGOR_SAGE_7_FIXTURE,
      displayName: "Igor",
    });

    const quickMap = buildProfileQuickMapViewModel(
      v0,
      buildProfileChartFrameworkInput({
        sunSignDisplay: "Водолей",
        risingSign: null,
        mcSign: null,
        lifePath: 7,
        archetypeLabel: "Sage",
        chartCards: [],
      }),
      {
        contract_version: "compact_user_model_v0",
        as_of: "2026-07-03",
        generated_at: "2026-07-03T12:00:00",
        identity: {
          moon_sign: "Рыбы",
          rising_sign: "Дева",
        },
        current_state: {},
        active_themes: [],
        behavioral_patterns: {},
        knowledge_atoms_top_k: [],
        confidence: { overall: 0.5, uncertainty_flags: [] },
      },
    );

    expect(quickMap.frameworkAnchors.map((item) => item.label)).toEqual(
      expect.arrayContaining(["Луна в Рыбы", "Асцендент в Дева"]),
    );
  });
});

describe("profileCopyToBullets", () => {
  it("splits semicolon lists", async () => {
    const { profileCopyToBullets } = await import("../profileCopyBullets");
    expect(profileCopyToBullets("ясность; свобода; системы", 3)).toEqual([
      "ясность",
      "свобода",
      "системы",
    ]);
  });
});
