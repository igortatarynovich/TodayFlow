import fs from "node:fs";
import path from "node:path";
import {
  resolveDailyTarotDeckIndex,
  resolveTarotDeckIndexByName,
  tarotCardFaceSrc,
  tarotCardFacePicture,
  tarotCardBackPicture,
  TAROT_FULL_DECK_COUNT,
} from "@/lib/tarotCardAssets";
import tarotIndex from "@/data/tarotDeckIndex.json";
import tarotWebManifest from "@/data/tarotWebManifest.json";

const TAROT_WEB = path.join(process.cwd(), "public/images/cards/tarot/web");

describe("tarotCardAssets full deck (web pipeline)", () => {
  it("registry has exactly 78 unique deck indices 0…77", () => {
    const ids = tarotIndex.cards.map((c) => c.deck_index).sort((a, b) => a - b);
    expect(ids).toHaveLength(78);
    expect(new Set(ids).size).toBe(78);
    expect(ids[0]).toBe(0);
    expect(ids[77]).toBe(77);
  });

  it("web manifest lists 78 cards and back variants", () => {
    expect(tarotWebManifest.cards).toHaveLength(78);
    expect(tarotWebManifest.back.variants["576x960"]).toBeTruthy();
  });

  it("all 78 face web assets exist on disk (avif+webp mid size)", () => {
    for (let i = 0; i < TAROT_FULL_DECK_COUNT; i++) {
      const stem = String(i).padStart(2, "0");
      const avif = path.join(TAROT_WEB, "faces", `${stem}-576x960.avif`);
      const webp = path.join(TAROT_WEB, "faces", `${stem}-576x960.webp`);
      expect(fs.existsSync(avif)).toBe(true);
      expect(fs.existsSync(webp)).toBe(true);
      expect(tarotCardFaceSrc(i)).toBeTruthy();
      expect(tarotCardFacePicture(i)?.avifSrcSet).toContain(".avif");
    }
    expect(fs.existsSync(path.join(TAROT_WEB, "back-576x960.webp"))).toBe(true);
    expect(tarotCardBackPicture().src).toContain("/images/cards/tarot/web/");
  });

  it("maps every deck index 0…77 to a web face path", () => {
    for (let i = 0; i < TAROT_FULL_DECK_COUNT; i++) {
      const src = tarotCardFaceSrc(i);
      expect(src).toBeTruthy();
      expect(src).toContain("/images/cards/tarot/web/");
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
