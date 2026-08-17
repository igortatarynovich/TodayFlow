import {
  PRODUCT_WEB_LANDING_FOOTER,
  PRODUCT_WEB_LANDING_HERO,
  PRODUCT_WEB_LANDING_SCREENS,
  PRODUCT_WEB_LANDING_SECTION_IDS,
  PRODUCT_WEB_LANDING_TODAY_PROMISE,
  PRODUCT_WEB_LANDING_TRUST,
} from "@/components/product-ui/productWebLandingContent";

describe("productWebLandingContent · copy antipatterns", () => {
  it("does not invent named testimonials with job titles", () => {
    const blob = JSON.stringify({
      promise: PRODUCT_WEB_LANDING_TODAY_PROMISE,
      trust: PRODUCT_WEB_LANDING_TRUST,
      hero: PRODUCT_WEB_LANDING_HERO,
      footer: PRODUCT_WEB_LANDING_FOOTER,
    });
    expect(blob).not.toMatch(/Елена Р\.|Юлиан В\.|Сара Л\./);
    expect(blob).not.toMatch(/Креативный директор|Системный архитектор|Клинический психолог/);
    expect(blob.toLowerCase()).not.toMatch(/testimonial/);
  });

  it("promise theme card avoids bare imperative poster copy", () => {
    const theme = PRODUCT_WEB_LANDING_TODAY_PROMISE.cards.find((c) => c.id === "theme");
    expect(theme?.value).toMatch(/Если с утра/);
    expect(theme?.value).not.toMatch(/^«?Сегодня лучше не спешить/);
  });

  it("landing screens put brand thesis before guest tools", () => {
    expect(PRODUCT_WEB_LANDING_SECTION_IDS).toEqual([
      "hero",
      "trust",
      "today",
      "compatibility",
      "tarot",
      "practices",
      "cta",
    ]);
    expect(PRODUCT_WEB_LANDING_SCREENS).toHaveLength(PRODUCT_WEB_LANDING_SECTION_IDS.length);
    expect(PRODUCT_WEB_LANDING_SECTION_IDS).not.toContain("why");
  });

  it("hero is the locked Trust Layer line, not a continuity slogan", () => {
    expect(PRODUCT_WEB_LANDING_HERO.beats).toEqual([
      "Точные астрономические данные.",
      "Столетия астрологической интерпретации.",
      "Один личный взгляд.",
    ]);
    expect(PRODUCT_WEB_LANDING_HERO.manifesto).toMatch(/NASA JPL/);
    expect(PRODUCT_WEB_LANDING_HERO.manifesto).toMatch(/историческ/);
    expect(PRODUCT_WEB_LANDING_HERO.manifesto).toMatch(/Не гадаем/);
    expect(JSON.stringify(PRODUCT_WEB_LANDING_HERO)).not.toMatch(/видит не только твой день/);
  });

  it("trust copy names NASA/JPL as ephemeris, not as astrology endorsement", () => {
    const blob = `${PRODUCT_WEB_LANDING_HERO.beats.join(" ")} ${PRODUCT_WEB_LANDING_HERO.manifesto} ${JSON.stringify(PRODUCT_WEB_LANDING_TRUST)}`;
    expect(blob).toMatch(/NASA JPL/);
    expect(blob).toMatch(/историческ/);
    expect(blob).toMatch(/личный взгляд/i);
    expect(blob.toLowerCase()).not.toMatch(/powered by nasa|nasa-certified|horizons|научная астрология|единственно верн|алгоритм|фундамент/);
    expect(blob).not.toMatch(/прочитан[ао].*алгоритм/i);
    expect(blob).not.toMatch(/небо не лж/);
  });

  it("trust pillars map to the three trust levels, not one school or a human astrologer", () => {
    expect(PRODUCT_WEB_LANDING_TRUST.items.map((item) => item.kicker)).toEqual([
      "Точность",
      "Глубина",
      "Человечность",
    ]);
    expect(PRODUCT_WEB_LANDING_TRUST.items[0]?.title).toMatch(/Астрономия/);
    expect(PRODUCT_WEB_LANDING_TRUST.body).not.toMatch(/наука/);
    expect(JSON.stringify(PRODUCT_WEB_LANDING_TRUST)).not.toMatch(/школа, которой доверяли/);
  });
});
