import { readFileSync, readdirSync } from "fs";
import { join } from "path";

/**
 * Guards the phase-6 globals split: module bodies concatenated in import order
 * must equal the frozen pre-split CSS body (no cascade drift).
 *
 * Visual regression (manual): /, /today, /profile, /tarot — see styles/globals/README.md
 */
describe("globals.css split cascade", () => {
  const stylesDir = join(__dirname, "..");
  const fixturePath = join(stylesDir, "pre-split-body.fixture.css");
  const orchestratorPath = join(__dirname, "../../../app/globals.css");

  const moduleOrder = [
    "01-tokens-base.css",
    "02-nav-footer.css",
    "03-orbit-components.css",
    "04-marketing-home.css",
    "05-product-pages.css",
    "06-serene-surfaces.css",
  ];

  it("orchestrator imports modules in locked order after foundation imports", () => {
    const orch = readFileSync(orchestratorPath, "utf8");
    const importLines = orch
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.startsWith("@import") && l.includes("styles/globals/"));
    expect(importLines).toHaveLength(moduleOrder.length);
    moduleOrder.forEach((name, i) => {
      expect(importLines[i]).toContain(name);
    });
  });

  it("concatenated module bodies match pre-split fixture", () => {
    const stripHeader = (text: string) => {
      if (!text.startsWith("/**")) return text;
      const end = text.indexOf("*/");
      if (end < 0) return text;
      return text.slice(end + 2).replace(/^\s*\n/, "");
    };

    const concat = moduleOrder
      .map((name) => stripHeader(readFileSync(join(stylesDir, name), "utf8")))
      .join("");
    const fixture = readFileSync(fixturePath, "utf8");
    expect(concat).toBe(fixture);
  });

  it("globals folder only contains the six ordered modules as .css (plus fixture)", () => {
    const files = readdirSync(stylesDir).filter((f) => f.endsWith(".css"));
    expect(files.sort()).toEqual([...moduleOrder, "pre-split-body.fixture.css"].sort());
  });
});
