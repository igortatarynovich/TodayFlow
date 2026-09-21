import {
  catalogPracticeFromSelection,
  contentClassFromFocusAxis,
  fetchCatalogPracticeForFocusAxis,
  needQueryFromFocusAxis,
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

  it("maps the closed F10 4-set to a coverage need cell", () => {
    expect(needQueryFromFocusAxis("work")).toEqual({
      purpose: "decision_making",
      direction: "focus",
      context: "work",
    });
    expect(needQueryFromFocusAxis("money")).toEqual({
      purpose: "clarity",
      direction: "reflect",
      context: "money",
    });
    expect(needQueryFromFocusAxis("relationships")).toEqual({
      purpose: "connection",
      direction: "connect",
      context: "relationships",
    });
    expect(needQueryFromFocusAxis("energy")).toEqual({
      purpose: "grounding",
      direction: "stabilize",
      context: "body",
    });
    expect(needQueryFromFocusAxis("tension")).toBeNull();
    expect(needQueryFromFocusAxis("clarity")).toBeNull();
    expect(needQueryFromFocusAxis("radiance")).toBeNull();
    expect(needQueryFromFocusAxis(null)).toBeNull();
    expect(contentClassFromFocusAxis("work")).toBe("practice");
    expect(contentClassFromFocusAxis("relationships")).toBe("practice");
    expect(contentClassFromFocusAxis("tension")).toBeNull();
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

  it("fetches GET /practices/select from Personal focus, not Global energy", async () => {
    getJsonMock.mockResolvedValue({
      item_id: "practice.intention_setting.001",
      title: "Намерение на час",
      body: "Одно намерение.",
      outcome_label: "Собрать внимание",
      duration: 3,
      matched: true,
      reason: "purpose=decision_making",
    });
    const practice = await fetchCatalogPracticeForFocusAxis("work");
    expect(getJsonMock).toHaveBeenCalledWith(
      "/practices/select?purpose=decision_making&direction=focus&context=work&content_class=practice&locale=ru",
    );
    expect(practice?.id).toBe("practice.intention_setting.001");
    expect(practice?.title).toBe("Намерение на час");
  });

  it("does not invent a practice when Personal focus_axis is missing", async () => {
    await expect(fetchCatalogPracticeForFocusAxis(null)).resolves.toBeNull();
    await expect(fetchCatalogPracticeForFocusAxis("momentum")).resolves.toBeNull();
    expect(getJsonMock).not.toHaveBeenCalled();
  });
});
