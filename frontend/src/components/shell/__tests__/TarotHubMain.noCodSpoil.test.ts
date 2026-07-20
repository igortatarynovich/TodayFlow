import { readFileSync } from "node:fs";
import { join } from "node:path";

describe("TarotHubMain card-of-day spoil DoD", () => {
  it("does not fetch /tarot/daily or /tarot/daily/public", () => {
    const src = readFileSync(join(process.cwd(), "src/components/shell/TarotHubMain.tsx"), "utf8");
    expect(src.includes("/tarot/daily")).toBe(false);
    expect(src.includes("getJson")).toBe(false);
    expect(src.includes("tarotCardFaceSrc")).toBe(false);
    expect(src.includes("Ещё не выбрана")).toBe(true);
    expect(src.includes("tarot-hub-card-of-day-locked")).toBe(true);
  });
});
