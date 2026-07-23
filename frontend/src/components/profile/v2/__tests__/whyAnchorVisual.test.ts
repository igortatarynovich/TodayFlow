import { resolveWhyAnchorVisual } from "@/components/profile/v2/whyAnchorVisual";

describe("resolveWhyAnchorVisual", () => {
  it("maps live fact labels to registry symbols without inventing prose", () => {
    expect(resolveWhyAnchorVisual("Солнце в Деве")).toEqual({ kind: "planet", slug: "sun" });
    expect(resolveWhyAnchorVisual("Луна в Рыбах")).toEqual({ kind: "planet", slug: "moon" });
    expect(resolveWhyAnchorVisual("Земля")).toEqual({ kind: "element", slug: "earth" });
    expect(resolveWhyAnchorVisual("Дева")).toEqual({ kind: "zodiac", slug: "virgo" });
    expect(resolveWhyAnchorVisual("Число пути 7 → Исследователь", "selected_by")).toEqual({
      kind: "lifePath",
      digit: "7",
    });
    expect(resolveWhyAnchorVisual("Путь 7")).toEqual({ kind: "lifePath", digit: "7" });
  });
});
