const { chromium, request } = require("playwright");
const fs = require("fs");
const path = require("path");

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000";
const API_URL = process.env.PLAYWRIGHT_API_BASE_URL || "http://localhost:8080";
const OUT_DIR = process.env.AUDIT_OUT_DIR || path.join(__dirname, "..", "e2e-audit-output");

function todayIso(daysOffset = 0) {
  const d = new Date();
  d.setDate(d.getDate() + daysOffset);
  return d.toISOString().split("T")[0];
}

async function apiContext(token) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  return request.newContext({ baseURL: API_URL, extraHTTPHeaders: headers });
}

async function signupAndSetup() {
  const email = `e2e-audit-${Date.now()}@example.com`;
  const password = "E2eAudit9!";
  const api = await apiContext();

  let r = await api.post("/auth/signup", {
    data: { email, password },
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  });
  if (!r.ok()) throw new Error(`signup failed: ${r.status()} ${await r.text()}`);

  r = await api.post("/auth/login", {
    data: { email, password },
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  });
  if (!r.ok()) throw new Error(`login failed: ${r.status()} ${await r.text()}`);
  const { token } = await r.json();

  const setupApi = await apiContext(token);
  const setupPayload = {
    first_name: "Audit",
    gender: "female",
    birth_date: "1990-05-15",
    birth_time: "10:00:00",
    time_unknown: false,
    timezone_offset_minutes: 180,
    timezone_name: "Europe/Moscow",
    location_name: "Moscow, Russia",
    latitude: 55.7558,
    longitude: 37.6173,
    label: "Я",
  };
  r = await setupApi.post("/account/core-setup", {
    data: setupPayload,
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  });
  if (!r.ok()) throw new Error(`core-setup failed: ${r.status()} ${await r.text()}`);
  const setupBody = await r.json();

  r = await setupApi.post("/account/core-profile/refresh", {
    data: {},
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  });
  if (!r.ok()) throw new Error(`core-profile/refresh failed: ${r.status()} ${await r.text()}`);
  const refreshBody = await r.json();

  await api.dispose();
  await setupApi.dispose();

  return { email, password, token, setupBody, refreshBody };
}

async function testApiEndpoints(token) {
  const ctx = await apiContext(token);
  const results = {};
  const targets = [
    "/auth/me",
    `/today/contract?target_date=${todayIso()}&timezone=UTC`,
    `/morning-ritual/today?target_date=${todayIso()}&fast_mode=1`,
    `/today/bundle?target_date=${todayIso()}`,
  ];
  for (const url of targets) {
    const t0 = Date.now();
    const r = await ctx.get(url);
    results[url] = {
      status: r.status(),
      durationMs: Date.now() - t0,
      preview: (await r.text()).slice(0, 300),
    };
  }
  await ctx.dispose();
  return results;
}

