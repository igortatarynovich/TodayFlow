import {
  DOMAIN_ORDER,
  orderDomainVerdicts,
  type DomainVerdict,
} from "@/lib/todayDomainVerdicts";

describe("todayDomainVerdicts", () => {
  it("orders fixed four domains and fills calm gaps", () => {
    const partial: DomainVerdict[] = [
      {
        domain: "money",
        verdict: "friction",
        why_short: "Сатурн: квадрат к Венера",
        driver_ids: ["a"],
        logic_source: "top_driver_v1",
      },
    ];
    const ordered = orderDomainVerdicts(partial);
    expect(ordered.map((r) => r.domain)).toEqual([...DOMAIN_ORDER]);
    expect(ordered[0].verdict).toBe("calm");
    expect(ordered[1].verdict).toBe("friction");
    expect(ordered[1].why_short).toContain("Сатурн");
  });
});
