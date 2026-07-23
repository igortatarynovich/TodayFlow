import { getLocale } from "@/lib/i18n";
import {
  AUTH_TOKEN_KEY,
  getAccessToken,
  getRefreshToken,
  setTokenPair,
} from "@/lib/authSessionStorage";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";
const AUTH_ME_CACHE_TTL_MS = 30_000;

type AuthMeCacheEntry = {
  key: string;
  expiresAt: number;
  data: unknown;
  inFlight: Promise<unknown> | null;
};

let authMeCache: AuthMeCacheEntry | null = null;
let refreshInFlight: Promise<boolean> | null = null;

export function clearAuthMeCache(): void {
  authMeCache = null;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public path: string,
    public details?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Читает JWT из localStorage, подчищает пробелы и при необходимости перезаписывает хранилище. */
export function getStoredAccessToken(): string | null {
  return getAccessToken();
}

async function tryRefreshAccessToken(): Promise<boolean> {
  if (typeof window === "undefined") return false;
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    const refresh = getRefreshToken();
    if (!refresh) return false;
    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept-Language": getLocale(),
        },
        body: JSON.stringify({ refresh_token: refresh }),
        credentials: "include",
      });
      if (!res.ok) return false;
      const data = (await res.json()) as {
        access_token?: string;
        refresh_token?: string;
        token?: string;
      };
      const access = (data.access_token || data.token || "").trim();
      const nextRefresh = (data.refresh_token || "").trim();
      if (!access) return false;
      setTokenPair(access, nextRefresh || refresh);
      clearAuthMeCache();
      return true;
    } catch {
      return false;
    } finally {
      refreshInFlight = null;
    }
  })();

  return refreshInFlight;
}

async function forceLogoutOnAuthFailure(): Promise<void> {
  if (typeof window === "undefined") return;
  const { clearAuthSession, notifyAuthSessionChanged } = await import("@/lib/authSession");
  clearAuthSession();
  notifyAuthSessionChanged();
}

async function request<T>(path: string, options?: RequestInit, allowRefresh = true): Promise<T> {
  const headers = new Headers(options?.headers || {});
  headers.set("Content-Type", "application/json");
  headers.set("Accept-Language", getLocale());
  Object.entries(authHeader()).forEach(([key, value]) => headers.set(key, value));

  const method = (options?.method || "GET").toUpperCase();
  if (path === "/auth/me" && method === "GET") {
    const authKey = `${headers.get("Authorization") || ""}|${headers.get("Accept-Language") || ""}`;
    const now = Date.now();
    if (authMeCache && authMeCache.key === authKey && authMeCache.expiresAt > now && authMeCache.data) {
      return authMeCache.data as T;
    }
    if (authMeCache && authMeCache.key === authKey && authMeCache.inFlight) {
      return authMeCache.inFlight as Promise<T>;
    }
    const inFlight = performRequest<T>(path, options, headers, allowRefresh)
      .then((data) => {
        authMeCache = {
          key: authKey,
          expiresAt: Date.now() + AUTH_ME_CACHE_TTL_MS,
          data,
          inFlight: null,
        };
        return data;
      })
      .catch((error) => {
        authMeCache = null;
        throw error;
      });
    authMeCache = {
      key: authKey,
      expiresAt: now + AUTH_ME_CACHE_TTL_MS,
      data: null,
      inFlight,
    };
    return inFlight;
  }

  return performRequest<T>(path, options, headers, allowRefresh);
}

async function performRequest<T>(
  path: string,
  options: RequestInit | undefined,
  headers: Headers,
  allowRefresh: boolean,
): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      credentials: "include",
    });

    if (!res.ok) {
      let message = `Request failed with status ${res.status}`;
      let details: unknown = undefined;

      try {
        const contentType = res.headers.get("content-type");
        if (contentType?.includes("application/json")) {
          details = await res.json();
          if (details && typeof details === "object" && "detail" in details) {
            const detail = (details as { detail?: unknown }).detail;
            if (typeof detail === "string") {
              message = detail || message;
            } else if (detail && typeof detail === "object" && "message" in detail) {
              message = String((detail as { message?: unknown }).message || message);
            } else {
              message = String(detail || message);
            }
          } else if (details && typeof details === "object" && "message" in details) {
            message = String((details as { message?: unknown }).message || message);
          }
        } else {
          const text = await res.text();
          if (text) {
            message = text;
          }
        }
      } catch {
        // If parsing fails, use default message
      }

      if (res.status === 401) {
        const isRefreshPath = path === "/auth/refresh" || path === "/auth/logout";
        if (allowRefresh && !isRefreshPath && getRefreshToken()) {
          const refreshed = await tryRefreshAccessToken();
          if (refreshed) {
            const retryHeaders = new Headers(options?.headers || {});
            retryHeaders.set("Content-Type", "application/json");
            retryHeaders.set("Accept-Language", getLocale());
            Object.entries(authHeader()).forEach(([key, value]) => retryHeaders.set(key, value));
            return performRequest<T>(path, options, retryHeaders, false);
          }
        }
        await forceLogoutOnAuthFailure();
        throw new ApiError("Unauthorized. Please log in again.", res.status, path, details);
      }

      if (res.status === 403) {
        throw new ApiError(message, res.status, path, details);
      }

      if (res.status === 404) {
        throw new ApiError("Resource not found.", res.status, path, details);
      }

      if (res.status >= 500) {
        throw new ApiError("Server error. Please try again later.", res.status, path, details);
      }

      throw new ApiError(message, res.status, path, details);
    }

    return res.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new ApiError("Network error. Please check your connection.", 0, path);
    }

    throw error;
  }
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function putJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "PUT",
    body: JSON.stringify(body)
  });
}

export async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  return request<T>(path, {
    method: "GET",
    ...init,
  });
}

export async function deleteJson(path: string): Promise<void> {
  await request(path, {
    method: "DELETE"
  });
}

export async function getBinary(path: string): Promise<Blob> {
  const headers = new Headers();
  headers.set("Accept-Language", getLocale());
  Object.entries(authHeader()).forEach(([key, value]) => headers.set(key, value));

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "GET",
      headers,
      credentials: "include",
    });

    if (!res.ok) {
      if (res.status === 401 && getRefreshToken()) {
        const refreshed = await tryRefreshAccessToken();
        if (refreshed) {
          const retryHeaders = new Headers();
          retryHeaders.set("Accept-Language", getLocale());
          Object.entries(authHeader()).forEach(([key, value]) => retryHeaders.set(key, value));
          const retry = await fetch(`${API_BASE}${path}`, {
            method: "GET",
            headers: retryHeaders,
            credentials: "include",
          });
          if (retry.ok) return retry.blob();
        }
      }
      if (res.status === 401) {
        await forceLogoutOnAuthFailure();
      }
      let message = `Request failed with status ${res.status}`;
      try {
        const text = await res.text();
        if (text) {
          message = text;
        }
      } catch {
        // Ignore parsing errors
      }
      throw new ApiError(message, res.status, path);
    }

    return res.blob();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new ApiError("Network error. Please check your connection.", 0, path);
    }
    throw error;
  }
}

function authHeader(): Record<string, string> {
  const token = getStoredAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Re-export for tests that poke storage key directly
export { AUTH_TOKEN_KEY };
