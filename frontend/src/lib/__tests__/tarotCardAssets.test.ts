import fs from "node:fs";
import path from "node:path";
import {
  resolveDailyTarotDeckIndex,
  resolveTarotDeckIndexByName,
  tarotCardFaceSrc,
  TAROT_FULL_DECK_COUNT,
} from "@/lib/tarotCardAssets";
import tarotIndex from "@/data/tarotDeckIndex.json";

const TAROT_PUBLIC = path.join(process.cwd(), "public/images/cards/tarot");

function facePathOnDisk(deckIndex: number): string {
  if (deckIndex <= 21) {
    return path.join(TAROT_PUBLIC, "Major Arcana", `${deckIndex}.png`);
  }
  const n = deckIndex - 22;
  const suits = ["Suit of Wands", "Suit of Cups", "Suit of Swords", "Suit of Pentacles"];
  const suit = suits[Math.floor(n / 14)]!;
  const rank = (n % 14) + 1;
  return path.join(TAROT_PUBLIC, suit, `${rank}.png`);
}

describe("tarotCardAssets full deck", () => {
  it("registry has exactly 78 unique deck indices 0…77", () => {
    const ids = tarotIndex.cards.map((c) => c.deck_index).sort((a, b) => a - b);
    expect(ids).toHaveLength(78);
    expect(new Set(ids).size).toBe(78);
    expect(ids[0]).toBe(0);
    expect(ids[77]).toBe(77);
    expect(ids.filter((i) => i <= 21)).toHaveLength(22);
    expect(ids.filter((i) => i >= 22)).toHaveLength(56);
  });

  it("all 78 face PNG assets exist on disk", () => {
    for (let i = 0; i < TAROT_FULL_DECK_COUNT; i++) {
      const file = facePathOnDisk(i);
      expect(fs.existsSync(file)).toBe(true);
      expect(tarotCardFaceSrc(i)).toBeTruthy();
    }
  });

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
