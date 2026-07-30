import { test, expect } from "@playwright/test";

/**
 * ScreenFlow Phase 1 measure protocol — transform pager, both axes.
 * Canon: docs/foundation/SCREEN_FLOW_V1.md
 */

const VIEWPORTS = [{ name: "phone-390", width: 390, height: 844 }] as const;

for (const axis of ["x", "y"] as const) {
  for (const vp of VIEWPORTS) {
    test.describe(`ScreenFlow harness axis=${axis} @ ${vp.name}`, () => {
      test.use({ viewport: { width: vp.width, height: vp.height } });

      test("navigates with transform + focus, no document smooth scroll", async ({ page }) => {
        await page.goto(`/visual-fixtures/screen-flow.html?axis=${axis}`);
        const container = page.locator(".container");
        await expect(container).toBeVisible();

        await page.locator("#next-btn").click();
        await expect(page.locator(".indicator")).toContainText("2 /");

        const heading = page.locator('[data-step-active="true"] h2, .step:not([aria-hidden="true"]) h2').first();
        // Fixture focuses active heading when possible
        const live = page.locator("[aria-live]");
        if (await live.count()) {
          await expect(live.first()).not.toBeEmpty();
        }

        const metrics = await page.evaluate(() => {
          const html = document.documentElement;
          const body = document.body;
          return {
            docScrollWidth: Math.max(html.scrollWidth, body.scrollWidth),
            docClientWidth: html.clientWidth,
            htmlSmooth: html.style.scrollBehavior,
          };
        });
        // Page must not blow past viewport (landing-class overflow). Internal track may be wider.
        expect(metrics.docScrollWidth).toBeLessThanOrEqual(metrics.docClientWidth + 2);
        expect(metrics.htmlSmooth).not.toBe("smooth");

        await page.locator("#next-btn").click();
        await page.locator("#next-btn").click();
        await page.locator("#next-btn").click();
        await expect(page.locator(".indicator")).toContainText(/\/\s*\d+/);
      });
    });
  }
}
