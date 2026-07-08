/** Cross-layer dedup: one phrase must not appear in two profile blocks. */

export function textsOverlap(a: string, b: string): boolean {
  const left = a.trim().toLowerCase();
  const right = b.trim().toLowerCase();
  if (!left || !right) return false;

  const probe = Math.min(40, left.length, right.length);
  if (probe < 16) return false;

  const slice = left.slice(0, probe);
  if (right.includes(slice) || left.includes(right.slice(0, probe))) return true;

  const wordsA = new Set(left.split(/\s+/).filter((w) => w.length > 4));
  const wordsB = right.split(/\s+/).filter((w) => w.length > 4);
  if (!wordsA.size || !wordsB.length) return false;

  let shared = 0;
  for (const w of wordsB) {
    if (wordsA.has(w)) shared += 1;
  }
  return shared >= 3;
}

export class ProfileContentLedger {
  private readonly used: string[] = [];

  hasOverlap(text: string | null | undefined): boolean {
    const t = text?.trim();
    if (!t) return false;
    return this.used.some((u) => textsOverlap(u, t));
  }

  claim(text: string | null | undefined): string | null {
    const t = text?.trim();
    if (!t) return null;
    if (this.hasOverlap(t)) return null;
    this.used.push(t);
    return t;
  }

  claimFirst(candidates: Array<string | null | undefined>, minLen = 24): string | null {
    for (const c of candidates) {
      const t = c?.trim();
      if (!t || t.length < minLen) continue;
      const claimed = this.claim(t);
      if (claimed) return claimed;
    }
    return null;
  }

  claimMany(candidates: Array<string | null | undefined>, max: number, minLen = 24): string[] {
    const out: string[] = [];
    for (const c of candidates) {
      if (out.length >= max) break;
      const t = c?.trim();
      if (!t || t.length < minLen) continue;
      const claimed = this.claim(t);
      if (claimed) out.push(claimed);
    }
    return out;
  }

  /** Register hero digest without blocking later layers from shorter non-overlapping picks. */
  seed(text: string | null | undefined): void {
    const t = text?.trim();
    if (t) this.used.push(t);
  }
}
