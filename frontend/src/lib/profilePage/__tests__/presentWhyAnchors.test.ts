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
        id: "life_path",
        class: "selected_by",
        label: "Число пути 7 · Искатель",
        contribution: "Семёрка — пауза и глубина.",
      },
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
    expect(selected?.id).toBe("life_path");
    expect(selected?.title).toMatch(/число пути 7/i);
    expect(primary.filter((r) => r.role === "selected").every((r) => r.id === "life_path")).toBe(
      true,
    );

    const asc = [...primary, ...secondary].find((r) => r.id.includes("presence"));
    expect(asc?.title).toMatch(/Асцендент в Водолее/i);
    expect(asc?.title).not.toMatch(/ASC|Aquarius/i);
    expect(asc?.claimProse).toMatch(/контакт/i);
  });

  it("drops occupancy claims instead of treating them as Why anchors", () => {
    const { primary, secondary } = presentWhyAnchors([
      { id: "sun", class: "portrait_influenced_by", label: "Солнце в Деве" },
      {
        id: "ce_claim:planet_in_sign:mars:cancer",
        class: "portrait_influenced_by",
        label: "Марс в Раке",
      },
      {
        id: "ce_claim:planet_in_house:mars:4",
        class: "portrait_influenced_by",
        label: "Марс в 4 доме",
      },
    ]);
    const ids = [...primary, ...secondary].map((r) => r.id);
    expect(ids).toContain("sun");
    expect(ids.some((id) => id.includes("planet_in_sign") || id.includes("planet_in_house"))).toBe(
      false,
    );
  });
});
