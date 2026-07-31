import { DOMAIN_ORDER, type DomainVerdict } from "@/lib/todayDomainVerdicts";
import { compressGlanceDomainVerdicts } from "@/lib/todayGlanceSpheres";

function row(domain: DomainVerdict["domain"], verdict: DomainVerdict["verdict"], why: string): DomainVerdict {
  return {
    domain,
    verdict,
    why_short: why,
    driver_ids: ["d"],
    logic_source: "top_driver_v1",
  };
}

describe("compressGlanceDomainVerdicts", () => {
  it("collapses all-same open day into one unanimous line", () => {
    const rows = DOMAIN_ORDER.map((domain, i) =>
      row(domain, "open", `why-${i}`),
    );
    const blocks = compressGlanceDomainVerdicts(rows);
    expect(blocks).toHaveLength(1);
    expect(blocks[0]).toMatchObject({
      kind: "compact",
      allSame: true,
      verdict: "open",
    });
    if (blocks[0].kind === "compact") {
      expect(blocks[0].label).toContain("ровный по всем направлениям");
    }
  });

  it("collapses 3 open + keeps friction outlier as card", () => {
    const rows: DomainVerdict[] = [
      row("work", "open", "w"),
      row("money", "open", "m"),
      row("relationships", "open", "r"),
      row("energy", "friction", "e"),
    ];
    const blocks = compressGlanceDomainVerdicts(rows);
    expect(blocks).toHaveLength(2);
    expect(blocks[0]).toMatchObject({
      kind: "compact",
      verdict: "open",
      allSame: false,
    });
    if (blocks[0].kind === "compact") {
      expect(blocks[0].label).toBe("Работа · Деньги · Отношения — открыто");
    }
    expect(blocks[1]).toMatchObject({
      kind: "card",
      row: expect.objectContaining({ domain: "energy", verdict: "friction" }),
    });
  });

  it("keeps four cards when no majority of 3+", () => {
    const rows: DomainVerdict[] = [
      row("work", "open", "w"),
      row("money", "open", "m"),
      row("relationships", "friction", "r"),
      row("energy", "charged", "e"),
    ];
    const blocks = compressGlanceDomainVerdicts(rows);
    expect(blocks.every((b) => b.kind === "card")).toBe(true);
    expect(blocks).toHaveLength(4);
  });

  it("returns empty for empty input", () => {
    expect(compressGlanceDomainVerdicts([])).toEqual([]);
  });
});
