/**
 * Согласование обращения на «ты» с профилем пользователя.
 * Когда пол неизвестен — в копирайте используем нейтральные конструкции (инфинитив, настоящее время, без прошедшего ж.р.).
 * Канонические значения с бэка: `female` | `male` | `unspecified` (`GET /account/core-profile` → `person.gender`).
 */
export type RuUserDeclension = "feminine" | "masculine" | "unspecified";

export function parseRuUserDeclension(raw?: string | null): RuUserDeclension {
  if (raw == null || String(raw).trim() === "") return "unspecified";
  const x = String(raw).trim().toLowerCase();
  if (
    ["f", "female", "feminine", "woman", "ж", "женский", "женщина"].includes(x) ||
    x.startsWith("жен")
  ) {
    return "feminine";
  }
  if (["m", "male", "masculine", "man", "м", "мужской", "мужчина"].includes(x) || x.startsWith("муж")) {
    return "masculine";
  }
  return "unspecified";
}

/** Заголовок блока «чего не дожимать» — единственное место, где уместно явное согласование, если пол известен. */
export function ritualAvoidHeadingForDeclension(d: RuUserDeclension): string {
  if (d === "feminine") return "Чего бы сегодня не дожимала";
  if (d === "masculine") return "Чего бы сегодня не дожимал";
  return "Чего сегодня лучше не дожимать";
}

export function ritualAvoidHeadingForUserGender(raw?: string | null): string {
  return ritualAvoidHeadingForDeclension(parseRuUserDeclension(raw));
}
