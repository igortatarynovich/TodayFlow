import { applyAct2AntiDupeMeaning, textOverlapRatio } from "@/lib/profilePage/journeyAntiDupe";

describe("journeyAntiDupe", () => {
  it("detects high overlap between recognition and paraphrased meaning", () => {
    const line = "Ты первым видишь структуру там, где остальные видят хаос.";
    const paraphrase = "Ты видишь структуру раньше остальных, пока они видят только хаос.";
    expect(textOverlapRatio(line, paraphrase)).toBeGreaterThan(0.35);
  });

  it("replaces overlapping Act-2 meaning with mechanism fallback", () => {
    const out = applyAct2AntiDupeMeaning({
      meaning: "Ты первым видишь структуру там, где остальные пока видят только хаос.",
      anchorId: "sun",
      recognitionLine: "Ты первым видишь структуру там, где остальные пока видят только хаос.",
    });
    expect(out).toMatch(/механизм|не повтор/i);
    expect(out).not.toMatch(/видишь структуру/i);
  });

  it("keeps distinct mechanism prose", () => {
    const out = applyAct2AntiDupeMeaning({
      meaning: "Расширяет портрет: как ты проявляешь силу через систему и точность.",
      anchorId: "sun",
      recognitionLine: "Ты первым видишь структуру там, где остальные видят хаос.",
    });
    expect(out).toMatch(/систему и точность/i);
  });
});
