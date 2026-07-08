import fs from "node:fs";
import path from "node:path";

const SRC_ROOT = path.join(process.cwd(), "src");

/** User-facing hrefs to `/natal-chart` must redirect via profile; API paths are allowed. */
const FORBIDDEN_HREF = /href\s*=\s*["'`]\/natal-chart/;

function walk(dir: string, out: string[] = []): string[] {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "__tests__" || entry.name === "natal-chart") continue;
      walk(full, out);
    } else if (/\.(tsx?|jsx?)$/.test(entry.name)) {
      out.push(full);
    }
  }
  return out;
}

describe("profile legacy routes audit", () => {
  it("has no user-facing /natal-chart hrefs in frontend src", () => {
    const offenders = walk(SRC_ROOT).filter((file) => {
      const text = fs.readFileSync(file, "utf8");
      return FORBIDDEN_HREF.test(text);
    });
    expect(offenders).toEqual([]);
  });
});
