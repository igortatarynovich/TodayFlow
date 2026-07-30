import {
  DOMAIN_ORDER,
  isSilentCalmBank,
  orderDomainVerdicts,
  type DomainVerdict,
} from "@/lib/todayDomainVerdicts";

describe("todayDomainVerdicts", () => {
  it("orders fixed domains without inventing calm fillers", () => {
    const partial: DomainVerdict[] = [
      {
        domain: "money",
        verdict: "friction",
        why_short: "Есть сопротивление — короче шаг",
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
      why_short: "Поле ровное — без лишнего давления",
      driver_ids: [] as string[],
      logic_source: "top_driver_v1",
    }));
    expect(orderDomainVerdicts(full).map((r) => r.domain)).toEqual([...DOMAIN_ORDER]);
  });

  it("flags identical why across four domains as silent (calm empty)", () => {
    const bank = DOMAIN_ORDER.map((domain) => ({
      domain,
      verdict: "calm" as const,
      why_short: "Без явного сигнала",
      driver_ids: [] as string[],
      logic_source: "top_driver_v1",
    }));
    expect(isSilentCalmBank(bank)).toBe(true);
  });

  it("flags identical open/support collapse as silent even with drivers", () => {
    const bank = DOMAIN_ORDER.map((domain, i) => ({
      domain,
      verdict: "open" as const,
      why_short: "Есть опора — можно опереться",
      driver_ids: [`d${i}`],
      logic_source: "top_driver_v1",
    }));
    expect(isSilentCalmBank(bank)).toBe(true);
  });

  it("does not flag differentiated soft domains as silent bank", () => {
    const quiet: DomainVerdict[] = [
      { domain: "work", verdict: "open", why_short: "В деле есть опора — можно опереться", driver_ids: ["a"], logic_source: "top_driver_v1" },
      { domain: "money", verdict: "open", why_short: "В ресурсах тише — без резких ходов", driver_ids: ["b"], logic_source: "top_driver_v1" },
      { domain: "relationships", verdict: "open", why_short: "В контакте мягче — есть на что опереться", driver_ids: ["c"], logic_source: "top_driver_v1" },
      { domain: "energy", verdict: "open", why_short: "В теле ровнее — можно опереться на ритм", driver_ids: ["d"], logic_source: "top_driver_v1" },
    ];
    expect(isSilentCalmBank(quiet)).toBe(false);
  });
});
