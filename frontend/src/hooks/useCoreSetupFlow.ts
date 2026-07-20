"use client";

import { useCallback, useMemo, useState, type FormEvent } from "react";
import { getJson, postJson } from "@/lib/api";
import { publishCoreProfileUpdate } from "@/lib/coreProfileCacheStorage";
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

export function useCoreSetupFlow(options: UseCoreSetupFlowOptions = {}) {
  const { warmNatalPreview = false, onCoreProfileUpdated, onAstroProfilesUpdated } = options;

  const [buildStage, setBuildStage] = useState<CoreSetupBuildStage>("idle");
  const [setupError, setSetupError] = useState<string | null>(null);
  const [setupMessage, setSetupMessage] = useState<string | null>(null);
  const [natalPreview, setNatalPreview] = useState<NatalChartPreview | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [setupForm, setSetupForm] = useState<CoreSetupPayload>(() => createEmptyCoreSetupForm());

  const loadNatalPreview = useCallback(async () => {
    setPreviewError(null);
    try {
      const chart = await getJson<NatalChartPreview>("/natal-chart/?include_interpretations=true");
      setNatalPreview(chart);
    } catch (err) {
      setPreviewError(err instanceof Error ? err.message : "Не удалось построить натальную карту.");
      setNatalPreview(null);
    }
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
          void getJson<{ latitude?: number; longitude?: number; local_name?: string; name?: string }>(
            `/astro/geocode?q=${encodeURIComponent(place)}`,
          )
            .then((hit) => {
              if (typeof hit?.latitude !== "number" || typeof hit?.longitude !== "number") return;
              setSetupForm((current) => {
                if ((current.location_name || "").trim().toLowerCase() !== place.toLowerCase()) {
                  return current;
                }
                return {
                  ...current,
                  latitude: hit.latitude!,
                  longitude: hit.longitude!,
                };
              });
            })
            .catch(() => {
              /* suggest/lookup soft-fail — user can re-pick city */
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
          await loadNatalPreview();
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
    previewError,
    isBuilding,
    currentBuildState,
    hasResolvedBirthplace,
    buildSteps,
    hydrateSetupForm,
    resetSetupFlow,
    handleCoreSetupSubmit,
    loadNatalPreview,
  };
}
