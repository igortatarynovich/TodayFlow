import { readFileSync } from "node:fs";
import { join } from "node:path";

describe("TarotHubMain — no card-of-day surface", () => {
  it("does not fetch or render card-of-day / day-number product", () => {
    const src = readFileSync(join(process.cwd(), "src/components/shell/TarotHubMain.tsx"), "utf8");
    expect(src.includes("/tarot/daily")).toBe(false);
    expect(src.includes("getJson")).toBe(false);
    expect(src.includes("tarotCardFaceSrc")).toBe(false);
    expect(src.includes("tarot-hub-card-of-day-locked")).toBe(false);
    expect(src.includes("Ещё не выбрана")).toBe(false);
    expect(src.includes("число дня")).toBe(false);
    expect(src.includes("Карта дня — в")).toBe(false);
  });
});
