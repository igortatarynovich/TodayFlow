import { postJson } from "@/lib/api";
import {
  narrativeProfileSelectorPayload,
  postTodayNarrative,
  TODAY_NARRATIVE_POLICY_VERSION,
  TODAY_NARRATIVE_VOICE_PROFILE,
} from "@/lib/todayNarrativeApi";

jest.mock("@/lib/api", () => ({
  postJson: jest.fn(),
}));

const mockedPostJson = postJson as jest.MockedFunction<typeof postJson>;

describe("postTodayNarrative", () => {
  it("sends policy and voice contract fields", async () => {
    mockedPostJson.mockResolvedValueOnce({
      generation_id: 101,
      generation_log_id: 101,
      surface: "guide",
      used_fallback: false,
      payload: {},
    });

    await postTodayNarrative({
      target_date: "2026-04-25",
      surface: "guide",
    });

    expect(mockedPostJson).toHaveBeenCalledWith("/today/narrative", {
      target_date: "2026-04-25",
      surface: "guide",
      policy_version: TODAY_NARRATIVE_POLICY_VERSION,
      voice_profile: TODAY_NARRATIVE_VOICE_PROFILE,
    });
  });

  it("narrativeProfileSelectorPayload accepts slim dict", () => {
    expect(narrativeProfileSelectorPayload({ task: "x" })).toEqual({ task: "x" });
    expect(narrativeProfileSelectorPayload(null)).toBeNull();
    expect(narrativeProfileSelectorPayload([])).toBeNull();
  });
});
