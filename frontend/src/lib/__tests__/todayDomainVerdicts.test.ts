import {
  DOMAIN_ORDER,
  orderDomainVerdicts,
  type DomainVerdict,
} from "@/lib/todayDomainVerdicts";

describe("todayDomainVerdicts", () => {
  it("orders fixed domains without inventing calm fillers", () => {
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
    expect(ordered.map((r) => r.domain)).toEqual(["money"]);
    expect(ordered[0].verdict).toBe("friction");
  });

  it("keeps full four-domain order when API sent all four", () => {
    const full = DOMAIN_ORDER.map((domain) => ({
      domain,
      verdict: "calm" as const,
      why_short: "Без явного сигнала",
      driver_ids: [] as string[],
      logic_source: "top_driver_v1",
    }));
    expect(orderDomainVerdicts(full).map((r) => r.domain)).toEqual([...DOMAIN_ORDER]);
  });
});
