import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson } from "@/lib/api";
import { useUserDay } from "./useUserDay";
import type { 
  AccountProfile, 
  UserSettings,
  LiteReport, 
  WeeklyInsightResponse, 
  AstroProfile, 
  TarotDailyDraw, 
  NumerologyProfile, 
  ZodiacReference,
  HouseReference,
  AspectResponse
} from "@/lib/types";

type Practice = {
  id: string;
  title: string;
  description: string;
  category: string;
  duration_minutes?: number;
  difficulty: string;
  is_free: boolean;
  is_personalized: boolean;
  personalized_reason?: string;
  access_level: string;
  tags: string[];
};

type JournalEntry = {
  id: number;
  type: string;
  content: string;
  created_at: string;
};

type TarotHistory = {
  draws: Array<{
    id: number;
    card_name: string;
    orientation: string;
    drawn_at: string;
  }>;
};

type ChallengeParticipation = {
  id: number;
  challenge_id: string;
  challenge_name?: string;
  started_at: string;
  is_active: boolean;
};

export type InterpretationBundle = {
  bundle_id: string;
  pattern_axis: string;
  day: number;
  pattern: {
    axis_id: string;
    name: string;
    value: number;
    is_positive: boolean;
  };
  practice?: {
    id: string;
    title: string;
    description: string;
    category: string;
    duration_minutes?: number;
    difficulty: string;
    is_free: boolean;
    access_level: string;
    tags: string[];
    personalized_reason?: string;
  };
  interpretation?: {
    facet: string;
    text: string;
    max_sentences: number;
  };
  cta?: {
    after_completion: string;
    target: string;
  };
};

export interface DashboardData {
  profile: AccountProfile | null;
  astroProfiles: AstroProfile[];
  liteReport: LiteReport | null;
  fullReport: any;
  weeklyInsight: WeeklyInsightResponse | null;
  dailyCheckIn: any;
  tarotCard: TarotDailyDraw | null;
  tarotFavorites: number[];
  numerologyProfile: NumerologyProfile | null;
  zodiacReferences: ZodiacReference[];
  houseReferences: HouseReference[];
  aspects: AspectResponse | null;
  dailyPractice: Practice | null;
  journalEntries: JournalEntry[];
  tarotHistory: TarotHistory | null;
  challenges: ChallengeParticipation[];
  interpretationBundle: InterpretationBundle | null;
  expandedPatterns: Set<string>;
}

