/**
 * FE display helpers — defensive only; meaning gate is backend.
 */

import { nearDuplicateClaim, scrubUserFacingText } from "@/lib/todayValueGate";

describe("todayValueGate (defensive)", () => {
  it("hides empty / whitespace", () => {
    expect(scrubUserFacingText("")).toBeNull();
    expect(scrubUserFacingText("   ")).toBeNull();
    expect(scrubUserFacingText(null)).toBeNull();
  });

  it("passes through non-empty text without meaning filtering", () => {
    const leak =
      "Слой быстрых решений пока собран слабо. Чаще всего сейчас всплывает тема `focus`.";
    // Backend owns meaning scrub; FE must not invent a second gate.
    expect(scrubUserFacingText(leak)).toBe(leak);
  });

  it("detects near-duplicate claims for composition dedupe", () => {
    expect(nearDuplicateClaim("Прямота без фильтра.", "Прямота без фильтра")).toBe(true);
    expect(
      nearDuplicateClaim(
        "Короткий разговор внезапно станет серьёзным.",
        "Отправь одно письмо из черновиков.",
      ),
    ).toBe(false);
  });
});
