import { createTarotQuestionSession } from "@/lib/tarotQuestionSession";
import { applyTarotEntryPrefill } from "@/lib/tarotEntryPrefill";
import { buildTarotDeepenHref, pickTarotDeepenOffers } from "@/lib/tarotDeepenOffers";

describe("tarotDeepenOffers", () => {
  it("puts intimacy first after a relationships reading", () => {
    const offers = pickTarotDeepenOffers("relationships");
    expect(offers[0]?.id).toBe("intimacy_practical");
    expect(offers.some((o) => o.id === "money_practical")).toBe(true);
    expect(offers).toHaveLength(4);
  });

  it("puts money first after work", () => {
    expect(pickTarotDeepenOffers("work")[0]?.id).toBe("money_practical");
  });

  it("builds deepen href with source and question", () => {
    const offer = pickTarotDeepenOffers("money")[0]!;
    const href = buildTarotDeepenHref(offer);
    expect(href).toContain("/tarot?");
    expect(href).toContain("source=deepen");
    expect(href).toContain("concern=");
    expect(href).toContain("question=");
  });
});

describe("applyTarotEntryPrefill deepen", () => {
  it("jumps to spread with ready question", () => {
    const session = createTarotQuestionSession();
    const params = new URLSearchParams({
      concern: "money",
      refine: "practical_week",
      question: "Какой один практический шаг по деньгам стоит сделать на этой неделе?",
      source: "deepen",
    });
    const next = applyTarotEntryPrefill(session, params);
    expect(next.step).toBe("spread");
    expect(next.concernDomain).toBe("money");
    expect(next.refinementId).toBe("practical_week");
    expect(next.customQuestion).toContain("практический шаг");
  });

  it("keeps topic= refine path for legacy links", () => {
    const session = createTarotQuestionSession();
    const next = applyTarotEntryPrefill(session, new URLSearchParams({ topic: "work" }));
    expect(next.concernDomain).toBe("work");
    expect(next.step).toBe("refine");
  });
});
