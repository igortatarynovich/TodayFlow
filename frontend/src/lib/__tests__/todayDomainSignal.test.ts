import {
  domainSignalWeight,
  mapSphereToDomain,
  sceneMagnitudeScore,
} from "@/lib/todayDomainSignal";

describe("todayDomainSignal", () => {
  it("orders irreversibility money > relationships > work > energy", () => {
    expect(domainSignalWeight("money")).toBeGreaterThan(domainSignalWeight("relationships"));
    expect(domainSignalWeight("relationships")).toBeGreaterThan(domainSignalWeight("work"));
    expect(domainSignalWeight("work")).toBeGreaterThan(domainSignalWeight("energy"));
  });

  it("maps legacy and extended spheres onto fixed-4", () => {
    expect(mapSphereToDomain("communication")).toBe("relationships");
    expect(mapSphereToDomain("home")).toBe("relationships");
    expect(mapSphereToDomain("energy_body")).toBe("energy");
    expect(mapSphereToDomain("creativity")).toBe("energy");
    expect(mapSphereToDomain("rest_travel")).toBe("energy");
    expect(mapSphereToDomain("money_work")).toBe("money");
    expect(mapSphereToDomain("family")).toBe("relationships");
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
