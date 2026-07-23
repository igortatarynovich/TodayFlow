import { buildProfileProgressiveDetailsProjection } from "../buildProfileProgressiveDetailsProjection";
import type { CoreProfile } from "@/lib/types";

function coreWithSlots(revealed: Record<string, unknown>, accessGated: string[] = []): CoreProfile {
  return {
    profile_version: "test",
    generated_at: "2026-01-01T00:00:00Z",
    is_ready: true,
    missing_fields: [],
    profile_hash: "h",
    person: {},
    astro: {},
    numerology: {},
    baseline: {},
    capability: {
      access: "free",
      profile_slots: {
        revealed: Object.keys(revealed),
        data_eligible: [...Object.keys(revealed), ...accessGated],
        access_gated: accessGated,
      },
      user_messages: accessGated.includes("helps")
        ? [{ code: "l3_gated", text: "Глубина откроется в пробном периоде." }]
        : [],
    },
    profile_matrix_v0: {
      revealed_slots: revealed,
      access_gated_slot_ids: accessGated,
      slots: { ...revealed },
    },
  } as CoreProfile;
}

describe("buildProfileProgressiveDetailsProjection", () => {
  it("builds explore items without identity/sun journey slots", () => {
    const details = buildProfileProgressiveDetailsProjection(
      coreWithSlots({
        identity_summary: "Держит ясность через ритм.",
        sun_element_numerology: { sun_sign: "taurus", element: "earth", life_path: 7 },
        cultural_catalog: {
          color: "изумрудный",
          traditions: [{ id: "chinese", label: "Китайский", value: "Лошадь · металл" }],
          stones: [{ id: "emerald", label: "изумруд" }],
        },
        emotional_style: "Чувствует глубже.",
        helps: ["Утро без экрана"],
      }),
    );
    expect(details.hasMatrix).toBe(true);
    expect(details.items.map((c) => c.id)).toEqual([
      "cultural_catalog",
      "emotional_style",
      "helps",
    ]);
    expect(details.items.map((c) => c.id)).not.toContain("identity_summary");
    expect(details.items.map((c) => c.id)).not.toContain("sun_element_numerology");
  });

  it("surfaces L3 gate message when helps access-gated", () => {
    const details = buildProfileProgressiveDetailsProjection(
      coreWithSlots(
        {
          emotional_style: "Стиль.",
        },
        ["helps"],
      ),
    );
    expect(details.accessGatedHelps).toBe(true);
    expect(details.userMessages.some((m) => m.code === "l3_gated")).toBe(true);
    expect(details.items.find((c) => c.id === "helps")).toBeUndefined();
  });

  it("omits slots listed in omitSlotIds", () => {
    const details = buildProfileProgressiveDetailsProjection(
      coreWithSlots({
        cultural_catalog: { color: "золото", traditions: [], stones: [] },
        helps: ["опора"],
        strengths: ["глубина"],
      }),
      { omitSlotIds: ["helps", "strengths"] },
    );
    expect(details.items.map((c) => c.id)).toEqual(["cultural_catalog"]);
  });
});
