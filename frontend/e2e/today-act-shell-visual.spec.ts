import { test, expect } from "@playwright/test";

/**
 * Wave 1 visual regression — ActShell page scenario at phone + tablet widths.
 * Fixture mirrors TodayActShell layout contract (full-bleed + one gutter + vertical dual).
 */
const VIEWPORTS = [
  { name: "phone-390", width: 390, height: 844 },
  { name: "tablet-768", width: 768, height: 1024 },
] as const;

for (const vp of VIEWPORTS) {
  test.describe(`Today ActShell visual @ ${vp.name}`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } });

    test("matches layout snapshot", async ({ page }) => {
      await page.goto("/visual-fixtures/today-act-shell.html");
      await expect(page.getByTestId("today-act-shell-fixture")).toBeVisible();
      await expect(page.locator("[data-today-act-shell='true']")).toHaveCount(5);
      await expect(page.getByTestId("today-slot-verdict-strip")).toBeVisible();
      await expect(page.getByTestId("today-slot-glance-timeline")).toBeVisible();
      await expect(page.getByTestId("today-slot-tap-widget")).toBeVisible();

      await expect(page).toHaveScreenshot(`today-act-shell-${vp.name}.png`, {
        fullPage: true,
        animations: "disabled",
      });
    });
  });
}
