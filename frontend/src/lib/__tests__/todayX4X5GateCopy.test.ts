/**
 * X4/X5 — joint honest reveal copy on locked T2-gate chrome.
 * PASS only when both clauses hold. Overlay gesture and YYYYMMDD formula stay out.
 * Canon: TODAY_PRODUCT_FLOW_V1 X4/X5 · TODAY_DISPLAY_INVENTORY_V1 T2-gate.*
 */

import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";

function normalize(s: string): string {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

describe("X4/X5 T2 gate copy bank", () => {
  const cardChrome = normalize(
    [copy.ritualTarotPendingTitle, copy.ritualTarotPendingBody, copy.ritualTarotPickCta, copy.ritualTarotOpenCta].join(
      "\n",
    ),
  );
  const numberChrome = normalize(
    [
      copy.ritualNumberPendingTitle,
      copy.ritualNumberPendingBody,
      copy.ritualNumberPickCta,
      copy.ritualNumberOpenCta,
    ].join("\n"),
  );

  it("X4: card chrome does not claim a real pick of a prebaked card", () => {
    expect(cardChrome).not.toMatch(/выбери ту/);
    expect(cardChrome).not.toMatch(/к которой тянет/);
    expect(cardChrome).not.toMatch(/выбрать карту/);
    expect(cardChrome).toMatch(/открой|вытяни|сними|открыть/);
  });

  it("X5: number chrome does not claim a personal calendar number", () => {
    expect(numberChrome).not.toMatch(/сво[её] число/);
    expect(numberChrome).not.toMatch(/тво[её] число/);
    expect(numberChrome).not.toMatch(/выбрать число/);
    expect(numberChrome).toMatch(/число (сегодняшнего )?дня|открыть число/);
  });
});
