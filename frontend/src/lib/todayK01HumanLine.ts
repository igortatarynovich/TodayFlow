/**
 * TIC-K01 presentation: formulate the already-chosen shared-day energy.
 * Not a second selector. Not greeting. Not a knowledge root.
 * Canon: TODAY_INFORMATION_CONTRACT_V1 K01 · TODAY_DISPLAY_INVENTORY_V1 T1-hero.human_line
 */

import type { DayVisualMode } from "@/lib/dayAtmosphere";
import { DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";

/** Closed 8-set sentences. Key = Engine `primary_energy`. Do not widen. */
export const SHARED_DAY_HUMAN_LINES: Record<DayVisualMode, string> = {
  grounded:
    "Общий день держится на заземлении: темп ровный, и опора в том, что просто и устойчиво.",
  flow: "Общий день идёт потоком: легче следовать самому движению, чем продавливать жёсткую форму.",
  radiance: "Общий день в сиянии: внимание тянется к видимому, тёплому и открытому тону.",
  momentum: "Общий день несёт импульс: энергия просит хода вперёд, а не долгой паузы.",
  clarity: "Общий день про ясность: меньше шума вокруг, и больше одного чёткого контура.",
  tension: "Общий день стоит в напряжении: поле сжато, и различия ощущаются резче обычного.",
  renewal: "Общий день про обновление: старое ослабевает, и появляется новое место для начала.",
  depth: "Общий день уходит в глубину: смысл ближе, чем видимая поверхность самих событий.",
};

function isClosedEnergy(value: string): value is DayVisualMode {
  return (DAY_VISUAL_MODES as readonly string[]).includes(value);
}

/** Map Engine primary_energy → T1-hero.human_line. Unknown / missing → omit. */
export function formulateSharedDayHumanLine(energy: unknown): string | null {
  if (typeof energy !== "string") return null;
  const key = energy.trim().toLowerCase();
  if (!isClosedEnergy(key)) return null;
  return SHARED_DAY_HUMAN_LINES[key];
}
