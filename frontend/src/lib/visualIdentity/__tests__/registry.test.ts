import {
  resolveArchetypeSlug,
  archetypeAssetPath,
  archetypeDisplayLabel,
  archetypeIllustrationPath,
  archetypeIllustrationSrc,
  resolveArchetypeIllustrationSlug,
  planetAssetPath,
  planetHasPhotoAsset,
  planetPhotoPath,
  earthPhotoPath,
  chartAngleAssetPath,
  zodiacOrbAssetPath,
  celestialKitDecorPath,
  resolvePlanetSlug,
  zodiacAssetPath,
  zodiacIllustrationPath,
  zodiacIllustrationSrc,
  resolveZodiacIllustrationSlug,
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
    expect(zodiacAssetPath("aquarius")).toBe("/images/icons/zodiac/aquarius.webp");
    expect(elementAssetPath("fire")).toBe("/images/icons/elements/fire.svg");
  });

  it("maps zodiac signs to painterly illustration WebP paths", () => {
    expect(zodiacIllustrationPath("aries")).toBe("/images/zodiac/aries.webp");
    expect(zodiacIllustrationSrc("Aquarius")).toBe("/images/zodiac/aquarius.webp");
    expect(zodiacIllustrationSrc("Водолей")).toBe("/images/zodiac/aquarius.webp");
    expect(resolveZodiacIllustrationSlug("Рыбы")).toBe("pisces");
    expect(zodiacIllustrationSrc("")).toBeNull();
    expect(resolveZodiacIllustrationSlug("Ophiuchus")).toBeNull();
  });

  it("prefers photo WebP for all ten traditional chart planets", () => {
    expect(planetHasPhotoAsset("sun")).toBe(true);
    expect(planetHasPhotoAsset("mercury")).toBe(true);
    expect(planetHasPhotoAsset("pluto")).toBe(true);
    expect(planetPhotoPath("saturn")).toBe("/images/icons/planets/saturn.webp");
    expect(planetPhotoPath("mercury")).toBe("/images/icons/planets/mercury.webp");
    expect(earthPhotoPath()).toBe("/images/icons/planets/earth.webp");
  });

  it("maps celestial-kit chart accents", () => {
    expect(chartAngleAssetPath("asc")).toBe("/images/icons/angles/asc.webp");
    expect(zodiacOrbAssetPath("leo")).toBe("/images/icons/zodiac-orbs/leo.webp");
    expect(celestialKitDecorPath("star-gold")).toBe("/images/decorative/kit/star-gold.webp");
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
