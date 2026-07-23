import {
  resolveArchetypeSlug,
  archetypeAssetPath,
  archetypeDisplayLabel,
  archetypeIllustrationPath,
  archetypeIllustrationSrc,
  resolveArchetypeIllustrationSlug,
  planetAssetPath,
  resolvePlanetSlug,
  zodiacAssetPath,
  elementAssetPath,
  resolveElementSlug,
  ARCHETYPE_SLUGS,
  VISUAL_ASSET_MODE,
} from "../registry";

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

  it("localizes archetype display labels by locale", () => {
    expect(archetypeDisplayLabel("Sage")).toBe("Мудрец");
    expect(archetypeDisplayLabel("Sage", "en")).toBe("Sage");
    expect(archetypeDisplayLabel("Architect", "ru")).toBe("Архитектор");
    expect(archetypeDisplayLabel("")).toBe("Личный архетип");
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

  it("maps all 12 production seeds to Pearson illustration slugs", () => {
    expect(resolveArchetypeIllustrationSlug("Architect")).toBe("pravitel");
    expect(resolveArchetypeIllustrationSlug("Creator")).toBe("tvorets");
    expect(resolveArchetypeIllustrationSlug("Sage")).toBe("mudrets");
    expect(resolveArchetypeIllustrationSlug("Strategist")).toBe("geroi");
    expect(resolveArchetypeIllustrationSlug("Catalyst")).toBe("buntar");
    expect(resolveArchetypeIllustrationSlug("Harmonizer")).toBe("liubovnik");
    expect(resolveArchetypeIllustrationSlug("Seeker")).toBe("iskatel");
    expect(resolveArchetypeIllustrationSlug("Explorer")).toBe("iskatel");
    expect(resolveArchetypeIllustrationSlug("shut")).toBe("shut");
    expect(resolveArchetypeIllustrationSlug("Guardian")).toBe("zabotlivyi");
    expect(resolveArchetypeIllustrationSlug("Mentor")).toBe("mag");
    expect(resolveArchetypeIllustrationSlug("Visionary")).toBe("nevinnyi");
    expect(resolveArchetypeIllustrationSlug("Observer")).toBe("slavnyi_malyi");
    expect(resolveArchetypeIllustrationSlug("pravitel")).toBe("pravitel");
    expect(resolveArchetypeIllustrationSlug("Любовник")).toBe("liubovnik");
    expect(resolveArchetypeIllustrationSlug("unknown-seed")).toBeNull();
    expect(archetypeIllustrationSrc("Architect")).toBe("/images/archetypes/pravitel.webp");
    expect(archetypeIllustrationPath("geroi")).toBe("/images/archetypes/geroi.webp");
  });
});
