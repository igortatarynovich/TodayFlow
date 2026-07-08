import { findEncyclopediaSelection, mapEncyclopediaToHubCards } from "@/lib/compatibilityEncyclopediaApi";

describe("compatibilityEncyclopediaApi", () => {
  const sample = {
    content_locale: "ru",
    version: "v1",
    hero: { eyebrow: "E", title: "T", lead: "L" },
    categories: [
      {
        id: "love",
        emoji: "❤️",
        title: "Любовь",
        subtitle: "sub",
        analyze_params: { topic: "love" },
        intro_blocks: [{ kind: "paragraph" as const, text: "Intro love" }],
      },
    ],
    popular_readings: [{ id: "opposites", title: "Opposites", analyze_params: { reading: "opposites" } }],
    series: [{ id: "office", title: "Office", subtitle: "sub", analyze_params: { series: "office" } }],
    entry_routes: {},
  };

  it("maps catalog to hub card hrefs", () => {
    const cards = mapEncyclopediaToHubCards(sample);
    expect(cards.categories[0].href).toBe("/compatibility/analyze?topic=love");
    expect(cards.popularReadings[0].href).toContain("reading=opposites");
  });

  it("finds selection by topic", () => {
    const sel = findEncyclopediaSelection(sample, { topic: "love" });
    expect(sel?.label).toBe("Любовь");
    expect(sel?.introBlocks[0].text).toBe("Intro love");
  });
});
