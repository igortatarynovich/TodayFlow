"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { deleteJson, getJson, postJson } from "@/lib/api";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { useAuth } from "@/lib/useAuth";
import { astroBirthFactsCaption, mergeAstroSaveIntoProfilesList } from "@/lib/accountAstroMeta";
import { publishCoreProfileUpdate } from "@/lib/coreProfileCacheStorage";
import type { AstroProfile, AstroProfileSaveResponse } from "@/lib/types";
import { useToast } from "@/components/ToastProvider";
import {
  buildPairCompatibilityRoute,
  buildQuickCompatibilityRoute,
  normalizeProfilesForCompatibility,
} from "@/lib/compatibilityRoutes";

type ProfilesResponse = {
  profiles: AstroProfile[];
  max_profiles: number;
  current_count: number;
  can_create_more: boolean;
};

type CreateProfileForm = {
  label: string;
  relation: "self" | "partner" | "child" | "close_person";
  birth_date: string;
  birth_time: string;
  time_unknown: boolean;
  location_name: string;
  is_primary: boolean;
};

const EMPTY_FORM: CreateProfileForm = {
  label: "",
  relation: "close_person",
  birth_date: "",
  birth_time: "",
  time_unknown: false,
  location_name: "",
  is_primary: false,
};

function relationModeForProfile(profile: AstroProfile): "romantic" | "family" | "parent_child" | "business" {
  if (profile.relation === "child") return "parent_child";
  if (profile.relation === "partner") return "romantic";
  const normalized = profile.label.toLowerCase();
  if (normalized.includes("коллег") || normalized.includes("работ") || normalized.includes("босс") || normalized.includes("команда")) {
    return "business";
  }
  if (
    normalized.includes("мама") ||
    normalized.includes("пап") ||
    normalized.includes("брат") ||
    normalized.includes("сест") ||
    normalized.includes("бабуш") ||
    normalized.includes("дедуш")
  ) {
    return "family";
  }
  return "romantic";
}

function relationHint(profile: AstroProfile) {
  if (profile.is_primary || profile.relation === "self") return "Основной личный профиль";
  if (profile.relation === "partner") return "Профиль партнера для совместимости и динамики отношений";
  if (profile.relation === "child") return "Профиль ребенка для семейного и поддерживающего чтения";
  return "Дополнительный профиль для совместимости и разборов";
}

function relationLabel(relation: AstroProfile["relation"] | undefined, isPrimary: boolean) {
  if (isPrimary || relation === "self") return "Личный профиль";
  if (relation === "partner") return "Партнер";
  if (relation === "child") return "Ребенок";
  return "Близкий человек";
}

