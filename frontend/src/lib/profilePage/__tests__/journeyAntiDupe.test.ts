import { applyAct2AntiDupeMeaning, textOverlapRatio } from "@/lib/profilePage/journeyAntiDupe";

describe("journeyAntiDupe", () => {
  it("detects high overlap between recognition and paraphrased meaning", () => {
    const line = "Ты первым видишь структуру там, где остальные видят хаос.";
    const paraphrase = "Ты видишь структуру раньше остальных, пока они видят только хаос.";
    expect(textOverlapRatio(line, paraphrase)).toBeGreaterThan(0.35);
  });

  it("replaces overlapping Act-2 meaning with fact fallback", () => {
    const out = applyAct2AntiDupeMeaning({
      meaning: "Ты первым видишь структуру там, где остальные пока видят только хаос.",
      anchorId: "sun",
      recognitionLine: "Ты первым видишь структуру там, где остальные пока видят только хаос.",
    });
    expect(out).toMatch(/Солнце окрашивает|проявляешь силу/i);
    expect(out).not.toMatch(/видишь структуру/i);
    expect(out).not.toMatch(/механизм|берётся только/i);
  });

  it("keeps distinct person prose", () => {
    const out = applyAct2AntiDupeMeaning({
      meaning: "Ты проявляешь силу через систему и точность.",
      anchorId: "sun",
      recognitionLine: "Ты первым видишь структуру там, где остальные видят хаос.",
    });
    expect(out).toMatch(/систему и точность/i);
  });
});