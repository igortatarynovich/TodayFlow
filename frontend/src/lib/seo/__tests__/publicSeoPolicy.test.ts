import { PUBLIC_SEO_BY_SEGMENT, ROBOTS_DISALLOW_PREFIXES, metadataForSegment } from "@/lib/seo/publicSeoPolicy";

describe("publicSeoPolicy", () => {
  it("marks personal shells as noindex and guest trials as indexable", () => {
    expect(PUBLIC_SEO_BY_SEGMENT.today.robots).toMatchObject({ index: false });
    expect(PUBLIC_SEO_BY_SEGMENT.profile.sitemap).toBe(false);
    expect(PUBLIC_SEO_BY_SEGMENT.compatibility.sitemap).toBe(true);
    expect(PUBLIC_SEO_BY_SEGMENT.tarot.robots).toMatchObject({ index: true });
  });

  it("keeps unique titles for closed routes", () => {
    expect(metadataForSegment("today").title).toBe("Сегодня");
    expect(metadataForSegment("auth").title).toBe("Вход");
    expect(metadataForSegment("compatibility").description).toMatch(/Динамика связи/);
  });

  it("disallows app prefixes in robots policy", () => {
    expect(ROBOTS_DISALLOW_PREFIXES).toEqual(
      expect.arrayContaining(["/today", "/profile", "/account", "/auth", "/onboarding"]),
    );
    expect(ROBOTS_DISALLOW_PREFIXES).not.toContain("/compatibility");
    expect(ROBOTS_DISALLOW_PREFIXES).not.toContain("/tarot");
    expect(ROBOTS_DISALLOW_PREFIXES).not.toContain("/practices");
  });
});
