#!/usr/bin/env node
/**
 * Run real FE QuickMap / V2 projection against a capture pack JSON.
 * Prints one JSON line to stdout for the Python harness.
 */
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(__dirname, "..");
const packPath = process.argv[2];

if (!packPath) {
  console.error("usage: node run_profile_capture_projection.mjs <capture_pack.json>");
  process.exit(2);
}

const absPack = path.resolve(packPath);
if (!fs.existsSync(absPack)) {
  console.log(JSON.stringify({ error: "pack_not_found", path: absPack }));
  process.exit(1);
}

const outFile = path.join(os.tmpdir(), `tf_capture_fe_${Date.now()}.json`);
const env = {
  ...process.env,
  PROFILE_CAPTURE_PACK: absPack,
  PROFILE_CAPTURE_FE_OUT: outFile,
};

const jestBin = path.join(frontendRoot, "node_modules", "jest", "bin", "jest.js");
const nodeBin = process.execPath;
const result = spawnSync(
  nodeBin,
  [
    jestBin,
    "--runInBand",
    "--testPathPattern=profileCaptureProjection.cli",
    "--forceExit",
  ],
  {
    cwd: frontendRoot,
    env,
    encoding: "utf8",
  },
);

if (!fs.existsSync(outFile)) {
  console.log(
    JSON.stringify({
      error: "fe_projection_no_output",
      status: result.status,
      error_spawn: result.error ? String(result.error) : null,
      stderr: (result.stderr || "").slice(-2500),
      stdout: (result.stdout || "").slice(-2500),
    }),
  );
  process.exit(1);
}

const payload = fs.readFileSync(outFile, "utf8");
try {
  fs.unlinkSync(outFile);
} catch {
  /* ignore */
}
process.stdout.write(payload.trim() + "\n");
process.exit(result.status === 0 ? 0 : 1);
