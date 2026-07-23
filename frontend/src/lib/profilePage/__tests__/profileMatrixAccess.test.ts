import {
  PROFILE_SLOT_HELPS,
  profileHelpsLineFromMatrix,
  profileSlotRevealed,
  profileUserMessages,
} from "../profileMatrixAccess";
import type { CoreProfile } from "@/lib/types";

describe("profileMatrixAccess", () => {
  it("reveals helps for trial and gates for free while keeping result eligibility", () => {
    const free = {
      capability: {
        profile_slots: {
          data_eligible: ["identity_summary", "helps"],
          revealed: ["identity_summary"],
          allowed: ["identity_summary"],
          access_gated: ["helps"],
        },
        user_messages: [{ code: "l3_gated", text: "В trial откроются конкретные опоры." }],
      },
      profile_matrix_v0: {
        slots: { helps: ["тишина перед решением"] },
        revealed_slots: {},
        access_gated_slot_ids: ["helps"],
      },
      profile_contract_v1: { helps: ["тишина перед решением"] },
    } as CoreProfile;

    const trial = {
      ...free,
      capability: {
        ...free.capability!,
        profile_slots: {
          data_eligible: ["identity_summary", "helps"],
          revealed: ["identity_summary", "helps"],
          allowed: ["identity_summary", "helps"],
          access_gated: [],
        },
      },
      profile_matrix_v0: {
        slots: { helps: ["тишина перед решением"] },
        revealed_slots: { helps: ["тишина перед решением"] },
        access_gated_slot_ids: [],
      },
    } as CoreProfile;

    expect(profileSlotRevealed(free, PROFILE_SLOT_HELPS)).toBe(false);
    expect(profileHelpsLineFromMatrix(free)).toBeNull();
    expect(profileUserMessages(free)[0]?.code).toBe("l3_gated");

    expect(profileSlotRevealed(trial, PROFILE_SLOT_HELPS)).toBe(true);
    expect(profileHelpsLineFromMatrix(trial)).toBe("тишина перед решением");
  });

  it("defaults to revealed when capability pack is absent (legacy)", () => {
    expect(profileSlotRevealed({} as CoreProfile, PROFILE_SLOT_HELPS)).toBe(true);
  });
});
