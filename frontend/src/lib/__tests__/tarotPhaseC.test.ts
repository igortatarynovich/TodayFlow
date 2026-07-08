import {
  buildTarotDeepenHref,
  parseTarotAnchorParam,
} from "@/lib/buildTarotDeepenHref";
import {
  buildTarotDeepenEventPayload,
  tarotDeepenIdempotencyKey,
} from "@/lib/tarotDeepenEvents";
import { buildTarotJourneySummary } from "@/lib/buildTarotJourneySummary";
import type { TarotJourneyEntry } from "@/lib/tarotJourneyStore";

describe("buildTarotDeepenHref", () => {
  it("builds three-card spread URL with anchor and question", () => {
    const href = buildTarotDeepenHref({
      cardId: 8,
      orientation: "reversed",
      source: "today",
    });
    expect(href).toContain("/tarot/spread/three_cards?");
    expect(href).toContain("anchor=8%3Areversed");
    expect(href).toContain("source=today");
  });

  it("parses anchor param", () => {
    expect(parseTarotAnchorParam("12:upright")).toEqual({ cardId: 12, orientation: "upright" });
    expect(parseTarotAnchorParam("5:reversed")).toEqual({ cardId: 5, orientation: "reversed" });
    expect(parseTarotAnchorParam(null)).toBeNull();
  });
});

describe("tarotDeepenEvents", () => {
  it("builds stable idempotency key per day", () => {
    const key = tarotDeepenIdempotencyKey({
      cardId: 3,
      source: "card_of_day",
      localDate: "2026-07-02",
    });
    expect(key).toBe("tarot-deepen:card_of_day:3:2026-07-02");
  });

  it("builds deepen event payload", () => {
    expect(
      buildTarotDeepenEventPayload({
        cardId: 1,
        orientation: "upright",
        source: "today",
      }),
    ).toEqual({
      card_id: 1,
      orientation: "upright",
      source: "today",
      spread_id: "three_cards",
    });
  });
});

describe("buildTarotJourneySummary", () => {
  const sample: TarotJourneyEntry[] = [
    {
      id: "a",
      completedAt: new Date().toISOString(),
      question: "Стоит ли менять работу?",
      concernDomain: "work",
      spreadId: "three_cards",
      spreadTitle: "Три карты",
      cardIds: [8, 12],
      cardNames: ["Strength", "Hanged Man"],
    },
    {
      id: "b",
      completedAt: new Date().toISOString(),
      question: "Как говорить с партнёром?",
      concernDomain: "relationships",
      spreadId: "one_card",
      spreadTitle: "Одна карта",
      cardIds: [6],
      cardNames: ["Lovers"],
    },
  ];

  it("aggregates themes and questions", () => {
    const summary = buildTarotJourneySummary(sample);
    expect(summary.totalSessions).toBe(2);
    expect(summary.themes.length).toBeGreaterThan(0);
    expect(summary.recentQuestions.length).toBe(2);
  });
});
