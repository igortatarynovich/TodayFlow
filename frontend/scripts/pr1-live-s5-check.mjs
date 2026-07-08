/**
 * PR1 live S5 perception check — api_live guide payloads → buildDailyFocusModel.
 * Run: node frontend/scripts/pr1-live-s5-check.mjs
 */
import { readFileSync } from "fs";
import { createRequire } from "module";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);

// ts compiled on the fly via ts-node alternative — use jest/tsx if needed
// Minimal inline: load via dynamic import after registering ts-node
async function main() {
  const { register } = await import("tsx/esm/api");
  register();

  const { buildDailyFocusModel } = await import("../src/lib/todayDailyFocus.ts");

  const jsonlPath = join(__dirname, "../../docs/datasets/raw/generation_logs_ru_v0.jsonl");
  const lines = readFileSync(jsonlPath, "utf8").trim().split("\n");

  const minimalContract = {
    contract_version: "today_contract_v1",
    global_context: { period: "день" },
    personal_growth: { development_point: "" },
    domains: {
      relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
      money_work: { status: "s", opportunity: "o", risk: "r", action: "a" },
      family: { status: "s", opportunity: "o", risk: "r", action: "a" },
    },
    primary_action: "",
    progress: {},
    generation_id: "live-check",
  };

  const PERCEPTION_FAIL = [
    /\bстоит\b/i,
    /\bлучше\b/i,
    /\bобрат/i,
    /\bсосредоточ/i,
    /\bсужай/i,
    /\bвыбери\b/i,
    /\bсделай\b/i,
    /\bобсуд/i,
    /\bне тороп/i,
    /\bдержи\b/i,
    /\bучитывай\b/i,
    /\bудели\b/i,
  ];

  function perceptionVerdict(text) {
    const hits = PERCEPTION_FAIL.filter((p) => p.test(text)).map((p) => p.source);
    return hits.length ? { pass: false, hits } : { pass: true, hits: [] };
  }

  const guides = [];
  for (const line of lines) {
    const row = JSON.parse(line);
    if (row.surface !== "guide" || row.export_kind !== "generation_log") continue;
    const payload = row.output_payload || row.normalized_response;
    if (!payload?.headline) continue;
    guides.push({ id: row.id, created_at: row.created_at, payload });
    if (guides.length >= 12) break;
  }

  // pick 3 spaced samples
  const picks = [guides[0], guides[3], guides[6]].filter(Boolean);

  console.log("=== PR1 Live S5 (api_live payloads → Daily Focus) ===\n");

  let allPass = true;
  for (const g of picks) {
    const model = buildDailyFocusModel(minimalContract, g.payload);
    const shown = [model.title, ...model.lines].join("\n");
    const v = perceptionVerdict(shown);
    if (!v.pass) allPass = false;

    console.log(`--- log id=${g.id} ${g.created_at} ---`);
    console.log(`TITLE: ${model.title}`);
    for (const l of model.lines) console.log(`LINE:  ${l}`);
    console.log(`PERCEPTION: ${v.pass ? "PASS" : "FAIL"} ${v.hits.join(", ") || ""}`);
    console.log(`RAW headline (not shown): ${(g.payload.headline || "").slice(0, 80)}…`);
    console.log();
  }

  console.log(`OVERALL perception: ${allPass ? "PASS (3/3)" : "FAIL — see above"}`);
  process.exit(allPass ? 0 : 1);
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
