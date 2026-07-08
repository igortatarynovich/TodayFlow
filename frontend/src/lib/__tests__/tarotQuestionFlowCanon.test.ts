import {
  composeTarotQuestion,
  buildTarotRitualHref,
  rankSpreadOffersForConcern,
} from "@/lib/tarotQuestionFlowCanon";

describe("tarotQuestionFlowCanon", () => {
  it("prefers custom question over domain seed", () => {
    expect(
      composeTarotQuestion({
        concernDomain: "work",
        refinementId: "stay_or_leave",
        customQuestion: "Стоит ли менять работу?",
      }),
    ).toBe("Стоит ли менять работу?");
  });

  it("uses refinement seed when no custom text", () => {
    expect(
      composeTarotQuestion({
        concernDomain: "relationships",
        refinementId: "ex_partner",
        customQuestion: "",
      }),
    ).toContain("бывш");
  });

  it("ranks relationship spreads first for relationships domain", () => {
    const offers = rankSpreadOffersForConcern("relationships");
    expect(offers[0]?.spreadId).toBe("guidance_relationship_five");
  });

  it("builds ritual href with question and domain", () => {
    const href = buildTarotRitualHref({
      spreadId: "three_cards",
      question: "Стоит ли менять работу?",
      concernDomain: "work",
      refinementId: "stay_or_leave",
    });
    expect(href).toContain("/tarot/spread/three_cards");
    expect(href).toContain("question=");
    expect(href).toContain("domain=work");
  });
});
