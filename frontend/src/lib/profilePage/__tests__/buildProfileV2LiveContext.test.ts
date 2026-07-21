import {
  buildProfileV2LiveContext,
  resolveObservationAccuracy,
  resolveProfileSourceDepth,
  resolveProfileV2AwarenessPercent,
} from "../buildProfileV2LiveContext";
import type { CompactUserModel, CoreProfile } from "@/lib/types";

describe("buildProfileV2LiveContext", () => {
  it("prefers CUM confidence for awareness percent helper", () => {
    const cum = { confidence: { overall: 0.68 } } as CompactUserModel;
    expect(
      resolveProfileV2AwarenessPercent({ cum, coreProfile: null, localClosedDays: 0 }),
    ).toBe(68);
  });

  it("does not fabricate awareness percent without CUM confidence", () => {
    expect(
      resolveProfileV2AwarenessPercent({
        cum: null,
        coreProfile: { living: { signal_profile: { signals_days: 5 } } } as CoreProfile,
        localClosedDays: 3,
      }),
    ).toBeNull();
  });

  it("maps evidence to qualitative observation accuracy levels", () => {
    expect(
      resolveObservationAccuracy({
        cum: { confidence: { overall: 0.68 } } as CompactUserModel,
        coreProfile: null,
      }).level,
    ).toBe("stable");

    expect(
      resolveObservationAccuracy({
        cum: null,
        coreProfile: null,
        localClosedDays: 0,
      }).level,
    ).toBe("initial");
  });

  it("resolves source_depth ladder from birth and check-ins", () => {
    expect(
      resolveProfileSourceDepth({
        coreProfile: { astro: { sun_sign: "Virgo" } } as CoreProfile,
        cum: null,
        localClosedDays: 0,
      }),
    ).toBe("birth_data_only");

    expect(
      resolveProfileSourceDepth({
        coreProfile: {
          astro: { sun_sign: "Virgo" },
          baseline: { archetype_seed: "explorer" },
          living: { signal_profile: { signals_days: 4 } },
        } as CoreProfile,
        cum: null,
        localClosedDays: 0,
      }),
    ).toBe("profile_plus_checkins");
  });

  it("builds Evidence without day anchors or day recommendations", () => {
    const cum = {
      generated_at: "2026-07-07T07:14:00.000Z",
      confidence: { overall: 0.68, delta_30d: 0.03 },
      recommendations: { primary: { id: "p1", text: "Один сложный разговор до 14:00." } },
      behavioral_patterns: { hints: ["точность", "глубина"], works: [], does_not_work: [] },
    } as CompactUserModel;

    const live = buildProfileV2LiveContext({
      coreProfile: {
        generated_at: "2026-07-06T10:00:00.000Z",
        astro: { sun_sign: "Virgo", sun_element: "earth" },
        profile_contract_v1: {
          contract_version: "v1",
          identity_core: "Ясный фокус",
          strengths: [],
          growth_zones: [],
          relationship_style: "",
          money_style: "",
          decision_style: "",
          recurring_patterns: [],
          helps: ["ритм без спешки"],
        },
      } as CoreProfile,
      cum,
      thriveAreas: ["глубина"],
    });

    expect(live.sourceDepth).toBe("onboarding_answers");
    expect(live.evidenceBody).toContain("ответы при старте");
    expect(live.evidenceTitle).toBeTruthy();
    expect(live.helps).toEqual(["ритм без спешки", "глубина"]);
    expect(live.helps.join(" ")).not.toContain("разговор");
    expect(live.elementLabel).toContain("Стихия");
    expect(live).not.toHaveProperty("hasStoneCard");
    expect(live).not.toHaveProperty("dailyAnchors");
    expect(live).not.toHaveProperty("updatedLabel");
  });

  it("keeps evidence honest when data is missing", () => {
    const live = buildProfileV2LiveContext({
      coreProfile: null,
      cum: null,
    });

    expect(live.sourceDepth).toBe("birth_data_only");
    expect(live.observationAccuracyLabel).toBe("первые контуры");
    expect(live.helps).toEqual([]);
    expect(live.evidenceNextStep).toBeTruthy();
  });
});
