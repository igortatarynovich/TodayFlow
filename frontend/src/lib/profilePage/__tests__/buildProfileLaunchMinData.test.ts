import {
  buildProfileChartTeaserLines,
  buildProfileCompatibilityPeople,
} from "@/lib/profilePage/buildProfileLaunchMinData";

describe("buildProfileLaunchMinData", () => {
  it("builds sun/moon/rising teaser lines when layers exist", () => {
    const lines = buildProfileChartTeaserLines({
      sunLayer: { bullets: ["Яркое солнечное проявление."] } as never,
      moonLayer: { bullets: ["Луна через отдых."] } as never,
      risingLayer: null,
      risingHint: "Асцендент уточняется по времени рождения.",
    });

    expect(lines).toHaveLength(3);
    expect(lines[0]).toMatchObject({ id: "sun", label: "Солнце" });
    expect(lines[2].body).toContain("Асцендент");
  });

  it("lists non-self circle profiles with compatibility routes", () => {
    const people = buildProfileCompatibilityPeople(
      [
        { id: 1, label: "Я", relation: "self", is_primary: true },
        { id: 2, label: "Макс", relation: "partner" },
      ],
      1,
    );

    expect(people).toHaveLength(1);
    expect(people[0]).toMatchObject({
      id: 2,
      label: "Макс",
      href: "/compatibility?profile1=1&profile2=2&relation_mode=romantic",
    });
  });
});
