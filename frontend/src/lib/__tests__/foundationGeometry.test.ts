import { resolveGeometryPreset } from "@/lib/foundationGeometry";

describe("resolveGeometryPreset", () => {
  it("returns explicit preset when provided", () => {
    expect(resolveGeometryPreset("today", "soft")).toBe("today");
    expect(resolveGeometryPreset("profile", "strong")).toBe("profile");
  });

  it("defaults to profile for soft emphasis", () => {
    expect(resolveGeometryPreset(undefined, "soft")).toBe("profile");
  });

  it("defaults to portal for strong emphasis", () => {
    expect(resolveGeometryPreset(undefined, "strong")).toBe("portal");
  });
});
