import {
  AUTH_SNAPSHOT_KEY,
  AUTH_TOKEN_KEY,
  clearAuthenticatedUserCaches,
} from "@/lib/authSessionStorage";
import { beginAuthSession, clearAuthSession } from "@/lib/authSession";

describe("auth session storage", () => {
  beforeEach(() => {
    window.localStorage.clear();
    window.sessionStorage.clear();
  });

  it("clears user-scoped caches but keeps locale", () => {
    window.localStorage.setItem("todayflow_locale_v2", "ru");
    window.localStorage.setItem("todayflow_token", "old");
    window.localStorage.setItem("todayflow_meaning_rings_cache_v1", "{}");
    window.localStorage.setItem("todayflow.day_engagement.v1.2026-07-03", "{}");
    window.sessionStorage.setItem("todayflow_core_profile:v1:default", "{}");
    window.sessionStorage.setItem("todayflow.compact_user_model.v0.2026-07-03", "{}");

    clearAuthenticatedUserCaches();

    expect(window.localStorage.getItem("todayflow_locale_v2")).toBe("ru");
    expect(window.localStorage.getItem("todayflow_meaning_rings_cache_v1")).toBeNull();
    expect(window.localStorage.getItem("todayflow.day_engagement.v1.2026-07-03")).toBeNull();
    expect(window.sessionStorage.getItem("todayflow_core_profile:v1:default")).toBeNull();
    expect(window.sessionStorage.getItem("todayflow.compact_user_model.v0.2026-07-03")).toBeNull();
  });

  it("beginAuthSession replaces token and clears snapshot", () => {
    window.localStorage.setItem(AUTH_TOKEN_KEY, "old-token");
    window.localStorage.setItem(AUTH_SNAPSHOT_KEY, "{}");
    window.sessionStorage.setItem("todayflow_core_profile:v1:default", "{}");

    beginAuthSession({ access_token: "  new-token  ", refresh_token: "refresh-1" });

    expect(window.localStorage.getItem(AUTH_TOKEN_KEY)).toBe("new-token");
    expect(window.localStorage.getItem("todayflow_refresh_token")).toBe("refresh-1");
    expect(window.localStorage.getItem(AUTH_SNAPSHOT_KEY)).toBeNull();
    expect(window.sessionStorage.getItem("todayflow_core_profile:v1:default")).toBeNull();
  });

  it("clearAuthSession removes credentials including refresh", () => {
    window.localStorage.setItem(AUTH_TOKEN_KEY, "token");
    window.localStorage.setItem("todayflow_refresh_token", "refresh");
    window.localStorage.setItem(AUTH_SNAPSHOT_KEY, "{}");
    clearAuthSession();
    expect(window.localStorage.getItem(AUTH_TOKEN_KEY)).toBeNull();
    expect(window.localStorage.getItem("todayflow_refresh_token")).toBeNull();
    expect(window.localStorage.getItem(AUTH_SNAPSHOT_KEY)).toBeNull();
  });
});
