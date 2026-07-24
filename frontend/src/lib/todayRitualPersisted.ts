/**
 * Локальное состояние ритуала Today (веб) — паритет с iOS `RitualDayExtras` + ключи открытия дня.
 * Единая точка парсинга, миграций и проверки «хребта» (`ritualSpineComplete`).
 */

export const RITUAL_STORAGE_PREFIX = "todayflow.ritual.v1";

export type RitualPersistedState = {
  opened: boolean;
  numberRevealed: boolean;
  mood: string | null;
  headTopic: string | null;
  essentials: Record<string, boolean>;
  honestStep: string | null;
  numberRhythm: string | null;
  tarotMainId: number | null;
  tarotClarifierId: number | null;
  tarotApplied: boolean;
  /** Карта зафиксирована и пользователь нажал «Продолжить» к числу. */
  tarotContinueAck: boolean;
  /** «Готово» в блоке настроения — гейт «Твой день» (iOS `checkInSubmitted`). */
  checkInSubmitted: boolean;
};

export function ritualPersistedStorageKey(dateISO: string): string {
  return `${RITUAL_STORAGE_PREFIX}.${dateISO}`;
}

/**
 * Нормализует объект из `JSON.parse` в стабильную форму и применяет миграции.
 */
export function normalizeRitualPersistedPayload(input: unknown): RitualPersistedState {
  const p = input && typeof input === "object" ? (input as Record<string, unknown>) : {};

  const opened = !!p.opened;
  const numberRevealed = !!p.numberRevealed;
  const mood = typeof p.mood === "string" ? p.mood : null;
  const headTopic = typeof p.headTopic === "string" ? p.headTopic : null;
  const essentials = p.essentials && typeof p.essentials === "object" && !Array.isArray(p.essentials) ? (p.essentials as Record<string, boolean>) : {};
  const honestStep = typeof p.honestStep === "string" ? p.honestStep : null;
  const numberRhythm = typeof p.numberRhythm === "string" ? p.numberRhythm : null;
  const tarotMainId =
    typeof p.tarotMainId === "number" && Number.isFinite(p.tarotMainId) ? p.tarotMainId : null;
  const tarotClarifierId =
    typeof p.tarotClarifierId === "number" && Number.isFinite(p.tarotClarifierId) ? p.tarotClarifierId : null;
  const tarotApplied = !!p.tarotApplied;

  let tarotContinueAck = !!p.tarotContinueAck;
  if (tarotMainId != null && numberRevealed) {
    tarotContinueAck = true;
  }

  const checkInSubmitted =
    typeof p.checkInSubmitted === "boolean" ? p.checkInSubmitted : Boolean(mood);

  return {
    opened,
    numberRevealed,
    mood,
    headTopic,
    essentials,
    honestStep,
    numberRhythm,
    tarotMainId,
    tarotClarifierId,
    tarotApplied,
    tarotContinueAck,
    checkInSubmitted,
  };
}

export function loadRitualPersisted(dateISO: string): RitualPersistedState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(ritualPersistedStorageKey(dateISO));
    if (!raw) return null;
    return normalizeRitualPersistedPayload(JSON.parse(raw));
  } catch {
    return null;
  }
}

export function saveRitualPersisted(dateISO: string, state: RitualPersistedState): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(ritualPersistedStorageKey(dateISO), JSON.stringify(state));
  } catch {
    /* quota */
  }
}

/** Первый визит без снимка: на широком экране сразу показываем блок карты/числа (см. `TODAY_SCREEN_V1_CANON.md`). */
export function shouldAutoOpenRitualOnDesktopFirstVisit(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.matchMedia("(min-width: 1024px)").matches;
  } catch {
    return false;
  }
}

export type RitualSpineSlice = Pick<
  RitualPersistedState,
  "tarotMainId" | "tarotContinueAck" | "numberRevealed" | "mood" | "checkInSubmitted"
>;

/** Карта (с ack) → число → подтверждение чек-ина — mood chips removed (R18). */
export function isRitualSpineComplete(s: RitualSpineSlice): boolean {
  return Boolean(
    s.tarotMainId != null && s.tarotContinueAck && s.numberRevealed && s.checkInSubmitted,
  );
}
