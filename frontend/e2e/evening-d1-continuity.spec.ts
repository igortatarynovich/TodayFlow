import { test, expect } from "@playwright/test";
import { PLAYWRIGHT_API_BASE, E2E_USER_PASSWORD } from "./helpers";

/**
 * Evening close + D+1 continuity — LLM-OFF regression.
 *
 * Verifies the actual user path:
 * 1. New user completes onboarding and pre-warms today's deterministic story.
 * 2. At evening time, the Today screen shows the evening step and the
 *    "Закрыть день" button.
 * 3. Closing the day stores the outcome/reflection locally and renders the
 *    closed-day state from the morning focus (deterministic theme short).
 * 4. When the calendar advances to the next day, Today picks up yesterday's
 *    closed focus/outcome via the continuity recall slot.
 *
 * This test uses Playwright's context clock to simulate evening and the next
 * morning, and the real localStorage continuity build-path (no injected fake
 * records). It is a single serial test because the evening close must happen
 * before the next-day continuity assertion.
 */
test.use({ timezoneId: "Europe/Moscow" });

test.describe("Evening close and D+1 continuity", () => {
  test.describe.configure({ mode: "serial" });

  test("закрывает день и на следующий день видит continuity", async ({
    page,
    request,
    context,
  }) => {
    const email = `e2e-evening-d1-${Date.now()}@example.com`;
    const password = E2E_USER_PASSWORD;

    const signup = await request.post(`${PLAYWRIGHT_API_BASE}/auth/signup`, {
      data: { email, password },
      headers: { "Content-Type": "application/json", Accept: "application/json" },
    });
    expect(
      signup.ok() || signup.status() === 400,
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
        first_name: "E2E Evening",
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

    // Dates must follow the real clock (server cycle date = real MSK date);
    // hardcoded dates skew the continuity record key one day off.
    const mskFmt = (d: Date) =>
      new Intl.DateTimeFormat("sv-SE", {
        timeZone: "Europe/Moscow",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      }).format(d);
    const nowReal = new Date();
    const today = mskFmt(nowReal);
    const tomorrow = mskFmt(new Date(nowReal.getTime() + 86_400_000));

    const warmToday = await request.post(`${PLAYWRIGHT_API_BASE}/today/story/refresh`, {
      data: { target_date: today, timezone: "Europe/Moscow" },
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    expect(
      warmToday.ok(),
      `story/refresh today ${email}: ${warmToday.status()} ${await warmToday.text()}`,
    ).toBeTruthy();

    // Simulate evening of today so the close-day UI is available.
    await context.clock.setFixedTime(new Date(`${today}T20:00:00+03:00`));

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

    // Start the day flow and jump to the evening step.
    const cta = page.getByTestId("today-day-personal-cta");
    await expect(
      cta,
      "Today step should have a continue CTA",
    ).toBeVisible({ timeout: 25_000 });
    await cta.click();
    await page.waitForTimeout(500);

    const lastDot = page.locator('[data-testid^="screen-flow-dot-"]').last();
    await expect(
      lastDot,
      "last screen-flow dot should be visible",
    ).toBeVisible({ timeout: 10_000 });
    await lastDot.click();
    await page.waitForTimeout(500);

    await expect(
      page.getByTestId("today-frame-evening"),
      "evening screen-flow step should be visible",
    ).toBeVisible({ timeout: 10_000 });

    // The legacy stacked path has a hidden button with the same test id; use the last visible one.
    const closeBtn = page.locator('[data-testid="today-evening-open"]').last();
    await expect(
      closeBtn,
      "close-day button should be offered in the evening step",
    ).toBeVisible({ timeout: 10_000 });
    await closeBtn.click({ force: true });

    // The existing close form renders with the deterministic morning focus.
    await expect(
      page.getByTestId("today-composition-evening"),
      "close form should open",
    ).toBeVisible({ timeout: 10_000 });

    // Promise suggestions may be unavailable in LLM-OFF; skip the picker and
    // fall back to the deterministic theme short as the day's main focus.
    const skipPromise = page.getByTestId("evening-promise-skip");
    if (await skipPromise.isVisible().catch(() => false)) {
      await skipPromise.click();
    }

    await page.getByTestId("day-continuity-outcome-done").click();
    await page.getByTestId("day-continuity-submit").click();

    await expect(
      page.getByTestId("today-day-continuity-closed"),
      "closed-day state should be shown after submit",
    ).toBeVisible({ timeout: 10_000 });

    const closedText = await page.getByTestId("today-day-continuity-closed").textContent();
    expect(closedText).toContain("День закрыт");
    expect(closedText).toContain("Получилось");
    expect(closedText).not.toContain("Не удалось загрузить");

    const focusText = await page
      .locator("[data-testid='today-day-continuity-closed'] h2")
      .textContent();
    expect(focusText).toBeTruthy();

    // --- D+1 continuity ---

    // Capture the ready contract for today so we can serve a deterministic,
    // non-assembling "tomorrow" contract to the frontend without changing the
    // production API. The backend's real server date is still today; the
    // browser calendar is advanced, and the continuity record from localStorage
    // is the genuine closed-day outcome.
    const todayContractResponse = await request.get(
      `${PLAYWRIGHT_API_BASE}/today/contract?target_date=${today}&timezone=Europe/Moscow`,
      {
        headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
      },
    );
    expect(
      todayContractResponse.ok(),
      `fetch today contract: ${todayContractResponse.status()} ${await todayContractResponse.text()}`,
    ).toBeTruthy();
    const todayContract = (await todayContractResponse.json()) as Record<string, unknown>;

    const tomorrowContract = JSON.parse(JSON.stringify(todayContract)) as Record<string, unknown>;
    const progress = (tomorrowContract.progress as Record<string, unknown>) ?? {};
    const lifecycle = ((progress.day_lifecycle as Record<string, unknown>) ?? {}) as Record<string, unknown>;
    lifecycle.status = "ready";
    lifecycle.local_date = tomorrow;
    lifecycle.target_date = tomorrow;
    progress.day_lifecycle = lifecycle;
    progress.story_status = "ok";
    tomorrowContract.progress = progress;

    // Advance the clock to the next morning.
    await context.clock.setFixedTime(new Date(`${tomorrow}T08:00:00+03:00`));

    // Serve the captured, non-assembling contract and a minimal tomorrow cycle.
    // 404 on progressive endpoints forces the provider to fall back to /today.
    // The frontend build may point at a different API host than
    // PLAYWRIGHT_API_BASE (localhost vs 127.0.0.1), and a bare `**/today`
    // glob would also swallow the frontend's own /today document — so match
    // API calls by "any port except the web server's".
    const webPort = new URL(page.url()).port;
    const isApi = (url: URL) => url.port !== webPort;
    await page.route((url) => isApi(url) && url.pathname === "/today/opening", async (route) => {
      await route.fulfill({ status: 404, body: "not used in test" });
    });
    await page.route((url) => isApi(url) && url.pathname === "/today/bundle", async (route) => {
      await route.fulfill({ status: 404, body: "not used in test" });
    });
    await page.route((url) => isApi(url) && url.pathname === "/today", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          date: tomorrow,
          morning: null,
          morning_completed: false,
          day_connection: null,
          day_trackers: [],
          day_journal_entries: [],
          day_completed: false,
          evening: null,
          evening_completed: false,
          morning_available: true,
          day_available: true,
          evening_available: false,
        }),
      });
    });
    await page.route((url) => isApi(url) && url.pathname === "/today/contract", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(tomorrowContract),
      });
    });

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

    await expect(
      page.getByTestId("today-entity-continuity-recall"),
      "next-day continuity recall slot should be visible",
    ).toBeVisible({ timeout: 25_000 });

    const recallText = await page.getByTestId("today-entity-continuity-recall").textContent();
    expect(recallText).toContain("Вчера главным было");
    expect(recallText).toContain("получилось");
    expect(recallText).toContain(focusText!);
  });
});
