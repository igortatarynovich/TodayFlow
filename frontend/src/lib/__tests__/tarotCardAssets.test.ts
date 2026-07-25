import {
  resolveDailyTarotDeckIndex,
  resolveTarotDeckIndexByName,
  tarotCardFaceSrc,
  TAROT_FULL_DECK_COUNT,
} from "@/lib/tarotCardAssets";

describe("tarotCardAssets full deck", () => {
  it("maps every deck index 0…77 to a face path", () => {
    for (let i = 0; i < TAROT_FULL_DECK_COUNT; i++) {
      const src = tarotCardFaceSrc(i);
      expect(src).toBeTruthy();
      expect(src).toContain("/images/cards/tarot/");
    }
  });

  it("resolves major and minor names in EN and RU", () => {
    expect(resolveTarotDeckIndexByName("The Fool")).toBe(0);
    expect(resolveTarotDeckIndexByName("Шут")).toBe(0);
    expect(resolveTarotDeckIndexByName("Ace of Cups")).toBe(36);
    expect(resolveTarotDeckIndexByName("Туз кубков")).toBe(36);
    expect(resolveTarotDeckIndexByName("King of Pentacles")).toBe(77);
    expect(resolveTarotDeckIndexByName("pentacles_king")).toBe(77);
  });

  it("resolveDailyTarotDeckIndex prefers numeric id then name then date hash", () => {
    expect(
      resolveDailyTarotDeckIndex({
        morningTarotCardId: 42,
        morningTarotName: null,
        cardName: "The Fool",
        dateISO: "2026-07-25",
      }),
    ).toBe(42);
    expect(
      resolveDailyTarotDeckIndex({
        morningTarotCardId: null,
        morningTarotName: "Двойка кубков",
        cardName: "The Fool",
        dateISO: "2026-07-25",
      }),
    ).toBe(37);
    const hashed = resolveDailyTarotDeckIndex({
      morningTarotCardId: null,
      morningTarotName: null,
      cardName: "unknown-card-xyz",
      dateISO: "2026-07-25",
    });
    expect(hashed).toBeGreaterThanOrEqual(0);
    expect(hashed).toBeLessThan(78);
  });
});
