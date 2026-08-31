import { test, expect } from "@playwright/test";

test.describe("Главная (гость)", () => {
  test("hero и вход в приложение", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /Точные астрономические данные/i }),
    ).toBeVisible({ timeout: 20_000 });
    const cta = page.getByRole("link", { name: /Смотреть пример дня/i }).first();
    await expect(cta).toBeVisible();
    await expect(cta).toHaveAttribute("href", "/demo/today");
  });
});
