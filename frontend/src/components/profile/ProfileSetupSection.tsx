"use client";

import Link from "next/link";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";
import { type FormEvent } from "react";
import { LoadingSpinner } from "@/components/orbit";
import { CityAutocompleteInput } from "@/components/CityAutocompleteInput";
import { SurfaceInsight, surfaceInsightStyles } from "@/components/foundation/SurfaceInsight";
import type { GeocodeResult } from "@/lib/types";

type ProfileSetupFormData = {
  first_name: string;
  last_name?: string | null;
  label: string;
  birth_date: string;
  birth_time?: string | null;
  time_unknown: boolean;
  location_name: string;
  latitude?: number | null;
  longitude?: number | null;
  gender: string;
};

type BuildStateCopy = {
  eyebrow: string;
  title: string;
  description: string;
  steps: string[];
};

function SetupStatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <SurfaceInsight className={surfaceInsightStyles.compact}>
      <p className={surfaceInsightStyles.statLabel}>{label}</p>
      <p className={surfaceInsightStyles.statValue}>{value}</p>
      {hint ? <p className={surfaceInsightStyles.statHint}>{hint}</p> : null}
    </SurfaceInsight>
  );
}

type ProfileSetupSectionProps = {
  variant?: "profile" | "onboarding";
  currentBuildState: BuildStateCopy | null;
  buildStage: "idle" | "saving" | "building" | "done";
  isBuilding: boolean;
  setupForm: ProfileSetupFormData;
  hasResolvedBirthplace: boolean;
  setupError: string | null;
  setupMessage: string | null;
  onFinishSetupFlow: () => void;
  onReopenSetupForm: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onFieldChange: <K extends keyof ProfileSetupFormData>(field: K, value: ProfileSetupFormData[K]) => void;
  onLocationSelect: (item: GeocodeResult) => void;
};

