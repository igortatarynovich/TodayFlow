/** Wrapped / share seed — story line for copy, not stats (Product Model §4.10). */

export async function copyMapShareLine(text: string): Promise<boolean> {
  if (typeof navigator === "undefined" || !navigator.clipboard?.writeText) return false;
  try {
    await navigator.clipboard.writeText(text.trim());
    return true;
  } catch {
    return false;
  }
}
