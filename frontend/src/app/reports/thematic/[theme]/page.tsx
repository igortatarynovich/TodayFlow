"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { buildAuthHref } from "@/lib/authRedirect";
import { LoadingSpinner } from "@/components/orbit";
import { ThematicReportForm, ThematicReportDisplay } from "@/components/reports";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson, postJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { useToast } from "@/components/ToastProvider";
import { getThematicReportMeta } from "@/lib/thematicReports";
import type { ThematicReport, AstroProfile } from "@/lib/types";

export default function ThematicReportPage({ params }: { params: { theme: string } }) {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [report, setReport] = useState<ThematicReport | null>(null);
  const [profiles, setProfiles] = useState<AstroProfile[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showContent, setShowContent] = useState(false);

  const theme = params.theme;
  const themeInfo = getThematicReportMeta(theme);

  useEffect(() => {
    if (!themeInfo) {
      setError("Неизвестный тип разбора");
      setLoading(false);
      return;
    }

    if (authLoading) return;

    if (!isAuthenticated) {
      setError("Требуется авторизация");
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        const profilesData = await getJson<{ profiles: AstroProfile[] }>("/account/astro-data").catch(() => ({ profiles: [] }));
        const safeProfiles = Array.isArray(profilesData?.profiles) ? profilesData.profiles : [];
        setProfiles(safeProfiles);
        const primaryProfile = safeProfiles.find((p) => p.is_primary) || safeProfiles[0];
        if (primaryProfile) {
          setSelectedProfileId(primaryProfile.id);
        }

        try {
          const existingReport = await getJson<ThematicReport>(`/reports/thematic/${theme}`);
          setReport(existingReport);
        } catch {
          console.log("No existing report found");
        }
      } catch (err) {
        console.error("Failed to load data", err);
        setError(err instanceof Error ? err.message : "Не удалось загрузить данные");
      } finally {
        setLoading(false);
        setTimeout(() => setShowContent(true), 100);
      }
    };

    loadData();
  }, [isAuthenticated, authLoading, theme, themeInfo]);

  const handleGenerate = async () => {
    if (!selectedProfileId) {
      toast.error("Выберите профиль");
      return;
    }

    const profile = profiles.find((p) => p.id === selectedProfileId);
    if (!profile) {
      toast.error("Профиль не найден");
      return;
    }

    if (!profile.birth_date || !profile.location_name) {
      toast.error("В профиле отсутствуют необходимые данные (дата рождения, место)");
      return;
    }

    setGenerating(true);
    try {
      const payload = {
        date: profile.birth_date,
        time: profile.time_unknown ? null : (profile.birth_time || null),
        location: profile.location_name,
        coordinates: profile.latitude && profile.longitude ? {
          latitude: profile.latitude,
          longitude: profile.longitude,
        } : undefined,
      };

      const newReport = await postJson<ThematicReport>(`/reports/thematic/${theme}`, payload);
      setReport(newReport);
      toast.success("Разбор успешно создан");
    } catch (err: any) {
      console.error("Failed to generate report", err);
      toast.error(err?.message || "Не удалось создать разбор");
    } finally {
      setGenerating(false);
    }
  };

  if (loading || authLoading) {
    return (
      <ProductPageScreen
        testId="thematic-report-page"
        title={themeInfo?.title ?? "Тематический разбор"}
        loading
        loadingLabel="Загрузка…"
      />
    );
  }

  if (error && !isAuthenticated) {
    return (
      <ProductPageScreen
        testId="thematic-report-page"
        title={themeInfo?.title ?? "Тематический разбор"}
        guest={{
          message: error,
          ctaHref: buildAuthHref("login", `/reports/thematic/${theme}`),
          ctaLabel: "Войти",
        }}
      />
    );
  }

  if (!themeInfo) {
    return (
      <ProductPageScreen
        testId="thematic-report-page"
        title="Ошибка"
        subtitle="Неизвестный тип разбора"
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <button type="button" className="orbit-button orbit-button-primary" onClick={() => router.push("/today")}>
            На главную
          </button>
        </section>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="thematic-report-page"
      title={`${themeInfo.icon} ${themeInfo.title}`}
      subtitle={themeInfo.description}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {!report ? (
        <ThematicReportForm
          profiles={profiles}
          selectedProfileId={selectedProfileId}
          onProfileChange={setSelectedProfileId}
          onGenerate={handleGenerate}
          generating={generating}
          showContent={showContent}
        />
      ) : (
        <ThematicReportDisplay
          report={report}
          themeTitle={themeInfo.title}
          onRegenerate={handleGenerate}
          generating={generating}
          showContent={showContent}
        />
      )}

      <p style={{ textAlign: "center", marginTop: "var(--orbit-space-xl)" }}>
        <Link href="/account/reports" className="orbit-link-subtle">
          ← Вернуться к истории разборов
        </Link>
      </p>
    </ProductPageScreen>
  );
}
