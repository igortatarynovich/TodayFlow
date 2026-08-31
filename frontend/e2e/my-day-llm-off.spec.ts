import { test, expect } from "@playwright/test";
import { PLAYWRIGHT_API_BASE, E2E_USER_PASSWORD } from "./helpers";

test.describe("My Day LLM-OFF", () => {
  test.describe.configure({ mode: "serial" });

  test("новый пользователь без LLM видит персональный сигнал в Мой день", async ({
    page,
    request,
  }) => {
    const email = `e2e-my-day-${Date.now()}@example.com`;
    const password = E2E_USER_PASSWORD;

    const signup = await request.post(`${PLAYWRIGHT_API_BASE}/auth/signup`, {
      data: { email, password },
      headers: { "Content-Type": "application/json", Accept: "application/json" },
    });
    expect(
      signup.ok(),
      `signup ${email}: ${signup.status()} ${await signup.text()}`,
    ).toBeTruthy();

    const login = await request.post(`${PLAYWRIGHT_API_BASE}/auth/login`, {
      data: { email, password },
      headers: { "Content-Type": "application/json", Accept: "application/json" },
    });
    expect(
      login.ok(),
      `login ${email}: ${login.status()} ${await login.text()}`,
    ).toBeTruthy();
    const { token, snapshot } = (await login.json()) as {
      token: string;
      snapshot?: string;
    };

    const profile = await request.post(`${PLAYWRIGHT_API_BASE}/account/core-setup`, {
      data: {
        birth_date: "1990-05-15",
        birth_time: "10:00",
        location_name: "Moscow, Russia",
        first_name: "E2E My Day",
      },
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    expect(
      profile.ok(),
      `core-setup ${email}: ${profile.status()} ${await profile.text()}`,
    ).toBeTruthy();

    const refresh = await request.post(`${PLAYWRIGHT_API_BASE}/today/story/refresh`, {
      data: { target_date: "2026-08-30", timezone: "Europe/Moscow" },
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    expect(
      refresh.ok(),
      `story/refresh ${email}: ${refresh.status()} ${await refresh.text()}`,
    ).toBeTruthy();

    await page.goto("/today");
    await page.evaluate(
      ({ token, snapshot }) => {
        localStorage.setItem("todayflow_token", token);
        if (snapshot) {
          localStorage.setItem("todayflow_auth_snapshot_v1", snapshot);
        }
      },
      { token, snapshot },
    );

    await page.reload();

    const myDayHeading = page.getByText("Мой день").first();
    await expect(myDayHeading).toBeVisible({ timeout: 25_000 });

    const myDaySection = page.locator("[data-testid='today-my-day']");
    await expect(myDaySection).toBeVisible({ timeout: 25_000 });

    const sectionText = await myDaySection.textContent();
    expect(sectionText).not.toContain("Не удалось загрузить");
    expect(sectionText).toMatch(/[Сс]олнце|[Лл]уна|[Мм]еркурий|[Вв]енера|[Мм]арс/);
  });
});
