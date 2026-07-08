import * as fs from "fs";
import * as path from "path";
import {
  buildProfileV0ViewModel,
  formatCoverageReportMarkdown,
} from "@/lib/profilePage/buildProfileV0Data";
import {
  IGOR_SAGE_7_FIXTURE,
  IGOR_SAGE_7_LABEL,
} from "@/lib/profilePage/fixtures/igorSage7ProfileFixture";

describe("Profile v0 Igor taxonomy audit", () => {
  it("produces coverage table for Igor / Sage / 7", () => {
    const model = buildProfileV0ViewModel({
      core: IGOR_SAGE_7_FIXTURE,
      displayName: "Igor",
      auditProfileLabel: IGOR_SAGE_7_LABEL,
    });

    const { coverage } = model.taxonomyAudit;
    const md = formatCoverageReportMarkdown(coverage);

    const outPath = path.join(
      __dirname,
      "../../../../../docs/status/PROFILE_V0_IGOR_TAXONOMY_AUDIT.md",
    );
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, md, "utf8");

    expect(coverage.rows.length).toBe(31);
    expect(coverage.summary.filled).toBe(29);
    expect(coverage.summary.unique).toBe(29);
    expect(coverage.summary.duplicate).toBe(0);
    expect(coverage.summary.weak).toBe(0);
    expect(coverage.summary.missing).toBe(2);

    // eslint-disable-next-line no-console
    console.log("\n--- Igor taxonomy audit summary ---");
    // eslint-disable-next-line no-console
    console.log(JSON.stringify(coverage.summary, null, 2));
    // eslint-disable-next-line no-console
    console.log(`Written: ${outPath}`);
  });
});
