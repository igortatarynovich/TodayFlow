import { test, expect } from "@playwright/test";
import { PLAYWRIGHT_API_BASE, E2E_USER_PASSWORD } from "./helpers";

test.use({ timezoneId: "Europe/Moscow" });

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

    // Warm *today* (MSK). A hardcoded yesterday date left /today on an
    // unbuilt contract whose interpretation_status=unavailable and empty
    // day_personal painted My Day as «Не удалось загрузить.»
    const today = new Intl.DateTimeFormat("sv-SE", {
      timeZone: "Europe/Moscow",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(new Date());

    const refresh = await request.post(`${PLAYWRIGHT_API_BASE}/today/story/refresh`, {
      data: { target_date: today, timezone: "Europe/Moscow" },
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

    const contractRes = await request.get(
      `${PLAYWRIGHT_API_BASE}/today/contract?target_date=${today}&timezone=Europe/Moscow`,
      { headers: { Authorization: `Bearer ${token}`, Accept: "application/json" } },
    );
    expect(
      contractRes.ok(),
      `today/contract ${email}: ${contractRes.status()} ${await contractRes.text()}`,
    ).toBeTruthy();
    const contract = (await contractRes.json()) as {
      day_story?: {
        day_personal?: {
          summary_ru?: string;
          personal_astrology?: { beats?: unknown[]; summary_ru?: string };
        };
      };
    };
    const dayPersonal = contract.day_story?.day_personal;
    const hasDeterministicPersonal =
      Boolean(dayPersonal?.summary_ru?.trim()) ||
      Boolean(dayPersonal?.personal_astrology?.summary_ru?.trim()) ||
      Boolean(dayPersonal?.personal_astrology?.beats?.length);
    expect(
      hasDeterministicPersonal,
      "LLM-off contract must carry deterministic day_personal (astro/IL), not an empty unavailable shell",
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
    await expect(page.getByTestId("today-my-day-unavailable")).toHaveCount(0);

    // Headline/bridge may honest-omit when summary is a generic placeholder
    // and natal-transit beat titles are empty. Launch contract is: My Day
    // renders the deterministic pane, not the unavailable card.
    const pane = page.getByTestId("today-my-day");
    await expect(pane).not.toHaveAttribute("data-fallback", "unavailable");
  });
});
