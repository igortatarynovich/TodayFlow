/**
 * Value gate unit tests — hide kitchen / system / textbook copy.
 */

import { findValueGateHits, scrubUserFacingText } from "@/lib/todayValueGate";

describe("todayValueGate", () => {
  it("hides living pipeline fluff and raw keys", () => {
    const text =
      "Слой быстрых решений пока собран слабо. Чаще всего сейчас всплывает тема `focus`.";
    expect(findValueGateHits(text).length).toBeGreaterThan(0);
    expect(scrubUserFacingText(text)).toBeNull();
  });

  it("hides truncated style×tarot mashup", () => {
    const text =
      "Осторожнее с темой «общий фон дня»… При твоём стиле («вы решаете…») «Двойка пентаклей»…";
    expect(scrubUserFacingText(text)).toBeNull();
  });

  it("allows concrete behavioral trap", () => {
    const text =
      "После резкого сообщения захочется сразу отправить ещё одно, чтобы окончательно объяснить свою позицию.";
    expect(scrubUserFacingText(text)).toBe(text);
  });

  it("hides textbook house meaning unless allowed", () => {
    const text = "Первый дом отвечает за первое впечатление.";
    expect(scrubUserFacingText(text)).toBeNull();
    expect(scrubUserFacingText(text, { allowTextbook: true })).toBe(text);
  });
});
