import { resolveArchetypeSlug, archetypeAssetPath, planetAssetPath, resolvePlanetSlug, zodiacAssetPath, elementAssetPath, resolveElementSlug, ARCHETYPE_SLUGS, VISUAL_ASSET_MODE } from "../registry";

describe("visualIdentity registry", () => {
  it("uses asset mode for profile symbols (DS-1 lite)", () => {
    expect(VISUAL_ASSET_MODE).toBe("asset");
  });

  it("resolves RU and EN archetype seeds", () => {
    expect(resolveArchetypeSlug("Sage")).toBe("sage");
    expect(resolveArchetypeSlug("мудрец")).toBe("sage");
    expect(resolveArchetypeSlug("Исследователь")).toBe("explorer");
    expect(resolveArchetypeSlug("Seeker")).toBe("seeker");
    expect(resolveArchetypeSlug("Alchemist")).toBe("catalyst");
    expect(resolveArchetypeSlug("")).toBe("unknown");
  });

  it("maps all 12 named archetypes to public SVG paths", () => {
    expect(ARCHETYPE_SLUGS).toHaveLength(12);
    for (const slug of ARCHETYPE_SLUGS) {
      expect(archetypeAssetPath(slug)).toBe(`/images/icons/archetypes/${slug}.svg`);
    }
  });

  it("maps slugs to public SVG paths", () => {
    expect(archetypeAssetPath("sage")).toBe("/images/icons/archetypes/sage.svg");
    expect(archetypeAssetPath("unknown")).toBe("/images/icons/archetypes/unknown.svg");
    expect(planetAssetPath("moon")).toBe("/images/icons/planets/moon.svg");
    expect(zodiacAssetPath("aquarius")).toBe("/images/icons/zodiac/aquarius.svg");
    expect(elementAssetPath("fire")).toBe("/images/icons/elements/fire.svg");
  });

  it("resolves EN and RU element names", () => {
    expect(resolveElementSlug("Fire")).toBe("fire");
    expect(resolveElementSlug("Вода")).toBe("water");
    expect(resolveElementSlug("unknown")).toBeNull();
  });

  it("resolves EN and RU planet names", () => {
    expect(resolvePlanetSlug("Sun")).toBe("sun");
    expect(resolvePlanetSlug("MERCURY")).toBe("mercury");
    expect(resolvePlanetSlug("Луна")).toBe("moon");
    expect(resolvePlanetSlug("unknown")).toBeNull();
  });
});
