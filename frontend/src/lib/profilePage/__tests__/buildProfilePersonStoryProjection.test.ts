import { buildProfilePersonStoryProjection } from "../buildProfilePersonStoryProjection";
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

describe("buildProfilePersonStoryProjection", () => {
  it("orders chapters top→bottom and omits empty", () => {
    const story = buildProfilePersonStoryProjection(
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
    expect(story.hasMatrix).toBe(true);
    expect(story.identityLine).toContain("ясность");
    expect(story.chapters.map((c) => c.id)).toEqual([
      "identity_summary",
      "sun_element_numerology",
      "cultural_catalog",
      "emotional_style",
      "helps",
    ]);
  });

  it("surfaces L3 gate message when helps access-gated", () => {
    const story = buildProfilePersonStoryProjection(
      coreWithSlots(
        {
          identity_summary: "Линия.",
          emotional_style: "Стиль.",
        },
        ["helps"],
      ),
    );
    expect(story.accessGatedHelps).toBe(true);
    expect(story.userMessages.some((m) => m.code === "l3_gated")).toBe(true);
    expect(story.chapters.find((c) => c.id === "helps")).toBeUndefined();
  });
});
