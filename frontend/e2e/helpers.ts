import type { APIRequestContext } from "@playwright/test";

/** Браузер ходит на этот origin (см. ``NEXT_PUBLIC_API_BASE_URL`` при ``next build``). */
export const PLAYWRIGHT_API_BASE = (
  process.env.PLAYWRIGHT_API_BASE_URL ?? "http://127.0.0.1:8080"
).replace(/\/$/, "");

export const E2E_USER_EMAIL =
  process.env.E2E_USER_EMAIL ?? "e2e-playwright@example.com";

export const E2E_USER_PASSWORD =
  process.env.E2E_USER_PASSWORD ?? "E2ePlaywright9!";

/**
 * Создаёт тестового пользователя, если его ещё нет (идемпотентно для повторных прогонов).
 */
export async function ensureE2eUser(request: APIRequestContext): Promise<void> {
  const res = await request.post(`${PLAYWRIGHT_API_BASE}/auth/signup`, {
    data: { email: E2E_USER_EMAIL, password: E2E_USER_PASSWORD },
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  });
  if (res.ok()) {
    return;
  }
  const text = await res.text();
  // 400: «уже есть» или другая валидация — для E2E достаточно попробовать логин в UI
  if (res.status() === 400) {
    return;
  }
  throw new Error(`E2E signup failed: ${res.status()} ${text}`);
}
