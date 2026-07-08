/**
 * Иллюстрация входа в ритуал «Твой день»: публичные файлы в
 * `/images/today-ritual-entry/` (см. ASSET_SPEC.txt в той папке).
 */

export type RitualEntryTimeSlot = "morning" | "day" | "evening";

export type RitualEntryEnergyBand = "soft" | "balanced" | "vivid";

const ENTRY_BASE = "/images/today-ritual-entry";

/** Локальные часы устройства: утро / день / вечер. */
export function ritualEntryTimeSlot(now: Date = new Date()): RitualEntryTimeSlot {
  const h = now.getHours();
  if (h >= 5 && h < 12) return "morning";
  if (h >= 12 && h < 17) return "day";
  return "evening";
}

/** Грубый «тон дня» по шкале энергии 0–100 (как в герое Today). */
export function ritualEntryEnergyBand(energyScore: number): RitualEntryEnergyBand {
  const s = Math.max(0, Math.min(100, Math.round(energyScore)));
  if (s < 40) return "soft";
  if (s < 70) return "balanced";
  return "vivid";
}

function basesFor(dateISO: string, slot: RitualEntryTimeSlot, band: RitualEntryEnergyBand): string[] {
  return [
    `${dateISO}-${slot}-${band}`,
    `${dateISO}-${slot}`,
    dateISO,
    `default-${slot}-${band}`,
    `default-${slot}`,
    "default",
  ];
}

const EXT_ORDER = [".webp", ".png", ".jpg", ".jpeg"] as const;

/** Полные пути для `<img src>` — по порядку до первого успешно загруженного. */
/** Строка над заголовком: дата · Утро|День|Вечер (локальные часы `now`). */
export function ritualEntryEyebrowLine(displayDate: string, now: Date): string {
  const slot = ritualEntryTimeSlot(now);
  const word = slot === "morning" ? "Утро" : slot === "day" ? "День" : "Вечер";
  return `${displayDate} · ${word}`;
}

export function ritualEntryImagePublicPaths(
  dateISO: string,
  energyScore: number,
  now: Date = new Date(),
): string[] {
  const slot = ritualEntryTimeSlot(now);
  const band = ritualEntryEnergyBand(energyScore);
  const out: string[] = [];
  for (const base of basesFor(dateISO, slot, band)) {
    for (const ext of EXT_ORDER) {
      out.push(`${ENTRY_BASE}/${base}${ext}`);
    }
  }
  return out;
}
