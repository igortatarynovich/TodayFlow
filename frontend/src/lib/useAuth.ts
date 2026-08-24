import { useState, useEffect, useCallback } from "react";
import { ApiError, getJson, getStoredAccessToken, isRequestAborted } from "./api";
import { clearCoreProfileCache } from "./coreProfileCacheStorage";
import type { AccountProfile } from "./types";

const AUTH_CACHE_TTL_MS = 30_000;
const AUTH_TOKEN_KEY = "todayflow_token";
const AUTH_SNAPSHOT_KEY = "todayflow_auth_snapshot_v1";
const AUTH_LAST_VALIDATED_AT_KEY = "todayflow_last_auth_validated_at";
const AUTH_LAST_SNAPSHOT_SAVED_AT_KEY = "todayflow_last_session_snapshot_saved_at";

type AuthSnapshot = {
  isAuthenticated: boolean;
  profile: AccountProfile | null;
};

type StoredAuthSnapshot = {
  token: string;
  profile: AccountProfile | null;
  savedAt: number;
};

type AuthStatus = {
  networkDegraded: boolean;
  warningMessage: string | null;
  lastValidatedAt: number | null;
  lastSnapshotSavedAt: number | null;
};

let authCache: {
  token: string | null;
  expiresAt: number;
  snapshot: AuthSnapshot | null;
  inFlight: Promise<AuthSnapshot> | null;
} = {
  token: null,
  expiresAt: 0,
  snapshot: null,
  inFlight: null,
};

function clearAuthCache() {
  authCache = {
    token: null,
    expiresAt: 0,
    snapshot: null,
    inFlight: null,
  };
}

function clearAuthStorageArtifacts() {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(AUTH_SNAPSHOT_KEY);
    localStorage.removeItem(AUTH_LAST_VALIDATED_AT_KEY);
    localStorage.removeItem(AUTH_LAST_SNAPSHOT_SAVED_AT_KEY);
  } catch {
    /* private mode */
  }
}

function readTimestamp(key: string): number | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const value = Number(raw);
    return Number.isFinite(value) && value > 0 ? value : null;
  } catch {
    return null;
  }
}

function persistValidatedAt(timestamp: number) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(AUTH_LAST_VALIDATED_AT_KEY, String(timestamp));
  } catch {
    /* private mode */
  }
}

function persistSnapshot(token: string, profile: AccountProfile | null, savedAt: number) {
  if (typeof window === "undefined") return;
  try {
    const payload: StoredAuthSnapshot = { token, profile, savedAt };
    localStorage.setItem(AUTH_SNAPSHOT_KEY, JSON.stringify(payload));
    localStorage.setItem(AUTH_LAST_SNAPSHOT_SAVED_AT_KEY, String(savedAt));
  } catch {
    /* private mode */
  }
}

function loadStoredSnapshot(token: string): StoredAuthSnapshot | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(AUTH_SNAPSHOT_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StoredAuthSnapshot;
    if (!parsed || typeof parsed !== "object") return null;
    if (parsed.token !== token) return null;
    if (typeof parsed.savedAt !== "number" || !Number.isFinite(parsed.savedAt) || parsed.savedAt <= 0) return null;
    return parsed;
  } catch {
    return null;
  }
}

