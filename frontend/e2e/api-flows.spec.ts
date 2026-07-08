import { test, expect } from "@playwright/test";
import {
  PLAYWRIGHT_API_BASE,
  E2E_USER_EMAIL,
  E2E_USER_PASSWORD,
  ensureE2eUser,
} from "./helpers";

/** Email, под которым гарантированно есть пользователь с ``E2E_USER_PASSWORD`` (см. beforeAll). */
let loginEmail = E2E_USER_EMAIL;

test.describe("Сценарии с живым API", () => {
  test.describe.configure({ mode: "serial" });

  test.beforeAll(async ({ request }) => {
    let apiOk = false;
    try {
      const probe = await request.get(`${PLAYWRIGHT_API_BASE}/openapi.json`, {
        timeout: 5000,
      });
      apiOk = probe.ok();
    } catch {
      apiOk = false;
    }
    test.skip(
      !apiOk,
      `Нет API на ${PLAYWRIGHT_API_BASE} — для локального E2E: uvicorn todayflow_backend.main:app --host 127.0.0.1 --port 8080 (см. backend/README.md)`,
    );
    if (process.env.E2E_USER_EMAIL) {
      await ensureE2eUser(request);
      loginEmail = E2E_USER_EMAIL;
    } else {
      loginEmail = `e2e-pw-${Date.now()}@example.com`;
      const created = await request.post(`${PLAYWRIGHT_API_BASE}/auth/signup`, {
        data: { email: loginEmail, password: E2E_USER_PASSWORD },
        headers: { "Content-Type": "application/json", Accept: "application/json" },
      });
      expect(
        created.ok(),
        `signup ${loginEmail}: ${created.status()} ${await created.text()}`,
      ).toBeTruthy();
    }
    const probeLogin = await request.post(`${PLAYWRIGHT_API_BASE}/auth/login`, {
      data: { email: loginEmail, password: E2E_USER_PASSWORD },
      headers: { "Content-Type": "application/json", Accept: "application/json" },
    });
    expect(
      probeLogin.ok(),
      `API login ${loginEmail}: ${probeLogin.status()} ${await probeLogin.text()}`,
    ).toBeTruthy();
  });

  test("логин через форму → Today или onboarding профиля", async ({ page }) => {
    await page.goto("/auth?mode=login");
    await expect(page.getByPlaceholder("your@email.com")).toBeVisible({
      timeout: 20_000,
    });
    await page.locator("#email").fill(loginEmail);
    await page.locator("#password").fill(E2E_USER_PASSWORD);
    const [loginResp] = await Promise.all([
      page.waitForResponse(
        (r) =>
          r.url().includes("/auth/login") && r.request().method() === "POST",
      ),
      page.getByRole("button", { name: "Войти", exact: true }).click(),
    ]);
    expect(loginResp.ok(), await loginResp.text()).toBeTruthy();
    await expect(page).toHaveURL(/\/(today|profile)/, { timeout: 25_000 });
  });

  test("хаб Таро загружается с API", async ({ page }) => {
    await page.goto("/tarot");
    await expect(
      page.getByRole("heading", { name: /Таро как ясный слой выбора и смысла/i }),
    ).toBeVisible({ timeout: 20_000 });
  });
});
