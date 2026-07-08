import { test, expect } from "@playwright/test";

test.describe("Авторизация", () => {
  test("форма входа на /auth", async ({ page }) => {
    await page.goto("/auth?mode=login");
    await expect(page.getByText("TodayFlow").first()).toBeVisible({ timeout: 20_000 });
    await expect(page.getByPlaceholder("your@email.com")).toBeVisible();
    await expect(page.getByPlaceholder("Введите пароль")).toBeVisible();
  });
});