async function capturePage(page, name, opts = {}) {
  const screenshotPath = path.join(OUT_DIR, `${name}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });
  const text = await page.evaluate(() => document.body.innerText);
  return {
    name,
    url: page.url(),
    screenshotPath,
    textPreview: text.slice(0, 2000),
  };
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const report = {
    baseUrl: BASE_URL,
    apiUrl: API_URL,
    createdAt: new Date().toISOString(),
    today: todayIso(),
    tomorrow: todayIso(1),
    user: null,
    apiEndpoints: {},
    screens: [],
  };

  const { email, password, token } = await signupAndSetup();
  report.user = { email, profile: { birthDate: "1990-05-15", location: "Moscow, Russia" } };

  // Pre-warm the day story so Today is not stuck in "assembling" shell.
  const warmApi = await apiContext(token);
  const t = todayIso();
  let refreshRes = await warmApi.post("/today/story/refresh", {
    data: { local_date: t, timezone: "Europe/Moscow", force: true },
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  });
  report.storyRefresh = {
    status: refreshRes.status(),
    body: await refreshRes.text().catch(() => ""),
  };
  // Poll for completion if backend returned a job.
  if (refreshRes.ok()) {
    try {
      const refreshBody = JSON.parse(report.storyRefresh.body);
      if (refreshBody.generation_id && refreshBody.story_status !== "ready" && refreshBody.story_status !== "complete") {
        for (let i = 0; i < 12; i++) {
          await new Promise((r) => setTimeout(r, 5000));
          const job = await warmApi.get(`/today/jobs/${refreshBody.generation_id}`);
          const jobBody = await job.text();
          report.storyRefresh[`poll_${i}`] = { status: job.status(), body: jobBody.slice(0, 300) };
          const jobJson = JSON.parse(jobBody);
          if (jobJson.job && (jobJson.job.status === "complete" || jobJson.job.status === "enriched" || jobJson.job.status === "failed")) break;
        }
      }
    } catch (e) {
      report.storyRefresh.parseError = e.message;
    }
  }
  await warmApi.dispose();

  report.apiEndpoints = await testApiEndpoints(token);

  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleErrors = [];
  const networkLog = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push({ text: msg.text(), location: msg.location() });
  });
  page.on("request", (req) => networkLog.push({ type: "request", method: req.method(), url: req.url() }));
  page.on("response", (res) => {
    const req = res.request();
    networkLog.push({ type: "response", method: req.method(), url: req.url(), status: res.status() });
  });
  page.on("requestfailed", (req) => {
    networkLog.push({ type: "failed", method: req.method(), url: req.url(), failure: req.failure()?.errorText || "" });
  });

  // Seed auth state directly in localStorage before any app render.
  await page.goto(BASE_URL);
  await page.evaluate((t) => {
    localStorage.setItem("todayflow_token", t);
    try {
      localStorage.setItem("todayflow_auth_snapshot_v1", JSON.stringify({ token: t, profile: null, savedAt: Date.now() }));
      localStorage.setItem("todayflow_last_session_snapshot_saved_at", String(Date.now()));
    } catch {}
  }, token);

  // Navigate to Today and wait generously for content to load.
  await page.goto(`${BASE_URL}/today`);
  await page.waitForLoadState("networkidle", { timeout: 30000 }).catch(() => {});
  // Wait until either the day content appears or a timeout.
  await page.waitForFunction(
    () => {
      const text = document.body.innerText;
      return !text.includes("День почти готов") || document.body.innerText.length > 200;
    },
    { timeout: 30000 }
  ).catch(() => {});
  await page.waitForTimeout(2000);
  const todayScreen = await capturePage(page, "today");
  todayScreen.consoleErrors = consoleErrors.splice(0, consoleErrors.length);
  todayScreen.networkLog = networkLog.splice(0, networkLog.length);
  report.screens.push(todayScreen);

  // Capture remaining surfaces with the same authenticated context.
  const surfaces = [
    { name: "profile", url: "/profile" },
    { name: "morning_ritual", url: "/morning-ritual" },
    { name: "practices", url: "/practices" },
    { name: "dashboard_daily", url: "/dashboard/daily" },
    { name: "tracking_diary", url: "/tracking/diary" },
  ];
  for (const { name, url } of surfaces) {
    try {
      await page.goto(`${BASE_URL}${url}`);
      await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
      await page.waitForTimeout(2000);
      const screen = await capturePage(page, name);
      screen.consoleErrors = consoleErrors.splice(0, consoleErrors.length);
      screen.networkLog = networkLog.splice(0, networkLog.length);
      report.screens.push(screen);
    } catch (err) {
      report.screens.push({ name, url, error: err.message });
    }
  }

  // Look for My Day and Evening text inside Today.
  try {
    await page.goto(`${BASE_URL}/today`);
    await page.waitForLoadState("networkidle", { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(3000);
    const myDayCount = await page.locator("text=/Мой день/i").count();
    const eveningCount = await page.locator("text=/Вечер/i").count();
    const energyCount = await page.locator("text=/Энергия/i").count();
    report.todayEmbedded = { myDayTextCount: myDayCount, eveningTextCount: eveningCount, energyTextCount: energyCount };
    await page.screenshot({ path: path.join(OUT_DIR, "today_myday_evening.png"), fullPage: true });
  } catch (err) {
    report.todayEmbeddedError = err.message;
  }

  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "report.json"), JSON.stringify(report, null, 2));
  console.log("Report written to", path.join(OUT_DIR, "report.json"));
  console.log("Screens:", report.screens.map((s) => s.name).join(", "));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
