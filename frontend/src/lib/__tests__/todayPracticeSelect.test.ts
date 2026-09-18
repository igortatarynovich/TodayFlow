import {
  catalogPracticeFromSelection,
  fetchCatalogPracticeForEnergy,
  needQueryFromPrimaryEnergy,
} from "@/lib/todayPracticeSelect";
import { getJson } from "@/lib/api";

jest.mock("@/lib/api", () => {
  const actual = jest.requireActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    getJson: jest.fn(),
  };
});

const getJsonMock = getJson as jest.MockedFunction<typeof getJson>;

describe("todayPracticeSelect", () => {
  beforeEach(() => {
    getJsonMock.mockReset();
  });

  it("maps the closed 8-set energy to a coverage need cell", () => {
    expect(needQueryFromPrimaryEnergy("tension")).toEqual({
      purpose: "calm",
      direction: "downregulate",
    });
    expect(needQueryFromPrimaryEnergy("clarity")).toEqual({
      purpose: "clarity",
      direction: "reflect",
    });
    expect(needQueryFromPrimaryEnergy("unknown")).toBeNull();
  });

  it("omits unmatched catalog selections", () => {
    expect(
      catalogPracticeFromSelection({
        item_id: null,
        title: "",
        body: "",
        outcome_label: "",
        duration: null,
        matched: false,
        reason: "no_hard_tag_match",
      }),
    ).toBeNull();
  });

  it("fetches GET /practices/select and returns a catalog practice", async () => {
    getJsonMock.mockResolvedValue({
      item_id: "practice.extended_exhale.001",
      title: "Выдох длиннее вдоха",
      body: "Сделать выдох длиннее вдоха.",
      outcome_label: "Снять напряжение",
      duration: 3,
      matched: true,
      reason: "purpose=calm",
    });
    const practice = await fetchCatalogPracticeForEnergy("tension");
    expect(getJsonMock).toHaveBeenCalledWith(
      "/practices/select?purpose=calm&direction=downregulate&locale=ru",
    );
    expect(practice?.id).toBe("practice.extended_exhale.001");
    expect(practice?.title).toBe("Выдох длиннее вдоха");
  });

  it("does not invent a practice when energy is missing", async () => {
    await expect(fetchCatalogPracticeForEnergy(null)).resolves.toBeNull();
    expect(getJsonMock).not.toHaveBeenCalled();
  });
});
