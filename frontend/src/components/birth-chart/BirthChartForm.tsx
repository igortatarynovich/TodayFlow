"use client";

import { t } from "@/lib/i18n";

import { FormEvent } from "react";
import { LoadingSpinner } from "@/components/orbit";
import { POPULAR_CITIES } from "@/data/cities";
import type { GeocodeResult } from "@/lib/types";

interface BirthChartFormProps {
  form: {
    date: string;
    time: string;
    timeUnknown: boolean;
    location: string;
    fullName: string;
  };
  loading: boolean;
  error: string | null;
  geocodeResult: GeocodeResult | null;
  onDateChange: (value: string) => void;
  onTimeChange: (value: string) => void;
  onTimeUnknownChange: (checked: boolean) => void;
  onLocationChange: (value: string) => void;
  onFullNameChange: (value: string) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => Promise<void> | void;
}

export function BirthChartForm({
  form,
  loading,
  error,
  onDateChange,
  onTimeChange,
  onTimeUnknownChange,
  onLocationChange,
  onFullNameChange,
  onSubmit,
}: BirthChartFormProps) {
  return (
    <form onSubmit={onSubmit} className="orbit-birth-chart-form">
      <div className="orbit-birth-chart-input-fields">
        <label className="orbit-birth-chart-input-label">
          {t("birthChart.form.title", "ДАТА / ВРЕМЯ / МЕСТО РОЖДЕНИЯ")}
        </label>
        <p className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)", lineHeight: 1.5 }}>
          {t("birthChart.form.description", "Для точного расчета укажите дату, место и время рождения (если известно). Время можно оставить неизвестным — расчет будет выполнен на полдень.")}
        </p>
        <div className="orbit-birth-chart-input-grid">
          <div className="orbit-birth-chart-input-wrapper">
            <svg width={20} height={20} className="orbit-birth-chart-input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            <input
              type="date"
              value={form.date}
              onChange={(e) => onDateChange(e.target.value)}
              className="orbit-birth-chart-input"
              required
            />
          </div>
          {!form.timeUnknown && (
            <div className="orbit-birth-chart-input-wrapper">
              <svg width={20} height={20} className="orbit-birth-chart-input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <input
                type="time"
                value={form.time}
                onChange={(e) => onTimeChange(e.target.value)}
                className="orbit-birth-chart-input"
              />
            </div>
          )}
          <label className="orbit-birth-chart-checkbox">
            <input
              type="checkbox"
              checked={form.timeUnknown}
              onChange={(e) => onTimeUnknownChange(e.target.checked)}
            />
            <span>{t("birthChart.form.timeUnknown", "Время неизвестно")}</span>
          </label>
          <div className="orbit-birth-chart-input-wrapper">
            <svg width={20} height={20} className="orbit-birth-chart-input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="10" r="3"/>
              <path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 7 8 11.7z"/>
            </svg>
            <input
              type="text"
              value={form.location}
              onChange={(e) => onLocationChange(e.target.value)}
              placeholder={t("birthChart.form.placeOfBirth", "Место рождения")}
              className="orbit-birth-chart-input"
              list="cities"
              required
            />
          </div>
          <datalist id="cities">
            {POPULAR_CITIES.map((city) => (
              <option key={city.name} value={city.name} />
            ))}
          </datalist>
          <div className="orbit-birth-chart-input-wrapper">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="orbit-birth-chart-input-icon">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <input
              type="text"
              value={form.fullName}
              onChange={(e) => onFullNameChange(e.target.value)}
              placeholder={t("birthChart.fullName", "Полное имя (для нумерологии)")}
              className="orbit-birth-chart-input"
            />
          </div>
        </div>
      </div>
      
      {error && (
        <p className="orbit-error" style={{ 
          marginTop: "var(--orbit-space-md)",
          color: "var(--orbit-color-lock)",
          fontSize: "var(--orbit-text-body-sm)"
        }}>
          {error}
        </p>
      )}
      
      <button
        type="submit"
        disabled={loading}
        className="orbit-birth-chart-calculate-button"
        style={{ 
          width: "100%",
          marginTop: "var(--orbit-space-lg)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "var(--orbit-space-sm)"
        }}
      >
        {loading ? (
          <>
            <LoadingSpinner size="sm" />
            <span>{t("birthChart.form.calculating", "Рассчитываем...")}</span>
          </>
        ) : (
          t("birthChart.form.calculate", "Рассчитать")
        )}
      </button>
    </form>
  );
}

