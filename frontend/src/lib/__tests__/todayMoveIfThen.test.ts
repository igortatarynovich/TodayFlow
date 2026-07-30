import { pickMoveIfThenFromScenes } from "@/lib/todayMoveIfThen";

describe("todayMoveIfThen D.4", () => {
  it("prefers primary scene with both do and avoid", () => {
    expect(
      pickMoveIfThenFromScenes([
        {
          role_in_story: "support",
          recommended_action: "Support do",
          do_not: "Support avoid",
        },
        {
          role_in_story: "primary",
          recommended_action: "Сделай один короткий шаг.",
          do_not: "Не дожимай до ночи.",
        },
      ]),
    ).toEqual({
      do: "Сделай один короткий шаг.",
      avoid: "Не дожимай до ночи.",
    });
  });

  it("returns null when scenes lack action copy", () => {
    expect(pickMoveIfThenFromScenes([])).toBeNull();
    expect(pickMoveIfThenFromScenes([{ role_in_story: "primary" }])).toBeNull();
  });

  it("allows single-sided honesty", () => {
    expect(
      pickMoveIfThenFromScenes([
        { role_in_story: "primary", recommended_action: "Только сделай.", do_not: "" },
      ]),
    ).toEqual({ do: "Только сделай.", avoid: "" });
  });
});
