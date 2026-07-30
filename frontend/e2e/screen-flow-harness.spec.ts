import { test, expect } from "@playwright/test";

/**
 * ScreenFlow axis protocol — transform pager + swipe / deadzone.
 * Canon: docs/foundation/SCREEN_FLOW_V1.md §2 (Today locks x).
 */

const VIEWPORTS = [{ name: "phone-390", width: 390, height: 844 }] as const;

async function swipe(
  page: import("@playwright/test").Page,
  opts: { x0: number; y0: number; x1: number; y1: number },
) {
  await page.evaluate(({ x0, y0, x1, y1 }) => {
    const el = document.querySelector(".container") || document.body;
    const fire = (type: string, x: number, y: number, touchesActive: boolean) => {
      const t = new Touch({ identifier: 1, target: el, clientX: x, clientY: y });
      el.dispatchEvent(
        new TouchEvent(type, {
          bubbles: true,
          cancelable: true,
          touches: touchesActive ? [t] : [],
          targetTouches: touchesActive ? [t] : [],
          changedTouches: [t],
        }),
      );
    };
    fire("touchstart", x0, y0, true);
    fire("touchmove", (x0 + x1) / 2, (y0 + y1) / 2, true);
    fire("touchmove", x1, y1, true);
    fire("touchend", x1, y1, false);
  }, opts);
}

for (const axis of ["x", "y"] as const) {
  for (const vp of VIEWPORTS) {
    test.describe(`ScreenFlow harness axis=${axis} @ ${vp.name}`, () => {
      test.use({ viewport: { width: vp.width, height: vp.height }, hasTouch: true });

      test("navigates with transform + focus, no document smooth scroll", async ({ page }) => {
        await page.goto(`/visual-fixtures/screen-flow.html?axis=${axis}`);
        const container = page.locator(".container");
        await expect(container).toBeVisible();

        await page.locator("#next-btn").click();
        await expect(page.locator(".indicator")).toContainText("2 /");

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

test.describe("ScreenFlow harness axis=x swipe + deadzone @ phone-390", () => {
  test.use({ viewport: { width: 390, height: 844 }, hasTouch: true });

  test("center swipe advances; left-edge swipe does not", async ({ page }) => {
    await page.goto(`/visual-fixtures/screen-flow.html?axis=x`);
    await expect(page.locator(".indicator")).toContainText("1 /");

    await swipe(page, { x0: 8, y0: 400, x1: -80, y1: 400 });
    await expect(page.locator(".indicator")).toContainText("1 /");

    await swipe(page, { x0: 280, y0: 400, x1: 80, y1: 400 });
    await expect(page.locator(".indicator")).toContainText("2 /");
  });
});
