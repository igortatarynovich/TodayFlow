/** Split profile insight copy into short bullet lines for Quick Map UI. */
export function profileCopyToBullets(text: string | null | undefined, max = 4): string[] {
  const raw = text?.trim();
  if (!raw) return [];

  if (raw.includes("•")) {
    return raw
      .split("•")
      .map((part) => part.trim())
      .filter(Boolean)
      .slice(0, max);
  }

  if (raw.includes("\n")) {
    return raw
      .split("\n")
      .map((part) => part.trim())
      .filter(Boolean)
      .slice(0, max);
  }

  if (raw.includes(";")) {
    return raw
      .split(";")
      .map((part) => part.trim())
      .filter(Boolean)
      .slice(0, max);
  }

  return [raw];
}

/** Compact tags for «where you thrive» — first clause or short phrase. */
export function profileCopyToTags(texts: Array<string | null | undefined>, max = 5): string[] {
  const tags: string[] = [];

  for (const text of texts) {
    for (const bullet of profileCopyToBullets(text, 2)) {
      const candidate = bullet.split(/[,—–-]/)[0]?.trim() ?? bullet.trim();
      if (!candidate || candidate.length > 48) continue;
      if (!tags.includes(candidate)) tags.push(candidate);
      if (tags.length >= max) return tags;
    }
  }

  return tags;
}
