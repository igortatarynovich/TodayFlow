/**
 * DS Task 1+2.6+2.7 — style gate runs inside Frontend Tests job (npm test).
 * New module.css hex / rgba / color-mix / font-size / max-width / ad-hoc CTA-card /
 * legacy token defs beyond baseline fail this test.
 */
import { execFileSync } from "child_process";
import path from "path";

const repoRoot = path.resolve(__dirname, "../../..");
const script = path.join(repoRoot, "scripts", "check_ds_style_gate.py");

describe("design-system style gate", () => {
  it("rejects new module.css DS debt beyond baseline (hex/rgba/type/width/adhoc)", () => {
    expect(() =>
      execFileSync("python3", [script, "--quiet"], {
        cwd: repoRoot,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"],
      }),
    ).not.toThrow();
  });
});
