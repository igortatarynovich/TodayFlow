import {
  stripHouseThemePrefix,
  withLifeSphereHowFrame,
  withRelationshipFrame,
} from "@/lib/profilePage/profileSphereCopy";

describe("profileSphereCopy", () => {
  it("strips house theme prefix before framing", () => {
    expect(stripHouseThemePrefix("7 дом: Про отношения из карты.")).toBe("Про отношения из карты.");
  });

  it("frames love sphere how as portrait layer", () => {
    const framed = withLifeSphereHowFrame("love", "7 дом: Про отношения из карты.");
    expect(framed).toMatch(/^В отношениях/i);
    expect(framed).not.toMatch(/7\s*дом/i);
  });

  it("does not double-frame relationship copy", () => {
    const once = withRelationshipFrame("В отношениях ты бережёшь дистанцию.");
    expect(once).toBe("В отношениях ты бережёшь дистанцию.");
  });
});
