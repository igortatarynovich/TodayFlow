/**
 * X3 — T2 gate copy must not claim Theme / Focus / Step / action timing.
 * Theatrical pick (X4) and «своё число» (X5) are out of this gate.
 * Canon: TODAY_PRODUCT_FLOW_V1 X3 · TODAY_DISPLAY_INVENTORY_V1 T2-gate.*
 */

import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";

function normalize(s: string): string {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

describe("X3 T2 gate copy", () => {
  const tarot = normalize(copy.ritualTarotPendingBody);
  const number = normalize(copy.ritualNumberPendingBody);
  const liveGates = `${tarot}\n${number}`;

  it("does not let the card define today", () => {
    expect(tarot).not.toMatch(/говорит о сегодня/);
    expect(tarot).not.toMatch(/какой сегодня день/);
    expect(tarot).not.toMatch(/начинает день/);
    expect(tarot).toMatch(/зеркал|слой|взгляд/);
  });

  it("does not let the number set when to act", () => {
    expect(number).not.toMatch(/задаёт ритм/);
    expect(number).not.toMatch(/когда лучше действовать/);
    expect(number).not.toMatch(/когда.{0,40}не торопиться/);
    expect(number).toMatch(/слой|линз|символ/);
  });

  it("does not present ritual as a new recommendation authority", () => {
    expect(liveGates).not.toMatch(/собер[её]т рекомендац/);
    expect(liveGates).not.toMatch(/соберёт день/);
  });
});
