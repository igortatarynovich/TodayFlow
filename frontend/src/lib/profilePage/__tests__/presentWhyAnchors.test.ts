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
      { id: "asc", class: "portrait_influenced_by", label: "Асцендент в Льве" },
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

  it("localizes EN signs and ASC; puts fact first on influenced CE claims", () => {
    const { primary, secondary } = presentWhyAnchors([
      {
        id: "ce_claim:direction_through_air_mind",
        class: "selected_by",
        label: "Путь через идеи и связи — Солнце в Gemini",
      },
      {
        id: "ce_claim:presence_through_air_asc",
        class: "portrait_influenced_by",
        label: "Первый контакт через вопросы — ASC в Aquarius",
      },
    ]);
    const selected = primary.find((r) => r.role === "selected");
    expect(selected?.title).toMatch(/идеи и связи/i);
    expect(selected?.detail).toBeNull();
    expect(selected?.title).not.toMatch(/Gemini|Солнце/i);

    const asc = [...primary, ...secondary].find((r) => r.id.includes("presence"));
    expect(asc?.title).toMatch(/Асцендент в Водолее/i);
    expect(asc?.title).not.toMatch(/ASC|Aquarius/i);
    expect(asc?.claimProse).toMatch(/контакт/i);
  });
});
