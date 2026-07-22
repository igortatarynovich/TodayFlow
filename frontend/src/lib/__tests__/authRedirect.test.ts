import { resolvePostCoreAuthTarget } from "@/lib/authRedirect";

describe("resolvePostCoreAuthTarget", () => {
  it("routes to Profile when core path is ready (First Today is optional)", () => {
    expect(resolvePostCoreAuthTarget()).toBe("/profile");
  });
});
