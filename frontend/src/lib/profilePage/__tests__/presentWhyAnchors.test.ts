import { presentWhyAnchors } from "@/lib/profilePage/presentWhyAnchors";

describe("presentWhyAnchors", () => {
  it("splits em-dash labels and keeps selected_by as primary pillar", () => {
    const { primary, secondary } = presentWhyAnchors([
      {
        id: "archetype_from_life_path",
        class: "selected_by",
        label: "Архетип Архитектора — рассчитан из числа пути 1",
      },
      { id: "sun", class: "portrait_influenced_by", label: "Солнце в Овне" },
      { id: "element", class: "portrait_influenced_by", label: "Стихия — огонь" },
      { id: "moon", class: "portrait_influenced_by", label: "Луна в Скорпионе" },
      { id: "asc", class: "portrait_influenced_by", label: "ASC в Льве" },
      { id: "rhythm", class: "portrait_influenced_by", label: "Ритм — быстрый старт" },
    ]);

    expect(primary.map((r) => r.id)).toEqual([
      "archetype_from_life_path",
      "sun",
      "moon",
      "asc",
    ]);
    expect(primary[0]?.title).toBe("Архетип Архитектора");
    expect(primary[0]?.detail).toBe("рассчитан из числа пути 1");
    expect(primary[0]?.role).toBe("selected");
    expect(secondary.map((r) => r.id)).toEqual(["element", "rhythm"]);
    expect(secondary[0]?.title).toBe("Стихия");
    expect(secondary[0]?.detail).toBe("огонь");
  });

  it("does not invent prose when label has no dash", () => {
    const { primary } = presentWhyAnchors([
      { id: "sun", class: "portrait_influenced_by", label: "Солнце в Деве" },
    ]);
    expect(primary[0]?.title).toBe("Солнце в Деве");
    expect(primary[0]?.detail).toBeNull();
  });
});
