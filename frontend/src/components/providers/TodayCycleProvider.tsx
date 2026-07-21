"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { getJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import {
  assembleTodayCycleFromProgressive,
  normalizeTodayPayload,
  type TodayCycleData,
} from "@/components/today/todayPageUtils";

export type TodayCycleContextValue = {
  cycle: TodayCycleData | null;
  loading: boolean;
  /** Полный `/today` ещё догружается после первого слоя (`/today/opening` + `/today/bundle`, паритет с iOS). */
  todayHeavyLayersPending: boolean;
  error: string | null;
  /** Обновить кэш после локальных правок полного цикла (без сети). */
  setCycle: (data: TodayCycleData) => void;
  /**
   * Загрузить день: параллельно `GET /today/opening` + `GET /today/bundle`, затем полный `GET /today` в фоне.
   * Промис резолвится после первого успешного слоя (как на iOS); тяжёлые поля подтягиваются асинхронно.
   */
  refetchToday: (options?: { force?: boolean }) => Promise<TodayCycleData | null>;
};

const TodayCycleContext = createContext<TodayCycleContextValue | null>(null);

export function TodayCycleProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated, profile } = useAuth();
  const userId = profile?.user_id ?? null;
  const [cycle, setCycleState] = useState<TodayCycleData | null>(null);
  const [loading, setLoading] = useState(false);
  const [todayHeavyLayersPending, setTodayHeavyLayersPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inFlightRef = useRef<Promise<TodayCycleData | null> | null>(null);
  const fullFetchGenerationRef = useRef(0);
  const activeUserIdRef = useRef<number | null>(null);

  const setCycle = useCallback((data: TodayCycleData) => {
    setCycleState(normalizeTodayPayload(data));
    setError(null);
    setTodayHeavyLayersPending(false);
  }, []);

  const refetchToday = useCallback(
    async (options?: { force?: boolean }): Promise<TodayCycleData | null> => {
      if (!isAuthenticated) {
        setCycleState(null);
        setError(null);
        setTodayHeavyLayersPending(false);
        inFlightRef.current = null;
        return null;
      }

      if (!options?.force && inFlightRef.current) {
        return inFlightRef.current;
      }

      const run = (async (): Promise<TodayCycleData | null> => {
        const fetchGeneration = ++fullFetchGenerationRef.current;
        const fetchUserId = userId;
        try {
          setLoading(true);
          setError(null);
          setTodayHeavyLayersPending(false);

          let firstPaint: TodayCycleData | null = null;
          try {
            const [openingRaw, bundleRaw] = await Promise.all([
              getJson<Record<string, unknown>>("/today/opening"),
              getJson<Record<string, unknown>>("/today/bundle"),
            ]);
            firstPaint = assembleTodayCycleFromProgressive(openingRaw, bundleRaw);
            if (firstPaint) {
              if (fetchGeneration === fullFetchGenerationRef.current && activeUserIdRef.current === fetchUserId) {
                setCycleState(firstPaint);
              }
            } else {
              firstPaint = null;
            }
          } catch {
            firstPaint = null;
          }

          if (!firstPaint) {
            const raw = await getJson<TodayCycleData>("/today");
            const data = normalizeTodayPayload(raw);
            if (fetchGeneration === fullFetchGenerationRef.current && activeUserIdRef.current === fetchUserId) {
              setCycleState(data);
              setError(null);
              setTodayHeavyLayersPending(false);
            }
            return data;
          }

          setLoading(false);
          setTodayHeavyLayersPending(true);

          void getJson<TodayCycleData>("/today")
            .then((fullRaw) => {
              if (fetchGeneration !== fullFetchGenerationRef.current) return;
              if (activeUserIdRef.current !== fetchUserId) return;
              setCycleState(normalizeTodayPayload(fullRaw));
              setError(null);
              setTodayHeavyLayersPending(false);
            })
            .catch((e) => {
              if (fetchGeneration !== fullFetchGenerationRef.current) return;
              if (activeUserIdRef.current !== fetchUserId) return;
              const msg = e instanceof Error ? e.message : "today_full_load_failed";
              setError(msg);
              setTodayHeavyLayersPending(false);
            });

          return firstPaint;
        } catch (e) {
          const msg = e instanceof Error ? e.message : "today_load_failed";
          setError(msg);
          return null;
        } finally {
          setLoading(false);
        }
      })();

      if (!options?.force) {
        inFlightRef.current = run;
      }
      run.finally(() => {
        if (inFlightRef.current === run) {
          inFlightRef.current = null;
        }
      });

      return run;
    },
    [isAuthenticated, userId],
  );

  useEffect(() => {
    if (!isAuthenticated) {
      activeUserIdRef.current = null;
      setCycleState(null);
      setError(null);
      setTodayHeavyLayersPending(false);
      inFlightRef.current = null;
      fullFetchGenerationRef.current += 1;
      return;
    }
    if (activeUserIdRef.current !== userId) {
      activeUserIdRef.current = userId;
      setCycleState(null);
      setError(null);
      setTodayHeavyLayersPending(false);
      inFlightRef.current = null;
      fullFetchGenerationRef.current += 1;
    }
    void refetchToday({ force: true });
  }, [isAuthenticated, userId, refetchToday]);

  /** После полуночи кэш по вчерашней дате: обновляем при возврате на вкладку / из bfcache. */
  useEffect(() => {
    if (!isAuthenticated) return;

    const maybeRefreshForNewDay = () => {
      if (typeof document !== "undefined" && document.visibilityState !== "visible") return;
      const todayIso = new Date().toISOString().split("T")[0];
      if (cycle?.date && cycle.date !== todayIso) {
        void refetchToday({ force: true });
      }
    };

    document.addEventListener("visibilitychange", maybeRefreshForNewDay);
    window.addEventListener("pageshow", maybeRefreshForNewDay);
    return () => {
      document.removeEventListener("visibilitychange", maybeRefreshForNewDay);
      window.removeEventListener("pageshow", maybeRefreshForNewDay);
    };
  }, [isAuthenticated, cycle?.date, refetchToday]);

  const value = useMemo<TodayCycleContextValue>(
    () => ({
      cycle,
      loading,
      todayHeavyLayersPending,
      error,
      setCycle,
      refetchToday,
    }),
    [cycle, loading, todayHeavyLayersPending, error, setCycle, refetchToday],
  );

  return <TodayCycleContext.Provider value={value}>{children}</TodayCycleContext.Provider>;
}

export function useTodayCycle(): TodayCycleContextValue {
  const ctx = useContext(TodayCycleContext);
  if (!ctx) {
    throw new Error("useTodayCycle must be used within TodayCycleProvider");
  }
  return ctx;
}
