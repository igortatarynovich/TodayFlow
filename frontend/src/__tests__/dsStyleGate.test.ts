/**
 * DS Task 1 — style gate runs inside Frontend Tests job (npm test).
 * GitHub OAuth token lacks `workflow` scope, so we do not edit .github/workflows/*.yml here.
 * New module.css hex / ad-hoc CTA-card classes / legacy token defs beyond baseline fail this test.
 */
import { execFileSync } from "child_process";
import path from "path";

const repoRoot = path.resolve(__dirname, "../../..");
const script = path.join(repoRoot, "scripts", "check_ds_style_gate.py");

describe("design-system style gate", () => {
  it("rejects new module.css ad-hoc / hex / legacy token debt beyond baseline", () => {
    expect(() =>
      execFileSync("python3", [script, "--quiet"], {
        cwd: repoRoot,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"],
      }),
    ).not.toThrow();
  });
});
