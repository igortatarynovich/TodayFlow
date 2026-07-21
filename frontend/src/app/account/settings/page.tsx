"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { OrientationRail } from "@/components/orbit";
import { ProductAuxWebScreen } from "@/components/product-ui/ProductAuxWebScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson, postJson, putJson } from "@/lib/api";
import { fetchCoreProfileCached, publishCoreProfileUpdate } from "@/lib/coreProfileCache";
import { signOut } from "@/lib/authSession";
import { t } from "@/lib/i18n";
import { useToast } from "@/components/ToastProvider";
import type { AccountProfile, UserSettings } from "@/lib/types";
import { insightDepthFromProfile } from "@/lib/insightDepth";
import { effectiveNarrativeDepth } from "@/lib/todayNarrativeDepthUi";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";

export default function AccountSettingsPage() {
  const toast = useToast();
  const router = useRouter();
  const { trackMeaningEvent } = useMeaningRuntime();
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [accountMe, setAccountMe] = useState<AccountProfile | null>(null);
  const [form, setForm] = useState<Partial<UserSettings>>({});
  const [saving, setSaving] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [showContent, setShowContent] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const [data, me] = await Promise.all([
          getJson<UserSettings>("/account/profile"),
          getJson<AccountProfile>("/auth/me").catch(() => null),
        ]);
        setSettings(data);
        setAccountMe(me);
        const tier = insightDepthFromProfile(me);
        const depthRaw = data.today_narrative_depth_level ?? "normal";
        const depthEffective = tier === "free" && depthRaw === "deep" ? "normal" : depthRaw;
        setForm({
          ...data,
          subscriptions: data.subscriptions || [],
          gender: data.gender ?? "unspecified",
          today_narrative_depth_level: depthEffective,
        });
      } catch (err) {
        console.error("Failed to load settings", err);
        toast.error(t("settings.errors.loadFailed", "Не удалось загрузить настройки"));
      } finally {
        setLoading(false);
        setTimeout(() => setShowContent(true), 100);
      }
    };

    loadSettings();
  }, [toast]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const tierBefore = insightDepthFromProfile(accountMe);
      const narrativeDepthBefore = settings
        ? effectiveNarrativeDepth(settings.today_narrative_depth_level, tierBefore)
        : null;
      await putJson("/account/profile", { ...form, subscriptions: form.subscriptions ?? [] });
      const [refreshed, me] = await Promise.all([
        getJson<UserSettings>("/account/profile"),
        getJson<AccountProfile>("/auth/me").catch(() => null),
      ]);
      setSettings(refreshed);
      setAccountMe(me);
      const tier = insightDepthFromProfile(me);
      const depthRaw = refreshed.today_narrative_depth_level ?? "normal";
      const depthEffective = tier === "free" && depthRaw === "deep" ? "normal" : depthRaw;
      const narrativeDepthAfter = effectiveNarrativeDepth(refreshed.today_narrative_depth_level, tier);
      if (narrativeDepthBefore != null && narrativeDepthAfter !== narrativeDepthBefore) {
        trackMeaningEvent({
          event_type: "today_narrative_depth_changed",
          event_source: "today",
          quality_score: 0.55,
          payload: { depth_level: narrativeDepthAfter, source: "account_settings" },
        });
      }
      setForm({
        ...refreshed,
        subscriptions: refreshed.subscriptions || [],
        gender: refreshed.gender ?? "unspecified",
        today_narrative_depth_level: depthEffective,
      });
      const coreFresh = await fetchCoreProfileCached({ force: true });
      if (coreFresh) {
        publishCoreProfileUpdate(coreFresh, null);
      }
      toast.success(t("account.saveSuccess", "Настройки сохранены"));
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("settings.errors.saveFailed", "Ошибка при сохранении настроек"));
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
      toast.error(t("settings.password.error.fillAll", "Заполни все поля для смены пароля"));
      return;
    }
    if (passwordForm.newPassword.length < 8) {
      toast.error(t("settings.password.error.minLength", "Новый пароль должен содержать минимум 8 символов"));
      return;
    }
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast.error(t("settings.password.error.mismatch", "Новые пароли не совпадают"));
      return;
    }

    setPasswordSaving(true);
    try {
      const response = await postJson<{ message: string }>("/auth/change-password", {
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword,
      });
      setPasswordForm({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
      toast.success(response.message || t("settings.password.success", "Пароль обновлён"));
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("settings.password.error.saveFailed", "Не удалось изменить пароль"));
    } finally {
      setPasswordSaving(false);
    }
  };

  const greetingOptions = [
    { value: "dear", label: t("birth.register.greeting.dear", "Dear") },
    { value: "hello", label: t("birth.register.greeting.hello", "Hello") },
    { value: "none", label: t("birth.register.greeting.none", "No greeting") },
  ];

  const languageOptions = [
    { value: "en", label: t("birth.register.language.en", "English") },
    { value: "ru", label: t("birth.register.language.ru", "Russian") },
  ];

  const genderOptions: { value: string; label: string }[] = [
    { value: "unspecified", label: t("account.gender.unspecified", "Предпочитаю нейтральные формулировки") },
    { value: "female", label: t("account.gender.female", "Женский род (для текста на «ты»)") },
    { value: "male", label: t("account.gender.male", "Мужской род (для текста на «ты»)") },
  ];

  const narrativeInsightTier = insightDepthFromProfile(accountMe);

  if (loading) {
    return (
      <ProductAuxWebScreen
        title={t("settings.page.title", "Настройки аккаунта")}
        loading
        loadingLabel={t("account.loading", "Загрузка настроек…")}
      />
    );
  }

  return (
    <ProductAuxWebScreen
      testId="account-settings-page"
      title={t("settings.page.title", "Настройки аккаунта")}
      subtitle={t("settings.page.subtitle", "Управляй своими персональными данными и настройками")}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {/* Profile Settings */}
      <section style={{ paddingBottom: "var(--orbit-space-4xl)" }}>
        <div style={{ maxWidth: "800px", margin: "0 auto" }}>
          <div
            className="orbit-card"
            style={{
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s",
            }}
          >
            <OrientationRail
              sectionLabel={t("settings.orientation.section.profile", "Profile")}
              metaLabel={t("settings.orientation.meta.profile", "Personal information")}
              stepLabel={t("settings.basicInfo.label", "Основная информация")}
            />
            <form onSubmit={handleSave} className="orbit-form" style={{ marginTop: "var(--orbit-space-lg)" }}>
              <label>
                {t("account.email", "Email")}
                <input
                  type="email"
                  value={form.email || ""}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </label>
              <label>
                {t("account.firstName", "First name")}
                <input
                  type="text"
                  value={form.first_name || ""}
                  onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                />
              </label>
              <label>
                {t("account.lastName", "Фамилия (необязательно)")}
                <input
                  type="text"
                  value={form.last_name || ""}
                  onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                />
              </label>
              <label>
                {t("account.country", "Country")}
                <input type="text" value={form.country || ""} onChange={(e) => setForm({ ...form, country: e.target.value })} />
              </label>
              <label>
                {t("account.greeting", "Greeting")}
                <select value={form.greeting || ""} onChange={(e) => setForm({ ...form, greeting: e.target.value })}>
                  {greetingOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("account.language", "Language")}
                <select value={form.language || ""} onChange={(e) => setForm({ ...form, language: e.target.value })}>
                  {languageOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("account.genderLabel", "Как согласовывать обращение на «ты»")}
                <select
                  value={form.gender ?? "unspecified"}
                  onChange={(e) => setForm({ ...form, gender: e.target.value })}
                >
                  {genderOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label id="today-narrative-depth-settings">
                {t("settings.todayNarrativeDepth.label", "Глубина текстов «Сегодня»")}
                <select
                  value={form.today_narrative_depth_level ?? "normal"}
                  onChange={(e) => setForm({ ...form, today_narrative_depth_level: e.target.value })}
                >
                  <option value="quick">{t("settings.todayNarrativeDepth.option.quick", "Короче — главное за один проход")}</option>
                  <option value="normal">{t("settings.todayNarrativeDepth.option.normal", "Обычно — баланс деталей")}</option>
                  {narrativeInsightTier !== "free" ? (
                    <option value="deep">{t("settings.todayNarrativeDepth.option.deep", "Глубже — больше контекста за один ответ")}</option>
                  ) : null}
                </select>
              </label>
              <p className="orbit-body-xs orbit-text-muted" style={{ margin: "-0.35rem 0 0", lineHeight: 1.45 }}>
                {narrativeInsightTier === "free"
                  ? t(
                      "settings.todayNarrativeDepth.helpFree",
                      "Режим «Глубже» доступен с подпиской Plus или Pro. Остальное влияет на объём ответа за один вызов (отдельно от тарифа инсайтов).",
                    )
                  : t(
                      "settings.todayNarrativeDepth.helpPaid",
                      "Влияет на объём ответа нарратива дня (не на тариф подписки). Новые тексты подтянутся при следующей генерации.",
                    )}
              </p>
              <button type="submit" disabled={saving} className="orbit-button orbit-button-primary" style={{ marginTop: "var(--orbit-space-md)" }}>
                {saving ? t("account.saving", "Сохранение…") : t("account.saveProfile", "Сохранить")}
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Quick Links */}
      <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-lg)", paddingBottom: "var(--orbit-space-4xl)" }}>
        <div className="orbit-hero-content-container" style={{ maxWidth: "800px", margin: "0 auto" }}>
          <div
            className="orbit-card"
            style={{
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.35s, transform 0.8s ease 0.35s",
              marginBottom: "var(--orbit-space-lg)",
            }}
          >
            <OrientationRail
              sectionLabel={t("settings.orientation.section.security", "Security")}
              metaLabel={t("settings.orientation.meta.password", "Password")}
              stepLabel={t("settings.orientation.step.passwordChange", "Смена пароля")}
            />
            <form onSubmit={handlePasswordChange} className="orbit-form" style={{ marginTop: "var(--orbit-space-lg)" }}>
              <label>
                {t("settings.password.currentLabel", "Текущий пароль")}
                <input
                  type="password"
                  value={passwordForm.currentPassword}
                  onChange={(e) => setPasswordForm((prev) => ({ ...prev, currentPassword: e.target.value }))}
                  autoComplete="current-password"
                />
              </label>
              <label>
                {t("settings.password.newLabel", "Новый пароль")}
                <input
                  type="password"
                  value={passwordForm.newPassword}
                  onChange={(e) => setPasswordForm((prev) => ({ ...prev, newPassword: e.target.value }))}
                  autoComplete="new-password"
                />
              </label>
              <label>
                {t("settings.password.confirmLabel", "Повтори новый пароль")}
                <input
                  type="password"
                  value={passwordForm.confirmPassword}
                  onChange={(e) => setPasswordForm((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                  autoComplete="new-password"
                />
              </label>
              <p className="orbit-body-xs orbit-text-muted" style={{ margin: 0 }}>
                {t("settings.password.forgotIntro", "Если не помнишь текущий пароль, используй")}{" "}
                <Link href="/auth/forgot-password" className="orbit-link-subtle">
                  {t("settings.password.forgotLink", "восстановление доступа")}
                </Link>.
              </p>
              <button type="submit" disabled={passwordSaving} className="orbit-button orbit-button-primary" style={{ marginTop: "var(--orbit-space-md)" }}>
                {passwordSaving
                  ? t("settings.password.submitting", "Обновляю пароль…")
                  : t("settings.password.submit", "Изменить пароль")}
              </button>
            </form>
          </div>

          <div
            className="orbit-card"
            style={{
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s",
            }}
          >
            <OrientationRail
              sectionLabel={t("settings.orientation.section.quickLinks", "Quick links")}
              metaLabel={t("settings.orientation.meta.navigation", "Navigation")}
              stepLabel={t("settings.quickLinks.label", "Быстрые ссылки")}
            />
            <div style={{ marginTop: "var(--orbit-space-lg)", display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
              <Link href="/account/profiles" className="orbit-link-subtle">
                {t("account.quickLinks.profiles", "Управление профилями →")}
              </Link>
              <Link href="/account/subscriptions" className="orbit-link-subtle">
                {t("account.quickLinks.subscriptions", "Подписки →")}
              </Link>
              <Link href="/account/reports" className="orbit-link-subtle">
                {t("account.quickLinks.reports", "История разборов →")}
              </Link>
              <Link href="/onboarding/core" className="orbit-link-subtle">
                {t("account.quickLinks.birthChart", "Создать новый разбор →")}
              </Link>
            </div>
          </div>

          <div
            className="orbit-card"
            style={{
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.45s, transform 0.8s ease 0.45s",
            }}
          >
            <OrientationRail
              sectionLabel={t("settings.session.section", "Session")}
              metaLabel={t("settings.orientation.meta.account", "Account")}
              stepLabel={t("settings.session.label", "Выход")}
            />
            <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-md)" }}>
              {t("settings.session.lead", "Выйти из аккаунта на этом устройстве. Локальные данные сессии будут очищены.")}
            </p>
            <button
              type="button"
              className="orbit-button orbit-button-secondary"
              style={{ marginTop: "var(--orbit-space-md)" }}
              onClick={() => {
                void signOut().then(() => router.replace("/auth?mode=login"));
              }}
            >
              {t("nav.logout", "Log out")}
            </button>
          </div>
        </div>
      </section>
    </ProductAuxWebScreen>
  );
}
