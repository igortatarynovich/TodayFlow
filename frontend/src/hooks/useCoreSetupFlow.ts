"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { getJson, postJson } from "@/lib/api";
import { publishCoreProfileUpdate } from "@/lib/coreProfileCacheStorage";
import {
  clearNatalPreviewCache,
  readNatalPreviewFromCache,
  writeNatalPreviewToCache,
} from "@/lib/natalChartPreviewCache";
import { logActiveJTBDAction } from "@/lib/jtbdFeedback";
import type { AstroProfile, CoreProfile, UserSettings } from "@/lib/types";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import {
  CORE_SETUP_BUILD_COPY,
  createEmptyCoreSetupForm,
  mergeCoreSetupFormFromAccount,
  type CoreSetupBuildStage,
  type CoreSetupPayload,
  type CoreSetupResponse,
} from "@/lib/coreSetup";

type AstroProfilesResponse = {
  profiles: AstroProfile[];
};

type UseCoreSetupFlowOptions = {
  /** Onboarding completes after API; profile hub also warms natal preview. */
  warmNatalPreview?: boolean;
  onCoreProfileUpdated?: (profile: CoreProfile) => void;
  onAstroProfilesUpdated?: (profiles: AstroProfile[]) => void;
};

const STRUCTURE_QUERY = "/natal-chart/?include_interpretations=false&include_editorial=false";
/** Routine enrich: houses/aspects text without LLM editorial. */
const ENRICH_QUERY = "/natal-chart/?include_interpretations=true&include_editorial=false";
/** First build after birth data save — editorial once. */
const SETUP_QUERY = "/natal-chart/?include_interpretations=true&include_editorial=true";