export function useDashboardData() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  
  const [profileUserId, setProfileUserId] = useState<number | undefined>(undefined);
  const { userDay } = useUserDay(profileUserId);
  
  const [data, setData] = useState<DashboardData>({
    profile: null,
    astroProfiles: [],
    liteReport: null,
    fullReport: null,
    weeklyInsight: null,
    dailyCheckIn: null,
    tarotCard: null,
    tarotFavorites: [],
    numerologyProfile: null,
    zodiacReferences: [],
    houseReferences: [],
    aspects: null,
    dailyPractice: null,
    journalEntries: [],
    tarotHistory: null,
    challenges: [],
    interpretationBundle: null,
    expandedPatterns: new Set(),
  });
  
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;

    if (!isAuthenticated) {
      if (typeof window !== "undefined") {
        window.location.href = "/profile";
      }
      return;
    }

    const loadData = async () => {
      const profileCreated = searchParams?.get("profile_created") === "true";
      const selectedProfileId = searchParams?.get("profile");
      
      if (profileCreated) {
        router.replace("/today", { scroll: false });
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      try {
        // Загружаем основные данные
        const [me, profilesData, accountSettings] = await Promise.allSettled([
          getJson<AccountProfile>("/auth/me"),
          getJson<{profiles: AstroProfile[], max_profiles: number, current_count: number, can_create_more: boolean}>("/account/astro-data"),
          getJson<UserSettings>("/account/profile"),
        ]);

        let profile: AccountProfile | null = null;
        let expandedPatterns = new Set<string>();
        let selectedProfile: AstroProfile | null = null;
        
        if (me.status === "fulfilled") {
          profile = me.value;
          
          // Устанавливаем userId для useUserDay
          setProfileUserId(profile.user_id);
          
          // Загружаем историю работы с паттернами (для персонального следа)
          const patternHistoryKey = `pattern_history_${profile.user_id}`;
          const history = localStorage.getItem(patternHistoryKey);
          if (history) {
            try {
              const parsed = JSON.parse(history);
              if (parsed.workedPatterns && Array.isArray(parsed.workedPatterns)) {
                expandedPatterns = new Set(parsed.workedPatterns);
              }
            } catch (e) {
              // Игнорируем ошибки парсинга
            }
          }
        }
        
        // Определяем выбранный профиль
        if (profilesData.status === "fulfilled" && profile) {
          const profiles = profilesData.value?.profiles || [];
          if (selectedProfileId) {
            selectedProfile = profiles.find(p => p.id === parseInt(selectedProfileId)) || null;
          } else {
            selectedProfile = profiles.find(p => p.is_primary) || profiles[0] || null;
          }
          
          // Если выбран другой профиль, пересоздаем lite report для него
          if (selectedProfile && selectedProfileId) {
            try {
              const reportPayload = {
                date: selectedProfile.birth_date,
                time: selectedProfile.time_unknown ? null : (selectedProfile.birth_time || null),
                location: selectedProfile.location_name || "",
                coordinates: selectedProfile.latitude && selectedProfile.longitude ? {
                  latitude: selectedProfile.latitude,
                  longitude: selectedProfile.longitude
                } : undefined
              };
              // Передаем astro_profile_id через query параметр в URL
              const url = `/reports/lite${selectedProfile.id ? `?astro_profile_id=${selectedProfile.id}` : ""}`;
              await postJson(url, reportPayload).catch(() => {
                // Если не удалось создать, продолжаем с существующим
              });
            } catch (err) {
              console.warn("Failed to regenerate lite report for selected profile:", err);
            }
          }
        }
        
        // Загружаем все данные параллельно (только если пользователь авторизован)
        if (profile) {
          const liteReportUrl = selectedProfileId 
            ? `/reports/lite?astro_profile_id=${selectedProfileId}`
            : "/reports/lite";
          
          const [
            liteReport,
            fullReport,
            weeklyInsight,
            dailyCheckIn,
            tarotCard,
            tarotFavoritesData,
            journals,
            tarotHistory,
            challengeParts,
            zodiacs,
            houses,
            aspectsData
          ] = await Promise.allSettled([
            profile.has_lite_report ? getJson<LiteReport>(liteReportUrl).catch(() => null) : Promise.resolve(null),
            profile.has_full_report ? getJson("/reports/full").catch(() => null) : Promise.resolve(null),
            (profile.has_lite_report || profile.is_paid) ? getJson<WeeklyInsightResponse>("/celestial/weekly-insight").catch(() => null) : Promise.resolve(null),
            profile.is_paid ? getJson("/celestial/check-in").catch(() => null) : Promise.resolve(null),
            getJson<TarotDailyDraw>("/tarot/daily").catch(() => null),
            getJson<{favorites: number[]}>("/tarot/favorites").catch(() => ({favorites: []})),
            getJson<JournalEntry[]>("/journal/entries").catch(() => []),
            getJson<TarotHistory>("/tarot/history").catch(() => null),
            getJson<ChallengeParticipation[]>("/challenges/my/participations").catch(() => []),
            getJson<ZodiacReference[]>("/reference/zodiac").catch(() => []),
            getJson<HouseReference[]>("/reference/houses").catch(() => []),
            profile.has_lite_report ? getJson<AspectResponse>("/aspects/lite").catch(() => null) : Promise.resolve(null)
          ]);

          let astroProfiles: AstroProfile[] = [];
          let numerologyProfile: NumerologyProfile | null = null;

          if (profilesData.status === "fulfilled") {
            astroProfiles = profilesData.value?.profiles || [];
            
            // Загружаем нумерологию для выбранного профиля (или основного).
            // ВАЖНО: full_name берём из account settings, а не из astro profile label.
            const profileForNumerology = selectedProfile || astroProfiles.find(p => p.is_primary) || astroProfiles[0];
            const settings = accountSettings.status === "fulfilled" ? accountSettings.value : null;
            const fullName = [settings?.first_name || "", settings?.last_name || ""].join(" ").trim();
            if (profileForNumerology && fullName) {
              try {
                numerologyProfile = await postJson<NumerologyProfile>("/numerology/name", {
                  full_name: fullName,
                  birth_date: profileForNumerology.birth_date
                }).catch(() => null);
              } catch (err) {
                console.warn("No numerology available", err);
              }
            }
          }

          setData(prev => ({
            ...prev,
            profile,
            astroProfiles,
            liteReport: liteReport.status === "fulfilled" ? liteReport.value : null,
            fullReport: fullReport.status === "fulfilled" ? fullReport.value : null,
            weeklyInsight: weeklyInsight.status === "fulfilled" ? weeklyInsight.value : null,
            dailyCheckIn: dailyCheckIn.status === "fulfilled" ? dailyCheckIn.value : null,
            tarotCard: tarotCard.status === "fulfilled" ? tarotCard.value : null,
            tarotFavorites: tarotFavoritesData.status === "fulfilled" ? (tarotFavoritesData.value?.favorites || []) : [],
            numerologyProfile,
            zodiacReferences: zodiacs.status === "fulfilled" ? (zodiacs.value || []) : [],
            houseReferences: houses.status === "fulfilled" ? (houses.value || []) : [],
            aspects: aspectsData.status === "fulfilled" ? aspectsData.value : null,
            journalEntries: journals.status === "fulfilled" ? (journals.value || []) : [],
            tarotHistory: tarotHistory.status === "fulfilled" ? tarotHistory.value : null,
            challenges: challengeParts.status === "fulfilled" ? (challengeParts.value || []) : [],
            expandedPatterns,
          }));
        } else {
          // Для неавторизованных пользователей загружаем только публичные данные
          const [tarotCard] = await Promise.allSettled([
            getJson<TarotDailyDraw>("/tarot/daily/public").catch(() => null),
          ]);
          
          setData(prev => ({
            ...prev,
            profile: null,
            astroProfiles: [],
            tarotCard: tarotCard.status === "fulfilled" ? tarotCard.value : null,
          }));
        }
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isAuthenticated, authLoading, searchParams, router]);

  // Загружаем Interpretation Bundle после установки userDay
  // ВАЖНО: Эндпоинт /practices/interpretation-bundle может возвращать пустой bundle
  // Запрос выполняется опционально - если эндпоинт не существует или возвращает пустой bundle, просто вернётся null
  useEffect(() => {
    if (!isAuthenticated || !data.profile?.is_paid || !userDay) return;

    const loadBundle = async () => {
      try {
        // Эндпоинт может быть не реализован или возвращать пустой bundle - это нормально, просто игнорируем
        const bundle = await getJson<InterpretationBundle>(`/practices/interpretation-bundle?day=${userDay}`).catch(() => null);
        // Проверяем, что bundle не пустой
        if (!bundle || !bundle.practice) {
          return;
        }
        if (bundle) {
          setData(prev => ({
            ...prev,
            interpretationBundle: bundle,
            dailyPractice: bundle.practice ? {
              id: bundle.practice.id,
              title: bundle.practice.title,
              description: bundle.practice.description,
              category: bundle.practice.category,
              duration_minutes: bundle.practice.duration_minutes,
              difficulty: bundle.practice.difficulty,
              is_free: bundle.practice.is_free || false,
              is_personalized: true,
              personalized_reason: bundle.practice.personalized_reason || bundle.interpretation?.text,
              access_level: bundle.practice.access_level || "lite",
              tags: bundle.practice.tags || [],
            } : prev.dailyPractice,
          }));
        } else if (!data.dailyPractice) {
          // Fallback: загружаем текущую практику только если еще не загружена
          getJson<Practice>("/practices/current")
            .then(practice => {
              if (practice) {
                setData(prev => ({
                  ...prev,
                  dailyPractice: practice,
                }));
              }
            })
            .catch(() => {
              // Игнорируем ошибки
            });
        }
      } catch (err) {
        console.warn("No interpretation bundle available, falling back to current practice", err);
        if (!data.dailyPractice) {
          getJson<Practice>("/practices/current")
            .then(practice => {
              if (practice) {
                setData(prev => ({
                  ...prev,
                  dailyPractice: practice,
                }));
              }
            })
            .catch(() => {
              // Игнорируем ошибки
            });
        }
      }
    };

    loadBundle();
  }, [isAuthenticated, data.profile?.is_paid, userDay, data.dailyPractice]);

  const updateExpandedPatterns = (patternId: string) => {
    setData(prev => {
      const newExpanded = new Set(prev.expandedPatterns);
      if (newExpanded.has(patternId)) {
        newExpanded.delete(patternId);
      } else {
        newExpanded.add(patternId);
        
        // Сохраняем в историю
        if (prev.profile) {
          const patternHistoryKey = `pattern_history_${prev.profile.user_id}`;
          const history = localStorage.getItem(patternHistoryKey);
          let parsed: { workedPatterns: string[] } = { workedPatterns: [] };
          if (history) {
            try {
              const parsedHistory = JSON.parse(history);
              if (parsedHistory && Array.isArray(parsedHistory.workedPatterns)) {
                parsed = parsedHistory;
              }
            } catch (e) {
              // Игнорируем ошибки парсинга
            }
          }
          parsed.workedPatterns = Array.from(newExpanded);
          localStorage.setItem(patternHistoryKey, JSON.stringify(parsed));
        }
      }
      return { ...prev, expandedPatterns: newExpanded };
    });
  };

  return { data, loading, updateExpandedPatterns, userDay };
}
