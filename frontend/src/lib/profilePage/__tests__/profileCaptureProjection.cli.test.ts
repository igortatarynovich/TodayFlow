/**
 * CLI-only: when PROFILE_CAPTURE_PACK is set, project GET body → QuickMap/visible_blocks.
 * Invoked by frontend/scripts/run_profile_capture_projection.mjs
 */
import fs from "fs";
import path from "path";
import type { CoreProfile } from "@/lib/types";
import { projectCoreProfileForCapture } from "./profileCaptureProjectionHarness";

const packPath = process.env.PROFILE_CAPTURE_PACK;
const outPath = process.env.PROFILE_CAPTURE_FE_OUT;

describe("profileCaptureProjection CLI", () => {
  const run = Boolean(packPath && outPath);

  (run ? it : it.skip)("writes FE projection sidecar for capture pack", () => {
    const abs = path.resolve(packPath as string);
    const pack = JSON.parse(fs.readFileSync(abs, "utf8")) as {
      core_profile_get_response?: CoreProfile | null;
    };
    const core = pack.core_profile_get_response;
    if (!core || typeof core !== "object") {
      fs.writeFileSync(
        outPath as string,
        JSON.stringify({ error: "missing_core_profile_get_response" }),
        "utf8",
      );
      return;
    }
    const result = projectCoreProfileForCapture(core as CoreProfile);
    fs.writeFileSync(outPath as string, JSON.stringify(result), "utf8");
    expect(result.visible_blocks).toBeTruthy();
  });
});
