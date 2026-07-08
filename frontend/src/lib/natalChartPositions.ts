/**
 * Доступ к телам в `positions` ответа натала: ключи могут быть Sun/sun и т.д.
 */
export function lookupNatalBodyPosition<T>(
  positions: Record<string, T> | null | undefined,
  body: string,
): T | undefined {
  if (!positions) return undefined;
  if (positions[body]) return positions[body];
  const want = body.toLowerCase();
  const key = Object.keys(positions).find((k) => k.toLowerCase() === want);
  return key ? positions[key] : undefined;
}