async function resolveAuthSnapshot(token: string): Promise<AuthSnapshot> {
  const now = Date.now();
  const hasFreshCache =
    authCache.snapshot &&
    authCache.token === token &&
    authCache.expiresAt > now;

  if (hasFreshCache) {
    return authCache.snapshot as AuthSnapshot;
  }

  if (authCache.inFlight && authCache.token === token) {
    return authCache.inFlight;
  }

  authCache.token = token;
  authCache.inFlight = getJson<AccountProfile>("/auth/me")
    .then((profile) => {
      const snapshot: AuthSnapshot = { isAuthenticated: true, profile };
      authCache.snapshot = snapshot;
      authCache.expiresAt = Date.now() + AUTH_CACHE_TTL_MS;
      const validatedAt = Date.now();
      persistValidatedAt(validatedAt);
      persistSnapshot(token, profile, validatedAt);
      return snapshot;
    })
    .catch((error) => {
      if (error instanceof ApiError && error.status === 401) {
        if (typeof window !== "undefined") {
          try {
            localStorage.removeItem(AUTH_TOKEN_KEY);
          } catch {
            /* private mode */
          }
        }
        clearAuthStorageArtifacts();
        const snapshot: AuthSnapshot = { isAuthenticated: false, profile: null };
        authCache.snapshot = snapshot;
        authCache.expiresAt = Date.now() + 2_000;
        return snapshot;
      }

      if (authCache.snapshot && authCache.token === token) {
        return authCache.snapshot;
      }

      throw error;
    })
    .finally(() => {
      authCache.inFlight = null;
    });

  return authCache.inFlight;
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [status, setStatus] = useState<AuthStatus>({
    networkDegraded: false,
    warningMessage: null,
    lastValidatedAt: null,
    lastSnapshotSavedAt: null,
  });

  const checkAuth = useCallback(async () => {
    try {
      const token = getStoredAccessToken();

      if (!token) {
        clearAuthCache();
        clearAuthStorageArtifacts();
        clearCoreProfileCache();
        setIsAuthenticated(false);
        setProfile(null);
        setStatus({
          networkDegraded: false,
          warningMessage: null,
          lastValidatedAt: null,
          lastSnapshotSavedAt: null,
        });
        return;
      }

      try {
        const snapshot = await resolveAuthSnapshot(token);
        setIsAuthenticated(snapshot.isAuthenticated);
        setProfile(snapshot.profile);
        setStatus({
          networkDegraded: false,
          warningMessage: null,
          lastValidatedAt: readTimestamp(AUTH_LAST_VALIDATED_AT_KEY),
          lastSnapshotSavedAt: readTimestamp(AUTH_LAST_SNAPSHOT_SAVED_AT_KEY),
        });
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          setIsAuthenticated(false);
          setProfile(null);
          setStatus({
            networkDegraded: false,
            warningMessage: null,
            lastValidatedAt: null,
            lastSnapshotSavedAt: null,
          });
          return;
        }
        const fallback = loadStoredSnapshot(token);
        if (fallback) {
          setIsAuthenticated(true);
          setProfile(fallback.profile);
          setStatus({
            networkDegraded: true,
            warningMessage:
              "Сеть нестабильна: работаем с сохраненной сессией и локальными данными.",
            lastValidatedAt: readTimestamp(AUTH_LAST_VALIDATED_AT_KEY),
            lastSnapshotSavedAt: fallback.savedAt,
          });
        } else {
          // Token is still present — do not dump the user back to guest on a hung probe.
          setIsAuthenticated(true);
          setStatus({
            networkDegraded: true,
            warningMessage:
              "Сеть нестабильна: не удалось подтвердить сессию, попробуй обновить позже.",
            lastValidatedAt: readTimestamp(AUTH_LAST_VALIDATED_AT_KEY),
            lastSnapshotSavedAt: readTimestamp(AUTH_LAST_SNAPSHOT_SAVED_AT_KEY),
          });
        }
        if (!isRequestAborted(error)) {
          console.error("Failed to resolve auth snapshot", error);
        }
      }
    } catch (error) {
      if (!isRequestAborted(error)) {
        console.error("Failed to resolve auth snapshot", error);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Optimistic paint from last validated snapshot so page navigations are not
    // blocked on /auth/me (many screens gate on authLoading).
    const token = getStoredAccessToken();
    if (token) {
      const stored = loadStoredSnapshot(token);
      if (stored) {
        setIsAuthenticated(true);
        setProfile(stored.profile);
        setStatus({
          networkDegraded: false,
          warningMessage: null,
          lastValidatedAt: readTimestamp(AUTH_LAST_VALIDATED_AT_KEY),
          lastSnapshotSavedAt: stored.savedAt,
        });
        setIsLoading(false);
      }
    }

    checkAuth();

    // Слушаем изменения localStorage для синхронизации между вкладками
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "todayflow_token") {
        checkAuth();
      }
    };

    // Слушаем кастомное событие для обновления в той же вкладке
    const handleAuthChange = () => {
      clearAuthCache();
      checkAuth();
    };

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("auth:update", handleAuthChange);
    
    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("auth:update", handleAuthChange);
    };
  }, [checkAuth]);

  // Функция для принудительного обновления состояния
  const refresh = useCallback(() => {
    checkAuth();
  }, [checkAuth]);

  return {
    isAuthenticated,
    isLoading,
    profile,
    refresh,
    networkDegraded: status.networkDegraded,
    warningMessage: status.warningMessage,
    lastValidatedAt: status.lastValidatedAt,
    lastSnapshotSavedAt: status.lastSnapshotSavedAt,
  };
}
