import {
  filterProfileCopyList,
  isMachineProfileToken,
  isMostlyLatinProse,
  isUsableProfileCopy,
  profileContractMatchesLocale,
} from "../profileCopySafety";

describe("profileCopySafety", () => {
  it("rejects machine tokens and embedded ritual_mood ids", () => {
    expect(isMachineProfileToken("ritual_mood:driven")).toBe(true);
    expect(isMachineProfileToken("Продолжи то, что уже работает: ritual_mood:driven.")).toBe(true);
    expect(isMachineProfileToken("evening_reflection")).toBe(true);
    expect(isMachineProfileToken("Короткие сессии фокуса")).toBe(false);
  });

  it("detects English prose for RU filtering", () => {
    expect(
      isMostlyLatinProse(
        "You are someone who navigates life by watching closely and adapting in real time.",
      ),
    ).toBe(true);
    expect(isMostlyLatinProse("Ты ориентируешься на мягкий ритм и маленькие конкретные шаги.")).toBe(false);
  });

  it("filters EN contract for RU locale", () => {
    expect(
      profileContractMatchesLocale(
        {
          identity_core:
            "You are someone who navigates life by watching closely and adapting in real time, finding your footing.",
        },
        "ru",
      ),
    ).toBe(false);
    expect(
      isUsableProfileCopy("Keen observation and real-time adaptation", "ru"),
    ).toBe(false);
    expect(filterProfileCopyList(["ritual_mood:driven", "Один спокойный шаг"], 4, "ru")).toEqual([
      "Один спокойный шаг",
    ]);
  });
});
