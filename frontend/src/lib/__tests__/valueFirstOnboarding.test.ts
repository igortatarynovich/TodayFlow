import { buildFirstResultModel } from "@/lib/buildFirstResultModel";
import { buildOnboardingPreviewModel } from "@/lib/buildOnboardingPreview";
import { chineseZodiacFromIsoDate } from "@/lib/chineseZodiacFromDate";
import {
  beginGuestOnboardingSession,
  patchGuestProfileDraft,
  readGuestProfileDraft,
} from "@/lib/guestProfileDraft";
import { textSimilarity } from "@/lib/interpretation/formatRecognitionText";
import { sunSignFromIsoDate } from "@/lib/sunSignFromDate";

describe("first result model", () => {
  beforeEach(() => {
    window.localStorage.clear();
    window.sessionStorage.clear();
  });

  const aquariusSevenDraft = () =>
    patchGuestProfileDraft({
      first_name: "Igor",
      birth_date: "2000-01-20",
      sun_sign: "Aquarius",
      life_path: 7,
    });

  it("builds reward screen sections from interpretation engine", () => {
    const model = buildFirstResultModel(aquariusSevenDraft());

    expect(model.heroTitle).toContain("Igor");
    expect(model.keyInfluences.length).toBeGreaterThanOrEqual(4);
    expect(model.keyInfluences.some((t) => t.id === "sun" && t.value === "Водолей")).toBe(true);
    expect(model.keyInfluences.some((t) => t.id === "life_path" && t.value === "7")).toBe(true);
    expect(model.portraitCards.length).toBe(4);
    expect(model.dominantTrait.headline.length).toBeGreaterThan(20);
    expect(model.audit.candidateCount).toBeGreaterThan(10);
    expect(model.closingMessage).toMatch(/начало|первый день/i);
    expect(model.nameInsight?.tiles.length).toBeGreaterThanOrEqual(2);
    expect(model.saveCtaLabel).toMatch(/сохранить/i);
    expect(model.refineCtaLabel).toMatch(/время/i);
  });

  it("uses distinct why explanations per visible card", () => {
    const model = buildFirstResultModel(aquariusSevenDraft());
    const whys = model.portraitCards.map((c) => c.whyExplanation);
    const unique = new Set(whys);

    expect(unique.size).toBe(whys.length);
    expect(model.dominantTrait.whyExplanation).not.toBe(whys[0]);
  });

  it("keeps portrait card bodies distinct from each other", () => {
    const model = buildFirstResultModel(aquariusSevenDraft());
    const bodies = model.portraitCards.map((c) => c.body);

    for (let i = 0; i < bodies.length; i++) {
      for (let j = i + 1; j < bodies.length; j++) {
        expect(textSimilarity(bodies[i], bodies[j])).toBeLessThan(0.45);
      }
    }
  });

  it("includes domain-language why explanations without system jargon", () => {
    const model = buildFirstResultModel(aquariusSevenDraft());
    const joined = [
      model.globalWhySummary,
      ...model.portraitCards.map((c) => c.whyExplanation),
      model.dominantTrait.whyExplanation,
      model.surprise?.whyExplanation ?? "",
    ]
      .join(" ")
      .toLowerCase();

    expect(joined).not.toMatch(/алгоритм|ии|pim|модель|вычисл|анализировали/);
    expect(model.globalWhySummary).toMatch(/водолей|число пути|стихия/i);
  });

  it("buildOnboardingPreviewModel delegates to first result", () => {
    const model = buildOnboardingPreviewModel(aquariusSevenDraft());
    expect(model.displayName).toBe("Igor");
    expect(model.portraitCards.length).toBe(4);
  });

  it("resolves sun sign from ISO date", () => {
    expect(sunSignFromIsoDate("1990-05-15")).toBe("Taurus");
    expect(sunSignFromIsoDate("2000-01-20")).toBe("Aquarius");
  });

  it("resolves chinese zodiac from birth date", () => {
    const profile = chineseZodiacFromIsoDate("2000-01-20");
    expect(profile?.animalRu).toBeTruthy();
    expect(profile?.traits.length).toBeGreaterThanOrEqual(2);
  });
});

describe("guest profile draft session", () => {
  beforeEach(() => {
    window.localStorage.clear();
    window.sessionStorage.clear();
  });

  it("stores in-progress draft in sessionStorage, not localStorage", () => {
    patchGuestProfileDraft({ first_name: "Anna", birth_date: "1992-03-03" });

    expect(window.sessionStorage.getItem("todayflow_guest_profile_session_v1")).toBeTruthy();
    expect(window.localStorage.getItem("todayflow_guest_profile_draft_v1")).toBeNull();
    expect(readGuestProfileDraft()?.first_name).toBe("Anna");
  });

  it("beginGuestOnboardingSession clears in-progress draft", () => {
    patchGuestProfileDraft({ first_name: "Anna", birth_date: "1992-03-03" });
    beginGuestOnboardingSession();

    expect(readGuestProfileDraft()).toBeNull();
    expect(window.localStorage.getItem("todayflow_guest_profile_draft_v1")).toBeNull();
  });
});