export function ProfileSetupSection({
  variant = "profile",
  currentBuildState,
  buildStage,
  isBuilding,
  setupForm,
  hasResolvedBirthplace,
  setupError,
  setupMessage,
  onFinishSetupFlow,
  onReopenSetupForm,
  onSubmit,
  onFieldChange,
  onLocationSelect,
}: ProfileSetupSectionProps) {
  const showCompletionState = buildStage === "done";
  const isOnboarding = variant === "onboarding";

  return (
    <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "minmax(0, 1fr)" }}>
      <SurfaceInsight data-testid="profile-setup-form">
        <h2 className={surfaceInsightStyles.sectionTitle}>
          {isOnboarding ? "Данные для персонального дня" : "Личная карта"}
        </h2>
        <p className={surfaceInsightStyles.sectionLead}>
          {isOnboarding
            ? "Минимум полей — максимум пользы в Today. Фамилия необязательна."
            : "Сначала сохраняем ключевые данные. Потом строим натальную карту, число пути и личную навигацию по главным сферам жизни."}
        </p>

        {currentBuildState ? (
          <div style={{ marginTop: "0.9rem", display: "grid", gap: "0.8rem", border: "1px solid rgba(201, 168, 115, 0.26)", background: "linear-gradient(180deg, rgba(255,252,246,0.96) 0%, rgba(255,255,255,0.94) 100%)", borderRadius: "18px", padding: "0.95rem 1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.8rem" }}>
              <LoadingSpinner size="sm" />
              <div>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#ab8750", textTransform: "uppercase", letterSpacing: "0.08em" }}>{currentBuildState.eyebrow}</p>
                <p className="orbit-body-sm" style={{ margin: "0.2rem 0 0", color: "#334155", fontWeight: 700 }}>{currentBuildState.title}</p>
              </div>
            </div>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#5f4930", lineHeight: 1.65 }}>{currentBuildState.description}</p>
            <div style={{ display: "grid", gap: "0.45rem" }}>
              {currentBuildState.steps.map((step, index) => (
                <div
                  key={step}
                  style={{
                    borderRadius: "999px",
                    padding: "0.46rem 0.7rem",
                    border: "1px solid rgba(201, 168, 115, 0.24)",
                    background: buildStage === "done" || index === 0 ? "rgba(232, 203, 150, 0.18)" : "rgba(255,255,255,0.88)",
                    color: "#5f4323",
                  }}
                >
                  <span className="orbit-body-xs" style={{ fontWeight: 700 }}>{step}</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}

        {showCompletionState ? (
          <div style={{ marginTop: "0.9rem", display: "grid", gap: "0.9rem" }}>
            <div style={{ borderRadius: "18px", padding: "1rem", background: "rgba(236, 253, 245, 0.92)", border: "1px solid rgba(52, 211, 153, 0.24)" }}>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#166534", fontWeight: 700 }}>
                {setupMessage || "Карта собрана. Профиль готов к работе."}
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#166534", lineHeight: 1.6 }}>
                {isOnboarding
                  ? "Основа сохранена. Следующий шаг — короткий выбор фокуса, потом первый персональный Today."
                  : "Данные уже сохранены. Теперь можно перейти к готовой карте, открыть Today или при необходимости сразу вернуться к редактированию данных."}
              </p>
            </div>

            <div style={{ display: "grid", gap: "0.7rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
              <SetupStatCard label="Имя" value={setupForm.first_name || "—"} hint="Это имя станет точкой входа для персональных подсказок." />
              <SetupStatCard
                label="Текст «ты»"
                value={
                  setupForm.gender === "female"
                    ? "Женский род"
                    : setupForm.gender === "male"
                      ? "Мужской род"
                      : "Нейтрально"
                }
                hint="Согласование формулировок в интерфейсе."
              />
              <SetupStatCard label="Дата рождения" value={setupForm.birth_date || "—"} hint="На ней держатся знак, дома, карта и числовой слой." />
              <SetupStatCard
                label="Точность времени"
                value={setupForm.time_unknown ? "Без времени" : setupForm.birth_time || "Время добавлено"}
                hint={setupForm.time_unknown ? "Профиль уже работает, но дома и углы могут быть менее точными." : "Точное время помогает удержать дома и оси без размывания."}
              />
              <SetupStatCard
                label="Город"
                value={setupForm.location_name || "—"}
                hint={hasResolvedBirthplace ? "Город подтвержден через поиск и сохранен с координатами." : "Название сохранено, но координаты еще можно уточнить."}
              />
            </div>

            <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
              <button type="button" className="orbit-button orbit-button-primary" onClick={onFinishSetupFlow}>
                {isOnboarding ? "Дальше" : "Перейти к карте"}
              </button>
              {!isOnboarding ? (
                <Link href="/today" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                  Открыть Today
                </Link>
              ) : null}
              <button type="button" className="orbit-button orbit-button-secondary" onClick={onReopenSetupForm}>
                Изменить данные
              </button>
            </div>
          </div>
        ) : (
        <form onSubmit={onSubmit} className="orbit-form" style={{ marginTop: "0.9rem" }}>
          <div style={{ display: "grid", gap: "0.85rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
            <label>
              Имя *
              <input type="text" value={setupForm.first_name} onChange={(e) => onFieldChange("first_name", e.target.value)} required disabled={isBuilding} />
            </label>
            {!isOnboarding ? (
              <label>
                Фамилия <span style={{ fontWeight: 500, color: "#8a7a66" }}>(необязательно)</span>
                <input type="text" value={setupForm.last_name || ""} onChange={(e) => onFieldChange("last_name", e.target.value)} disabled={isBuilding} />
              </label>
            ) : null}
            {!isOnboarding ? (
              <label>
                Название профиля
                <input type="text" value={setupForm.label} onChange={(e) => onFieldChange("label", e.target.value)} placeholder="Я" disabled={isBuilding} />
              </label>
            ) : null}
            <label>
              Обращение в тексте на «ты»
              <select value={setupForm.gender || "unspecified"} onChange={(e) => onFieldChange("gender", e.target.value)} disabled={isBuilding}>
                <option value="unspecified">Нейтральные формулировки</option>
                <option value="female">Женский род</option>
                <option value="male">Мужской род</option>
              </select>
              <span className="orbit-body-xs" style={{ display: "block", marginTop: "0.35rem", color: "#64748b", lineHeight: 1.55 }}>
                Нужно для естественного русского текста. Можно сменить позже в настройках аккаунта.
              </span>
            </label>
            <label>
              Дата рождения *
              <input type="date" value={setupForm.birth_date} onChange={(e) => onFieldChange("birth_date", e.target.value)} required disabled={isBuilding} />
            </label>
            <div style={{ border: "1px solid rgba(201, 168, 115, 0.22)", borderRadius: "16px", padding: "0.85rem 0.9rem", background: "rgba(255,252,246,0.86)", color: "#5f4930" }}>
              <p className="orbit-body-xs" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.08em", color: "#ab8750" }}>Зачем нужно время</p>
              <p className="orbit-body-xs" style={{ margin: "0.38rem 0 0", lineHeight: 1.6 }}>
                Точное время помогает правильно построить дома карты и сделать профиль заметно точнее в темах отношений, карьеры и жизненных периодов.
              </p>
            </div>
            {!setupForm.time_unknown ? (
              <label>
                Время рождения
                <input type="time" value={setupForm.birth_time || ""} onChange={(e) => onFieldChange("birth_time", e.target.value)} disabled={isBuilding} />
                <span className="orbit-body-xs" style={{ display: "block", marginTop: "0.35rem", color: "#64748b", lineHeight: 1.55 }}>
                  Если знаешь время примерно, лучше указать хотя бы его, чем оставлять поле пустым.
                </span>
              </label>
            ) : (
              <div style={{ display: "flex", alignItems: "center", border: "1px dashed rgba(143,119,86,0.3)", borderRadius: "16px", padding: "0.9rem", color: "#6b7280", fontSize: "0.9rem" }}>
                Профиль можно собрать и без времени. Просто часть карты будет менее точной, и это нормально для первого входа.
              </div>
            )}
            <label style={{ display: "flex", alignItems: "center", gap: "0.6rem", alignSelf: "end" }}>
              <input type="checkbox" checked={setupForm.time_unknown} onChange={(e) => onFieldChange("time_unknown", e.target.checked)} disabled={isBuilding} />
              <span className="orbit-body-sm">Время рождения неизвестно</span>
            </label>
          </div>

          <label style={{ marginTop: "0.85rem" }}>
            Место рождения *
            <CityAutocompleteInput
              value={setupForm.location_name}
              onChange={(value) => {
                onFieldChange("location_name", value);
                onFieldChange("latitude", null);
                onFieldChange("longitude", null);
              }}
              onSelect={onLocationSelect}
              placeholder="Город, страна"
              required
              disabled={isBuilding}
            />
          </label>
          <div style={{ marginTop: "0.55rem", borderRadius: "16px", padding: "0.8rem 0.9rem", background: hasResolvedBirthplace ? "rgba(236, 253, 245, 0.9)" : "rgba(255,252,246,0.86)", border: hasResolvedBirthplace ? "1px solid rgba(52, 211, 153, 0.28)" : "1px solid rgba(201, 168, 115, 0.2)" }}>
            <p className="orbit-body-sm" style={{ margin: 0, color: hasResolvedBirthplace ? "#166534" : "#5f4930", fontWeight: 700 }}>
              {hasResolvedBirthplace ? "Город найден и координаты сохранены" : "Выбери город из подсказок"}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.28rem 0 0", color: hasResolvedBirthplace ? "#166534" : "#64748b", lineHeight: 1.55 }}>
              {hasResolvedBirthplace
                ? "Это поможет точнее построить карту и не потерять место рождения из-за разницы в написании."
                : "Лучше выбирать вариант из выпадающего списка. Так координаты сохранятся корректно, а карта будет точнее."}
            </p>
          </div>

          <div style={{ marginTop: "0.95rem", display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
            <button type="submit" className="orbit-button orbit-button-primary" disabled={isBuilding}>
              {isBuilding ? "Собираем карту..." : isOnboarding ? "Сохранить и продолжить" : "Построить карту жизни"}
            </button>
            {!isOnboarding ? (
              <Link href="/today" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                Пока открыть Today
              </Link>
            ) : null}
          </div>

          {setupError ? <p className="orbit-error" style={{ margin: "0.8rem 0 0" }}>{setupError}</p> : null}
          {setupMessage ? (
            <div style={{ marginTop: "0.8rem", borderRadius: "18px", padding: "0.9rem", background: "rgba(236, 253, 245, 0.92)", border: "1px solid rgba(52, 211, 153, 0.24)" }}>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#166534", fontWeight: 700 }}>{setupMessage}</p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#166534", lineHeight: 1.55 }}>
                Теперь не нужно возвращаться в форму. Следующий правильный шаг — открыть день или перейти в полную карту личности.
              </p>
              <div style={{ marginTop: "0.7rem", display: "flex", gap: "0.55rem", flexWrap: "wrap" }}>
                <Link href="/today" className="orbit-button orbit-button-primary orbit-button-sm" style={{ textDecoration: "none" }}>Открыть Today</Link>
                <Link href={PROFILE_CHART_DEEP_PATH} className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>Открыть карту</Link>
              </div>
            </div>
          ) : null}
        </form>
        )}
      </SurfaceInsight>

      <SurfaceInsight data-testid="profile-setup-preview">
        <h2 className={surfaceInsightStyles.sectionTitle}>Что появится после сборки</h2>
        <div style={{ marginTop: "0.9rem", display: "grid", gap: "0.7rem" }}>
          <SetupStatCard label="Карта жизни" value="Дома и главные сферы" hint="Где отношения, дом, реализация и деньги складываются в одну картину." />
          <SetupStatCard label="Число пути" value="Личное число пути" hint="Используется в «Я сегодня», прогнозах и общем жизненном тоне." />
          <SetupStatCard label="Маршруты" value="Я сегодня, Таро, Совместимость" hint="Все основные экраны начинают работать как единый личный маршрут." />
        </div>
      </SurfaceInsight>
    </div>
  );
}