export function useCoreSetupFlow(options: UseCoreSetupFlowOptions = {}) {
  const { warmNatalPreview = false, onCoreProfileUpdated, onAstroProfilesUpdated } = options;

  const [buildStage, setBuildStage] = useState<CoreSetupBuildStage>("idle");
  const [setupError, setSetupError] = useState<string | null>(null);
  const [setupMessage, setSetupMessage] = useState<string | null>(null);
  const [natalPreview, setNatalPreview] = useState<NatalChartPreview | null>(null);
  const [natalPreviewLoading, setNatalPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [setupForm, setSetupForm] = useState<CoreSetupPayload>(() => createEmptyCoreSetupForm());
  const loadGenRef = useRef(0);

  const applyPreview = useCallback((chart: NatalChartPreview) => {
    setNatalPreview(chart);
    writeNatalPreviewToCache(chart, (chart as { astro_profile_id?: number }).astro_profile_id ?? null);
  }, []);

  const loadNatalPreview = useCallback(
    async (opts?: { force?: boolean; withEditorial?: boolean }) => {
      const gen = ++loadGenRef.current;
      setPreviewError(null);

      if (!opts?.force) {
        const cached = readNatalPreviewFromCache(null);
        if (cached) {
          setNatalPreview(cached);
          setNatalPreviewLoading(false);
          // Soft revalidate structure in background (no LLM editorial).
          void getJson<NatalChartPreview>(STRUCTURE_QUERY)
            .then((chart) => {
              if (gen !== loadGenRef.current) return;
              applyPreview({ ...cached, ...chart, interpretations: cached.interpretations ?? chart.interpretations });
            })
            .catch(() => {
              /* keep cache */
            });
          return;
        }
      }

      setNatalPreviewLoading(true);
      try {
        // Phase 1: structure only — wheel + signature without waiting for LLM.
        const structure = await getJson<NatalChartPreview>(STRUCTURE_QUERY);
        if (gen !== loadGenRef.current) return;
        applyPreview(structure);
        setNatalPreviewLoading(false);

        // Phase 2: interpretations. Editorial only on first setup / explicit request.
        const enrichUrl = opts?.withEditorial ? SETUP_QUERY : ENRICH_QUERY;
        const full = await getJson<NatalChartPreview>(enrichUrl);
        if (gen !== loadGenRef.current) return;
        applyPreview(full);
      } catch (err) {
        if (gen !== loadGenRef.current) return;
        setPreviewError(err instanceof Error ? err.message : "Не удалось построить натальную карту.");
        const cached = readNatalPreviewFromCache(null);
        if (cached) {
          setNatalPreview(cached);
        } else if (opts?.force) {
          setNatalPreview(null);
        }
        setNatalPreviewLoading(false);
      }
    },
    [applyPreview],
  );

  const reloadNatalPreview = useCallback(() => {
    void loadNatalPreview({ force: true, withEditorial: false });
  }, [loadNatalPreview]);

  useEffect(() => {
    const cached = readNatalPreviewFromCache(null);
    if (cached) setNatalPreview(cached);
  }, []);

  const hydrateSetupForm = useCallback(
    (profile: UserSettings | null, core: CoreProfile | null) => {
      setSetupForm((prev) => {
        const next = mergeCoreSetupFormFromAccount(prev, profile, core);
        // Re-resolve coords when place is known but lat/lng were wiped on hydrate.
        const place = (next.location_name || "").trim();
        if (
          place.length >= 2 &&
          (typeof next.latitude !== "number" || typeof next.longitude !== "number")
        ) {
          // Only auto-fill coords when suggest has a single unambiguous hit —
          // never silent first-of-many (same class as TZ civil-as-UT bug).
          void getJson<
            Array<{ latitude?: number; longitude?: number; display_name?: string; country?: string }>
          >(`/astro/geocode/suggest?q=${encodeURIComponent(place)}&limit=6`)
            .then((hits) => {
              if (!Array.isArray(hits) || hits.length !== 1) return;
              const hit = hits[0];
              if (typeof hit?.latitude !== "number" || typeof hit?.longitude !== "number") return;
              setSetupForm((current) => {
                if ((current.location_name || "").trim().toLowerCase() !== place.toLowerCase()) {
                  return current;
                }
                return {
                  ...current,
                  latitude: hit.latitude!,
                  longitude: hit.longitude!,
                  location_name: (hit.display_name || current.location_name || "").trim(),
                };
              });
            })
            .catch(() => {
              /* suggest soft-fail — user can re-pick city */
            });
        }
        return next;
      });
    },
    [],
  );

  const resetSetupFlow = useCallback(() => {
    setBuildStage("idle");
    setSetupError(null);
    setSetupMessage(null);
  }, []);

  const handleCoreSetupSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setSetupError(null);
      setSetupMessage(null);
      setPreviewError(null);
      setNatalPreview(null);
      clearNatalPreviewCache(null);

      if (!setupForm.first_name.trim() || !setupForm.birth_date || !setupForm.location_name.trim()) {
        setSetupError("Заполни имя, дату рождения и место рождения.");
        return;
      }

      setBuildStage("saving");
      try {
        const payload = {
          ...setupForm,
          first_name: setupForm.first_name.trim(),
          last_name: setupForm.last_name?.trim() || null,
          label: setupForm.label.trim() || "Я",
          location_name: setupForm.location_name.trim(),
          birth_time: setupForm.time_unknown ? null : setupForm.birth_time || null,
          latitude: setupForm.latitude ?? null,
          longitude: setupForm.longitude ?? null,
          gender: setupForm.gender || "unspecified",
        };
        const response = await postJson<CoreSetupResponse>("/account/core-setup", payload);
        onCoreProfileUpdated?.(response.core_profile);
        publishCoreProfileUpdate(response.core_profile);
        try {
          const astroRefresh = await getJson<AstroProfilesResponse>("/account/astro-data");
          if (Array.isArray(astroRefresh?.profiles)) {
            onAstroProfilesUpdated?.(astroRefresh.profiles);
          }
        } catch {
          /* список astro не критичен для завершения setup */
        }

        if (warmNatalPreview) {
          setBuildStage("building");
          await loadNatalPreview({ force: true, withEditorial: true });
        }

        setBuildStage("done");
        setSetupMessage(
          "Карта собрана. Теперь система будет использовать её в Today, Guidance и Compatibility. Чем больше ты отвечаешь и фиксируешь действия, тем точнее будут подсказки.",
        );

        await logActiveJTBDAction("profile_core_setup_completed", {
          birth_date: payload.birth_date,
          time_unknown: payload.time_unknown,
          location_name: payload.location_name,
        }).catch((error) => {
          console.error("Failed to log core setup completion", error);
        });
      } catch (error) {
        setBuildStage("idle");
        setSetupError(error instanceof Error ? error.message : "Не удалось сохранить профиль.");
      }
    },
    [setupForm, warmNatalPreview, loadNatalPreview, onCoreProfileUpdated, onAstroProfilesUpdated],
  );

  const isBuilding = buildStage === "saving" || buildStage === "building";
  const currentBuildState = buildStage !== "idle" ? CORE_SETUP_BUILD_COPY[buildStage] : null;
  const hasResolvedBirthplace =
    typeof setupForm.latitude === "number" && typeof setupForm.longitude === "number";

  const buildSteps = useMemo(
    () => [
      {
        title: "Личные данные",
        done: buildStage === "building" || buildStage === "done",
        active: buildStage === "saving",
      },
      {
        title: "Ядро профиля",
        done: buildStage === "done",
        active: buildStage === "building",
      },
      {
        title: "Натальная карта",
        done: buildStage === "done" && !!natalPreview,
        active: buildStage === "done" && !natalPreview && !previewError && warmNatalPreview,
      },
    ],
    [buildStage, natalPreview, previewError, warmNatalPreview],
  );

  return {
    setupForm,
    setSetupForm,
    buildStage,
    setBuildStage,
    setupError,
    setupMessage,
    setSetupMessage,
    natalPreview,
    natalPreviewLoading,
    previewError,
    isBuilding,
    currentBuildState,
    hasResolvedBirthplace,
    buildSteps,
    hydrateSetupForm,
    resetSetupFlow,
    handleCoreSetupSubmit,
    loadNatalPreview,
    reloadNatalPreview,
  };
}
