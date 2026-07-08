/** Join class names — minimal helper for DS components. */
export function joinClass(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}
