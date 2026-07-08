import {
  compatibilityHubSymbol,
  compatibilityPairSymbolFromDisplay,
  parsePairSignsFromDisplay,
} from "@/lib/compatibilityHeroSymbol";

describe("compatibilityHeroSymbol", () => {
  it("parses pair display labels", () => {
    expect(parsePairSignsFromDisplay("Овен × Телец")).toEqual({
      fromSign: "Овен",
      toSign: "Телец",
    });
  });

  it("builds hub and pair symbols", () => {
    expect(compatibilityHubSymbol()).toBeTruthy();
    expect(compatibilityPairSymbolFromDisplay("Овен × Телец")).toBeTruthy();
  });
});
