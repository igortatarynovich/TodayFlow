import { buildWhyFormationCards } from "@/lib/profilePage/buildWhyFormationCards";

describe("buildWhyFormationCards", () => {
  it("adds life-path meaning on selected and forbids sun-as-cause framing", () => {
    const { selected, influenced } = buildWhyFormationCards(
      [
        {
          id: "archetype_from_life_path",
          class: "selected_by",
          label: "Архетип Исследователя — рассчитан из числа пути 7",
        },
        { id: "sun", class: "portrait_influenced_by", label: "Солнце в Деве" },
        { id: "element", class: "portrait_influenced_by", label: "Стихия — земля" },
        { id: "rhythm", class: "portrait_influenced_by", label: "Ритм — точный старт" },
      ],
      {
        core: {
          numerology: { life_path: 7 },
          astro: { sun_sign: "virgo", sun_element: "earth" },
          baseline: { rhythm_style: "Точный старт без спешки" },
        } as never,
        frameworkCards: [
          {
            id: "sun",
            title: "Солнце",
            anchor: "в Деве",
            body: "Ты проявляешь себя через систему и точность.",
          },
        ],
      },
    );

    expect(selected).toHaveLength(1);
    expect(selected[0]?.meaning).toMatch(/глубин|смысл|понят/i);
    expect(selected[0]?.meaning).toMatch(/только из числа пути/i);
    expect(selected[0]?.meaning).not.toMatch(/Солнца.*выбира/i);

    expect(influenced.map((r) => r.id)).toEqual(["sun", "element", "rhythm"]);
    expect(influenced.find((r) => r.id === "sun")?.meaning).toMatch(/систему и точность/i);
    expect(influenced.find((r) => r.id === "element")?.meaning).toMatch(/практик|тело|результат/i);
    expect(influenced.find((r) => r.id === "rhythm")?.meaning).toMatch(/Точный старт|точный старт/i);
    expect(influenced.every((r) => r.meaning.length > 20)).toBe(true);
  });
});
