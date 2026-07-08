import { test, expect } from "@playwright/test";

test.describe("Главная (гость)", () => {
  test("hero и вход в приложение", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /Узнай, что для тебя актуально сегодня/i }),
    ).toBeVisible({ timeout: 20_000 });
    const cta = page.getByRole("link", { name: "Начать", exact: true });
    await expect(cta).toBeVisible();
    await expect(cta).toHaveAttribute("href", "/auth");
  });
});
