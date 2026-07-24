import {
  PRODUCT_WEB_LANDING_RETURN_REASONS,
  PRODUCT_WEB_LANDING_TODAY_PROMISE,
} from "@/components/product-ui/productWebLandingContent";

describe("productWebLandingContent · copy antipatterns", () => {
  it("does not invent named testimonials with job titles", () => {
    const blob = JSON.stringify({
      reasons: PRODUCT_WEB_LANDING_RETURN_REASONS,
      promise: PRODUCT_WEB_LANDING_TODAY_PROMISE,
    });
    expect(blob).not.toMatch(/Елена Р\.|Юлиан В\.|Сара Л\./);
    expect(blob).not.toMatch(/Креативный директор|Системный архитектор|Клинический психолог/);
    expect(blob.toLowerCase()).not.toMatch(/testimonial/);
  });

  it("return reasons are product facts, not attributed quotes", () => {
    expect(PRODUCT_WEB_LANDING_RETURN_REASONS.items).toHaveLength(3);
    for (const item of PRODUCT_WEB_LANDING_RETURN_REASONS.items) {
      expect(item.title.trim().length).toBeGreaterThan(0);
      expect(item.body.trim().length).toBeGreaterThan(20);
      expect(item).not.toHaveProperty("name");
      expect(item).not.toHaveProperty("role");
      expect(item).not.toHaveProperty("quote");
    }
  });

  it("promise theme card avoids bare imperative poster copy", () => {
    const theme = PRODUCT_WEB_LANDING_TODAY_PROMISE.cards.find((c) => c.id === "theme");
    expect(theme?.value).toMatch(/Если с утра/);
    expect(theme?.value).not.toMatch(/^«?Сегодня лучше не спешить/);
  });
});
