import { getLocale } from "@/lib/i18n";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";
const AUTH_ME_CACHE_TTL_MS = 30_000;

type AuthMeCacheEntry = {
  key: string;
  expiresAt: number;
  data: unknown;
  inFlight: Promise<unknown> | null;
};

let authMeCache: AuthMeCacheEntry | null = null;

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

async function request<T>(path: string, options?: RequestInit): Promise<T> {
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
    const inFlight = performRequest<T>(path, options, headers)
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

  return performRequest<T>(path, options, headers);
}

/** Читает JWT из localStorage, подчищает пробелы и при необходимости перезаписывает хранилище. */
export function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("todayflow_token");
  if (raw == null) return null;
  const trimmed = raw.trim();
  if (!trimmed) {
    localStorage.removeItem("todayflow_token");
    return null;
  }
  if (trimmed !== raw) {
    localStorage.setItem("todayflow_token", trimmed);
  }
  return trimmed;
}

async function performRequest<T>(path: string, options: RequestInit | undefined, headers: Headers): Promise<T> {

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
            message = String(details.detail || message);
          } else if (details && typeof details === "object" && "message" in details) {
            message = String(details.message || message);
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

      // Handle specific error cases
      if (res.status === 401) {
        // Unauthorized - clear token and let components redirect to login.
        if (typeof window !== "undefined") {
          const { clearAuthSession, notifyAuthSessionChanged } = await import("@/lib/authSession");
          clearAuthSession();
          notifyAuthSessionChanged();
        }
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
    // Re-throw ApiError as-is
    if (error instanceof ApiError) {
      throw error;
    }

    // Handle network errors
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new ApiError("Network error. Please check your connection.", 0, path);
    }

    // Re-throw other errors
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

export async function getJson<T>(path: string): Promise<T> {
  return request<T>(path, {
    method: "GET"
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