export default function ProfilesPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();

  const [profiles, setProfiles] = useState<AstroProfile[]>([]);
  const [limits, setLimits] = useState<ProfilesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [form, setForm] = useState<CreateProfileForm>(EMPTY_FORM);

  const loadProfiles = useCallback(async () => {
    try {
      const data = await getJson<ProfilesResponse>("/account/astro-data");
      setProfiles(Array.isArray(data?.profiles) ? data.profiles : []);
      setLimits(data || null);
    } catch (err) {
      console.error("Error loading profiles:", err);
      toast.error("Не удалось загрузить профили");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth?redirect=/account/profiles");
      return;
    }

    if (isAuthenticated) {
      void loadProfiles();
    }
  }, [authLoading, isAuthenticated, loadProfiles, router]);

  const primaryProfile = useMemo(
    () => profiles.find((profile) => profile.is_primary) || profiles[0] || null,
    [profiles],
  );
  const compatibilityProfiles = useMemo(() => normalizeProfilesForCompatibility(profiles), [profiles]);
  const quickCompatibilityRoute = useMemo(
    () =>
      buildQuickCompatibilityRoute({
        profiles: compatibilityProfiles,
        primaryProfileId: primaryProfile?.id || null,
        preferred: "any",
      }),
    [compatibilityProfiles, primaryProfile?.id],
  );
  const hasSecondaryProfiles = useMemo(
    () => profiles.some((profile) => !profile.is_primary),
    [profiles],
  );

  const handleSetPrimary = async (profileId: number) => {
    try {
      const saved = await postJson<AstroProfileSaveResponse>(`/account/astro-data/${profileId}/primary`, {});
      if (saved.core_profile) {
        publishCoreProfileUpdate(saved.core_profile, saved.core_profile.astro?.profile_id ?? saved.id);
      }
      setProfiles((prev) => prev.map((p) => ({ ...p, is_primary: p.id === profileId })));
      toast.success("Основной профиль обновлен");
    } catch (err) {
      console.error("Error setting primary profile:", err);
      toast.error("Не удалось сделать профиль основным");
    }
  };

  const handleDelete = async (profileId: number) => {
    const profile = profiles.find((item) => item.id === profileId);
    if (!profile) return;

    if (!window.confirm(`Удалить профиль "${profile.label}"?`)) {
      return;
    }

    try {
      setDeleting(profileId);
      await deleteJson(`/account/astro-data/${profileId}`);
      toast.success("Профиль удален");
      await loadProfiles();
    } catch (err) {
      console.error("Error deleting profile:", err);
      toast.error("Не удалось удалить профиль");
    } finally {
      setDeleting(null);
    }
  };

  const handleCreate = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!limits?.can_create_more) {
      toast.error("Лимит профилей достигнут");
      return;
    }

    if (!form.label.trim() || !form.birth_date || !form.location_name.trim()) {
      toast.error("Заполни название, дату и место рождения");
      return;
    }

    try {
      setSaving(true);
      const saved = await postJson<AstroProfileSaveResponse>("/account/astro-data", {
        label: form.label.trim(),
        birth_date: form.birth_date,
        birth_time: form.time_unknown ? null : form.birth_time || null,
        time_unknown: form.time_unknown,
        location_name: form.location_name.trim(),
        relation: profiles.length === 0 ? "self" : form.relation,
        is_primary: profiles.length === 0 ? true : form.is_primary,
      });
      if (saved.core_profile) {
        publishCoreProfileUpdate(saved.core_profile, saved.core_profile.astro?.profile_id ?? saved.id);
      }
      setProfiles((prev) => {
        const existed = prev.some((p) => p.id === saved.id);
        const next = mergeAstroSaveIntoProfilesList(prev, saved);
        if (!existed) {
          setLimits((lim) => {
            if (!lim) return lim;
            const current_count = Math.min(lim.max_profiles, lim.current_count + 1);
            return { ...lim, current_count, can_create_more: current_count < lim.max_profiles };
          });
        }
        return next;
      });
      toast.success("Профиль создан");
      setForm(EMPTY_FORM);
    } catch (err: any) {
      console.error("Error creating profile:", err);
      toast.error(err?.message || "Не удалось создать профиль");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        title="Круг людей"
        loading
        loadingLabel="Загрузка профилей…"
      />
    );
  }

  const profilesIntro =
    "Здесь хранится твой круг: ты и люди, с которыми тебе важно понять связь. Каждый профиль можно использовать для совместимости и разборов; ядром остаётся твой личный профиль.";

  return (
    <ProductPageScreen
      testId="account-profiles-page"
      eyebrow="Profile Circle"
      title="Круг людей"
      subtitle={profilesIntro}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
          <div className={pl.panel}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.55rem", marginBottom: "1rem" }}>
              <Link href="/profile" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                Мой профиль
              </Link>
              <Link
                href={hasSecondaryProfiles ? quickCompatibilityRoute.href : "#add-profile"}
                className="orbit-button orbit-button-primary orbit-button-sm"
                style={{ textDecoration: "none" }}
              >
                {hasSecondaryProfiles ? quickCompatibilityRoute.label : "Добавить человека"}
              </Link>
            </div>

            <div className={pl.grid2}>
              <div className={pl.panel} style={{ padding: "0.95rem" }}>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>Всего профилей</p>
                <p className="orbit-heading-2" style={{ margin: "0.35rem 0 0", color: "#1f2937" }}>{limits?.current_count || 0}</p>
              </div>
              <div className={pl.panel} style={{ padding: "0.95rem" }}>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>Лимит плана</p>
                <p className="orbit-heading-2" style={{ margin: "0.35rem 0 0", color: "#1f2937" }}>{limits?.max_profiles || 1}</p>
              </div>
              <div className={pl.panel} style={{ padding: "0.95rem" }}>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>Основной профиль</p>
                <p className="orbit-heading-3" style={{ margin: "0.35rem 0 0", color: "#1f2937" }}>{primaryProfile?.label || "Не задан"}</p>
              </div>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1.05fr) minmax(320px, 0.95fr)", gap: "1rem", alignItems: "start" }}>
            <div className={pl.panel}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.75rem", flexWrap: "wrap", marginBottom: "0.9rem" }}>
                <div>
                  <p className="orbit-body-xs" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.12em", color: "#a17d4c" }}>
                    Saved Profiles
                  </p>
                  <h2 className="orbit-heading-2" style={{ margin: "0.3rem 0 0" }}>
                    Круг людей
                  </h2>
                </div>
                {primaryProfile ? (
                  <Link
                    href={hasSecondaryProfiles ? quickCompatibilityRoute.href : "#add-profile"}
                    className="orbit-button orbit-button-secondary orbit-button-sm"
                    style={{ textDecoration: "none" }}
                  >
                    {hasSecondaryProfiles ? quickCompatibilityRoute.label : "Добавить связь"}
                  </Link>
                ) : null}
              </div>

              {profiles.length === 0 ? (
                <div style={{ padding: "1rem", borderRadius: "20px", background: "rgba(255,255,255,0.8)", border: "1px solid rgba(198, 166, 119, 0.2)" }}>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.75 }}>
                    Пока здесь только твой основной профиль. Добавь любого важного человека из круга, чтобы открыть совместимость и персональные сравнения.
                  </p>
                </div>
              ) : (
                <div style={{ display: "grid", gap: "0.8rem" }}>
                  {profiles.map((profile) => {
                    const birthFactsLine = astroBirthFactsCaption(profile);
                    return (
                    <div
                      key={profile.id}
                      className="orbit-card todayflow-panel"
                      style={{
                        padding: "1rem",
                        borderRadius: "22px",
                        border: profile.is_primary ? "1px solid rgba(188, 148, 88, 0.52)" : "1px solid rgba(198, 166, 119, 0.22)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", alignItems: "flex-start" }}>
                        <div style={{ flex: "1 1 260px", minWidth: 0 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.55rem", flexWrap: "wrap" }}>
                            <h3 className="orbit-heading-3" style={{ margin: 0 }}>
                              {profile.label}
                            </h3>
                            {profile.is_primary ? (
                              <span className="todayflow-month-pill" style={{ padding: "0.32rem 0.68rem", fontSize: "0.78rem", color: "#7c5a33" }}>
                                Основной
                              </span>
                            ) : null}
                          </div>
                          <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#5f4930" }}>
                            {new Date(profile.birth_date).toLocaleDateString("ru-RU", {
                              day: "numeric",
                              month: "long",
                              year: "numeric",
                            })}
                            {profile.location_name ? ` · ${profile.location_name}` : ""}
                          </p>
                          <p className="orbit-body-xs" style={{ margin: "0.28rem 0 0", color: "#8a6f49" }}>
                            {relationLabel(profile.relation, Boolean(profile.is_primary))}
                          </p>
                          {profile.birth_time ? (
                            <p className="orbit-body-xs" style={{ margin: "0.2rem 0 0", color: "#8a6f49" }}>
                              Время рождения: {profile.birth_time}
                            </p>
                          ) : null}
                          <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#6b7280", lineHeight: 1.6 }}>
                            {relationHint(profile)}
                          </p>
                          {birthFactsLine ? (
                            <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#64748b", lineHeight: 1.6 }}>
                              {birthFactsLine}{" "}
                              <Link href="/profile" className="orbit-link-subtle" style={{ whiteSpace: "nowrap" }}>
                                Редактировать в профиле →
                              </Link>
                            </p>
                          ) : null}
                          <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                            {profile.is_primary
                              ? "Этот профиль — твой главный. Через него идут Today, прогнозы и сравнения с другими людьми."
                              : "С этим человеком можно сразу открыть совместимость и посмотреть, где связь дается легче, а где требует больше ясности."}
                          </p>
                        </div>

                        <div style={{ display: "grid", gap: "0.5rem", justifyItems: "end" }}>
                          {!profile.is_primary && primaryProfile ? (
                            <div
                              style={{
                                padding: "0.75rem 0.85rem",
                                borderRadius: "16px",
                                background: "rgba(255,255,255,0.82)",
                                border: "1px solid rgba(198, 166, 119, 0.18)",
                                maxWidth: "320px",
                              }}
                            >
                              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                                Следующий ход
                              </p>
                              <p className="orbit-body-xs" style={{ margin: "0.32rem 0 0", color: "#475569", lineHeight: 1.6 }}>
                                Сначала сравни этого человека со своим основным профилем, потом при необходимости углубляйся в быстрый или полный разбор.
                              </p>
                            </div>
                          ) : null}
                          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", justifyContent: "flex-end" }}>
                          {!profile.is_primary ? (
                            <button
                              onClick={() => void handleSetPrimary(profile.id)}
                              className="orbit-button orbit-button-secondary orbit-button-xs"
                              disabled={deleting === profile.id}
                            >
                              Сделать основным
                            </button>
                          ) : null}
                          <Link
                            href={
                              profile.is_primary
                                ? quickCompatibilityRoute.href
                                : buildPairCompatibilityRoute(profile, primaryProfile?.id || null).href
                            }
                            className="orbit-button orbit-button-primary orbit-button-xs"
                            style={{ textDecoration: "none" }}
                          >
                            {profile.is_primary
                              ? hasSecondaryProfiles
                                ? quickCompatibilityRoute.label
                                : "Добавить связь"
                              : "Открыть связь"}
                          </Link>
                          {!profile.is_primary ? (
                            <Link
                              href={`/compatibility?profile1=${primaryProfile?.id || profile.id}&profile2=${profile.id}&mode=sign&relation_mode=${relationModeForProfile(profile)}`}
                              className="orbit-button orbit-button-secondary orbit-button-xs"
                              style={{ textDecoration: "none" }}
                            >
                              Быстрый слой
                            </Link>
                          ) : null}
                          <Link
                            href="/compatibility/birthdates"
                            className="orbit-button orbit-button-secondary orbit-button-xs"
                            style={{ textDecoration: "none" }}
                          >
                            Сравнить по датам
                          </Link>
                          <button
                            onClick={() => void handleDelete(profile.id)}
                            className="orbit-button orbit-button-secondary orbit-button-xs"
                            disabled={deleting === profile.id}
                            style={{ color: "#b91c1c" }}
                          >
                            {deleting === profile.id ? "Удаление..." : "Удалить"}
                          </button>
                          </div>
                        </div>
                      </div>
                    </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div id="add-profile" className={pl.panel}>
              <p className="orbit-body-xs" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.12em", color: "#a17d4c" }}>
                Add Profile
              </p>
              <h2 className="orbit-heading-2" style={{ margin: "0.3rem 0 0.45rem" }}>
                Добавить человека
              </h2>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.7 }}>
                Добавляй только нужные данные: имя, дата, место и при наличии время рождения. Этого достаточно, чтобы потом открыть совместимость,
                сравнение или отдельный разбор связи.
              </p>

              {!limits?.can_create_more ? (
                <div style={{ marginTop: "0.95rem", padding: "1rem", borderRadius: "18px", background: "rgba(255,255,255,0.82)", border: "1px solid rgba(198, 166, 119, 0.22)" }}>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.65 }}>
                    Ты достиг лимита профилей по текущему плану.
                  </p>
                  <div style={{ marginTop: "0.7rem" }}>
                    <Link href="/pricing" className="orbit-button orbit-button-primary orbit-button-sm" style={{ textDecoration: "none" }}>
                      Посмотреть планы
                    </Link>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleCreate} style={{ display: "grid", gap: "0.75rem", marginTop: "0.95rem" }}>
                  <label style={{ display: "grid", gap: "0.3rem" }}>
                    <span className="orbit-body-sm" style={{ color: "#6a5132", fontWeight: 600 }}>Название профиля</span>
                    <input
                      type="text"
                      value={form.label}
                      onChange={(event) => setForm((prev) => ({ ...prev, label: event.target.value }))}
                      placeholder="Например: Аня, Друг, Коллега, Папа"
                      className="orbit-input"
                    />
                  </label>
                  <label style={{ display: "grid", gap: "0.3rem" }}>
                    <span className="orbit-body-sm" style={{ color: "#6a5132", fontWeight: 600 }}>Роль в круге</span>
                    <select
                      value={profiles.length === 0 ? "self" : form.relation}
                      onChange={(event) =>
                        setForm((prev) => ({
                          ...prev,
                          relation: event.target.value as CreateProfileForm["relation"],
                        }))
                      }
                      className="orbit-input"
                      disabled={profiles.length === 0}
                    >
                      <option value="self">Я</option>
                      <option value="partner">Партнер / супруг</option>
                      <option value="child">Ребенок</option>
                      <option value="close_person">Близкий человек</option>
                    </select>
                  </label>
                  <label style={{ display: "grid", gap: "0.3rem" }}>
                    <span className="orbit-body-sm" style={{ color: "#6a5132", fontWeight: 600 }}>Дата рождения</span>
                    <input
                      type="date"
                      value={form.birth_date}
                      onChange={(event) => setForm((prev) => ({ ...prev, birth_date: event.target.value }))}
                      className="orbit-input"
                    />
                  </label>
                  <label style={{ display: "grid", gap: "0.3rem" }}>
                    <span className="orbit-body-sm" style={{ color: "#6a5132", fontWeight: 600 }}>Место рождения</span>
                    <input
                      type="text"
                      value={form.location_name}
                      onChange={(event) => setForm((prev) => ({ ...prev, location_name: event.target.value }))}
                      placeholder="Город, страна"
                      className="orbit-input"
                    />
                  </label>
                  <label style={{ display: "flex", alignItems: "center", gap: "0.55rem" }}>
                    <input
                      type="checkbox"
                      checked={form.time_unknown}
                      onChange={(event) => setForm((prev) => ({ ...prev, time_unknown: event.target.checked, birth_time: event.target.checked ? "" : prev.birth_time }))}
                    />
                    <span className="orbit-body-sm" style={{ color: "#5f4930" }}>Время рождения неизвестно</span>
                  </label>
                  {!form.time_unknown ? (
                    <label style={{ display: "grid", gap: "0.3rem" }}>
                      <span className="orbit-body-sm" style={{ color: "#6a5132", fontWeight: 600 }}>Время рождения</span>
                      <input
                        type="time"
                        value={form.birth_time}
                        onChange={(event) => setForm((prev) => ({ ...prev, birth_time: event.target.value }))}
                        className="orbit-input"
                      />
                    </label>
                  ) : null}
                  {profiles.length > 0 ? (
                    <label style={{ display: "flex", alignItems: "center", gap: "0.55rem" }}>
                      <input
                        type="checkbox"
                        checked={form.is_primary}
                        onChange={(event) => setForm((prev) => ({ ...prev, is_primary: event.target.checked }))}
                      />
                      <span className="orbit-body-sm" style={{ color: "#5f4930" }}>Сделать основным профилем</span>
                    </label>
                  ) : null}
                  <button type="submit" className="orbit-button orbit-button-primary" disabled={saving}>
                    {saving ? "Сохраняю..." : "Создать профиль"}
                  </button>
                </form>
              )}

              <div style={{ marginTop: "1rem", padding: "0.95rem", borderRadius: "18px", background: "rgba(255,255,255,0.82)", border: "1px solid rgba(198, 166, 119, 0.18)" }}>
                <p className="orbit-body-xs" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.12em", color: "#a17d4c" }}>
                  Дальше
                </p>
                <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#5f4930", lineHeight: 1.7 }}>
                  После сохранения профиль сразу появится в списке. Оттуда можно в один тап открыть совместимость с твоим основным профилем
                  и быстро перейти к разбору конкретной связи.
                </p>
              </div>
            </div>
          </div>
    </ProductPageScreen>
  );
}
