"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DsBody, DsButton, DsEyebrow } from "@/design-system";
import {
  CompatibilityFunnelSection,
  type CompatibilityFunnelArtifact,
} from "@/components/compatibility/CompatibilityFunnelSection";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { t } from "@/lib/i18n";
import type { AstroProfile } from "@/lib/types";

interface CompatibilityResult {
  profile_1: {
    id: number;
    label: string;
    horoscopes: unknown;
  };
  profile_2: {
    id: number;
    label: string;
    horoscopes: unknown;
  };
  funnel_artifact?: CompatibilityFunnelArtifact | null;
  compatibility: {
    overall_score: number;
    aspects: Array<{
      type: string;
      description: string;
      score: number;
    }>;
    synastry: {
      sun?: { profile_1: string; profile_2: string };
      moon?: { profile_1: string; profile_2: string };
      rising?: { profile_1: string; profile_2: string };
    };
  };
}

function aspectTypeLabel(type: string): string {
  if (type === "chinese_zodiac") return "Китайский зодиак";
  if (type === "sun_signs") return "Знаки Солнца";
  return "Знаки Луны";
}

export default function CompatibilityPage() {
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [profiles, setProfiles] = useState<AstroProfile[]>([]);
  const [profile1Id, setProfile1Id] = useState<number | null>(null);
  const [profile2Id, setProfile2Id] = useState<number | null>(null);
  const [compatibility, setCompatibility] = useState<CompatibilityResult | null>(null);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("todayflow_token") : null;
    if (!token) {
      setError(t("account.errors.authRequired", "Требуется авторизация"));
      setLoading(false);
      return;
    }

    const loadProfiles = async () => {
      try {
        const data = await getJson<{ profiles: AstroProfile[] }>("/account/astro-data");
        const safeProfiles = Array.isArray(data?.profiles) ? data.profiles : [];
        setProfiles(safeProfiles);
        if (safeProfiles.length >= 2) {
          setProfile1Id(safeProfiles[0].id);
          setProfile2Id(safeProfiles[1].id);
        }
      } catch (err) {
        console.error("Failed to load profiles", err);
        setError(
          err instanceof Error
            ? err.message
            : t("compatibility.errors.loadProfilesFailed", "Не удалось загрузить профили"),
        );
      } finally {
        setLoading(false);
      }
    };

    void loadProfiles();
  }, []);

  const handleCompare = async () => {
    if (!profile1Id || !profile2Id) {
      toast.error(t("compatibility.errors.selectTwoProfiles", "Выберите два профиля для сравнения"));
      return;
    }

    if (profile1Id === profile2Id) {
      toast.error(t("compatibility.errors.selectDifferentProfiles", "Выберите разные профили для сравнения"));
      return;
    }

    setComparing(true);
    setError(null);

    try {
      const result = await postJson<CompatibilityResult>("/compatibility/compare", {
        profile_id_1: profile1Id,
        profile_id_2: profile2Id,
      });
      setCompatibility(result);
    } catch (err) {
      console.error("Failed to compare profiles", err);
      setError(
        err instanceof Error
          ? err.message
          : t("compatibility.errors.compareFailed", "Не удалось сравнить профили"),
      );
      toast.error(t("compatibility.errors.compareFailed", "Ошибка при сравнении профилей"));
    } finally {
      setComparing(false);
    }
  };

  if (loading) {
    return (
      <ProductPageScreen
        testId="account-compatibility-page"
        title="Совместимость"
        loading
        loadingLabel="Загрузка профилей…"
      />
    );
  }

  if (error && !profiles.length) {
    return (
      <ProductPageScreen
        testId="account-compatibility-page"
        title="Совместимость"
        guest={{
          message: error,
          ctaHref: "/auth?redirect=/account/compatibility",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  if (profiles.length < 2) {
    return (
      <ProductPageScreen
        testId="account-compatibility-page"
        eyebrow="По сохранённым профилям"
        title="Совместимость"
        subtitle="Нужны минимум два профиля."
        railTitle="Совместимость"
        railHint="Добавь второй профиль в круг людей, чтобы сравнить карты."
        contentClassName={pl.content}
      >
        <nav className={pl.toolbar} aria-label="Навигация">
          <Link href="/account" className={pl.textLink}>
            ← Кабинет
          </Link>
          <Link href="/compatibility" className={pl.textLink}>
            Хаб совместимости
          </Link>
        </nav>
        <div className={pl.loginGate}>
          <DsBody size="sm" muted>
            Создай ещё один профиль — партнёра, ребёнка или близкого человека.
          </DsBody>
          <DsButton href="/account/profiles">Создать профиль</DsButton>
        </div>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="account-compatibility-page"
      eyebrow="По сохранённым профилям"
      title="Совместимость"
      subtitle="Два профиля — расчёт ниже."
      railTitle="Совместимость"
      railHint="Сравнение по сохранённым профилям из круга людей."
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <nav className={pl.toolbar} aria-label="Навигация">
        <Link href="/compatibility" className={pl.textLink}>
          ← Совместимость
        </Link>
        <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap", alignItems: "center" }}>
          <Link href="/compatibility/analyze" className={pl.textLink}>
            Единый экран
          </Link>
          <Link href="/account" className={pl.textLink}>
            Кабинет
          </Link>
        </div>
      </nav>

      <section className={pl.panel} aria-labelledby="compat-profile-selection">
        <DsEyebrow id="compat-profile-selection">
          {t("compat.page.orientation.selectionStep", "Выбор профилей")}
        </DsEyebrow>
        <div className={pl.grid2} style={{ marginTop: "1rem" }}>
          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="compat-profile-1">
              Первый профиль
            </label>
            <select
              id="compat-profile-1"
              value={profile1Id ?? ""}
              onChange={(e) => setProfile1Id(Number(e.target.value))}
              className={pl.fieldInput}
            >
              <option value="">Выберите профиль</option>
              {profiles.map((profile) => (
                <option key={profile.id} value={profile.id}>
                  {profile.label} {profile.is_primary ? "(Основной)" : ""}
                </option>
              ))}
            </select>
          </div>
          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="compat-profile-2">
              Второй профиль
            </label>
            <select
              id="compat-profile-2"
              value={profile2Id ?? ""}
              onChange={(e) => setProfile2Id(Number(e.target.value))}
              className={pl.fieldInput}
            >
              <option value="">Выберите профиль</option>
              {profiles.map((profile) => (
                <option key={profile.id} value={profile.id}>
                  {profile.label} {profile.is_primary ? "(Основной)" : ""}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div style={{ marginTop: "1.25rem" }}>
          <DsButton
            size="block"
            disabled={comparing || !profile1Id || !profile2Id || profile1Id === profile2Id}
            onClick={handleCompare}
          >
            {comparing ? "Сравниваю…" : "Сравнить профили"}
          </DsButton>
        </div>
      </section>

      {error ? (
        <div className={pl.panel}>
          <DsBody size="sm">{error}</DsBody>
        </div>
      ) : null}

      {compatibility ? (
        <section className={pl.panel} aria-labelledby="compat-results">
          <DsEyebrow id="compat-results">
            {t("compat.page.orientation.resultsSection", "Compatibility")} ·{" "}
            {compatibility.compatibility.overall_score}%
          </DsEyebrow>

          <div className={pl.scoreHero}>
            <p className={pl.scoreValue}>{compatibility.compatibility.overall_score}%</p>
            <DsBody size="sm" muted>
              {compatibility.profile_1.label} · {compatibility.profile_2.label}
            </DsBody>
          </div>

          {compatibility.funnel_artifact ? (
            <CompatibilityFunnelSection artifact={compatibility.funnel_artifact} omitTopMargin />
          ) : null}

          {compatibility.compatibility.synastry ? (
            <div style={{ marginTop: "1.5rem" }}>
              <h3 className={v2.sectionTitle}>Знаки</h3>
              <div className={pl.grid2} style={{ marginTop: "0.75rem" }}>
                {compatibility.compatibility.synastry.sun ? (
                  <div className={pl.panel} style={{ padding: "1rem" }}>
                    <p className={pl.fieldLabel}>Солнце</p>
                    <DsBody size="sm" muted>
                      {compatibility.profile_1.label}: {compatibility.compatibility.synastry.sun.profile_1}
                    </DsBody>
                    <DsBody size="sm" muted>
                      {compatibility.profile_2.label}: {compatibility.compatibility.synastry.sun.profile_2}
                    </DsBody>
                  </div>
                ) : null}
                {compatibility.compatibility.synastry.moon ? (
                  <div className={pl.panel} style={{ padding: "1rem" }}>
                    <p className={pl.fieldLabel}>Луна</p>
                    <DsBody size="sm" muted>
                      {compatibility.profile_1.label}: {compatibility.compatibility.synastry.moon.profile_1}
                    </DsBody>
                    <DsBody size="sm" muted>
                      {compatibility.profile_2.label}: {compatibility.compatibility.synastry.moon.profile_2}
                    </DsBody>
                  </div>
                ) : null}
                {compatibility.compatibility.synastry.rising ? (
                  <div className={pl.panel} style={{ padding: "1rem" }}>
                    <p className={pl.fieldLabel}>Восходящий</p>
                    <DsBody size="sm" muted>
                      {compatibility.profile_1.label}: {compatibility.compatibility.synastry.rising.profile_1}
                    </DsBody>
                    <DsBody size="sm" muted>
                      {compatibility.profile_2.label}: {compatibility.compatibility.synastry.rising.profile_2}
                    </DsBody>
                  </div>
                ) : null}
              </div>
            </div>
          ) : null}

          {compatibility.compatibility.aspects?.length ? (
            <div style={{ marginTop: "1.5rem" }}>
              <h3 className={v2.sectionTitle}>Аспекты</h3>
              <div className={pl.formStack} style={{ marginTop: "0.75rem" }}>
                {compatibility.compatibility.aspects.map((aspect, index) => (
                  <div
                    key={index}
                    className={pl.panel}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: "1rem",
                      padding: "1rem",
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p className={pl.fieldLabel}>{aspectTypeLabel(aspect.type)}</p>
                      <DsBody size="sm" muted>
                        {aspect.description}
                      </DsBody>
                    </div>
                    <p className={pl.scoreValue} style={{ fontSize: "1.5rem" }}>
                      {aspect.score}/10
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </section>
      ) : null}

      <div style={{ textAlign: "center" }}>
        <Link href="/account/profiles" className={pl.textLink}>
          ← Вернуться к профилям
        </Link>
      </div>
    </ProductPageScreen>
  );
}
