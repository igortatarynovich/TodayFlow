import { domainSignalWeight, sceneMagnitudeScore } from "@/lib/todayDomainSignal";

describe("todayDomainSignal", () => {
  it("orders irreversibility money > relationships > work > energy", () => {
    expect(domainSignalWeight("money")).toBeGreaterThan(domainSignalWeight("relationships"));
    expect(domainSignalWeight("relationships")).toBeGreaterThan(domainSignalWeight("work"));
    expect(domainSignalWeight("work")).toBeGreaterThan(domainSignalWeight("energy"));
  });

  it("boosts primary role", () => {
    const support = sceneMagnitudeScore({
      sphere: "work",
      role_in_story: "support",
      trap: "t",
    });
    const primary = sceneMagnitudeScore({
      sphere: "work",
      role_in_story: "primary",
      trap: "t",
    });
    expect(primary).toBeGreaterThan(support);
  });
});
