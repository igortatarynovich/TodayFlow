import { readFileSync } from "node:fs";

/** Slot ids from Inventory §2 index tables. Wildcards kept as written. */
export function extractInventoryIndexSlotIds(markdown: string): string[] {
  const ids: string[] = [];
  const seen = new Set<string>();
  let inIndex = false;
  for (const line of markdown.split("\n")) {
    if (line.startsWith("## 2. Индекс слотов")) {
      inIndex = true;
      continue;
    }
    if (inIndex && line.startsWith("## ")) break;
    const match = line.match(/^\| `([^`]+)` \|/);
    if (inIndex && match) {
      const id = match[1];
      if (!seen.has(id)) {
        seen.add(id);
        ids.push(id);
      }
    }
  }
  return ids;
}

export function readInventoryIndexSlotIds(absPath: string): string[] {
  return extractInventoryIndexSlotIds(readFileSync(absPath, "utf8"));
}
