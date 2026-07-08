"use client";

import { useState, useEffect } from "react";
import { getJson } from "@/lib/api";
import { t } from "@/lib/i18n";
import { LoadingSpinner } from "@/components/orbit";

type TransitInsight = {
  transiting_planet: string;
  natal_planet: string;
  aspect: string;
  strength: string;
  tension_level: string;
  area: string;
  feeling: string;
  psychological_description: string;
  recommendations: string[];
};

type TransitPeriod = {
  start_date: string;
  end_date: string;
  intensity: string;
  description: string;
  themes: string[];
};

type DailyForecast = {
  date: string;
  transits: any[];
  tensions: any[];
  resources: any[];
  psychological_insights: TransitInsight[];
  conscious_actions: string[];
  intensity_score: number;
};

type WeeklyBackgroundForecast = {
  week_start: string;
  week_end: string;
  background_text: string;
  direction: string;
  key_transits: any[];
  intensity_score: number;
};

// TransitTimeline will calculate periods from DailyForecast[] based on intensity_score

interface TransitTimelineProps {
  astroProfileId?: number;
  forecastType?: "daily" | "weekly" | "monthly";
  days?: number;
}

export function TransitTimeline({ astroProfileId, forecastType = "weekly", days = 30 }: TransitTimelineProps) {
  const [forecasts, setForecasts] = useState<DailyForecast[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadForecast();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [forecastType, days, astroProfileId]);

  async function loadForecast() {
    try {
      setLoading(true);
      setError(null);

      // Don't try to load if no astroProfileId
      if (!astroProfileId) {
        console.warn("TransitTimeline: No astroProfileId provided, skipping load");
        setLoading(false);
        return;
      }

      let endpoint = "";
      if (forecastType === "daily") {
        endpoint = "/reports/daily-forecast";
      } else if (forecastType === "weekly") {
        // Для TransitTimeline используем старый endpoint (детальный) для визуализации
        // Недельный фон (weekly-background) используется только для текстового отображения
        endpoint = "/reports/weekly-forecast";
      } else if (forecastType === "monthly") {
        endpoint = "/reports/monthly-forecast";
      }

      const params = new URLSearchParams();
      if (astroProfileId) {
        params.set("astro_profile_id", String(astroProfileId));
      }

      console.log("TransitTimeline: Loading forecast from:", `${endpoint}?${params.toString()}`);
      
      const data = await getJson<DailyForecast | DailyForecast[] | WeeklyBackgroundForecast>(`${endpoint}?${params.toString()}`);
      
      // Обработка разных форматов ответа
      let forecastList: DailyForecast[] = [];
      
      if (Array.isArray(data)) {
        // Массив DailyForecast (старый формат weekly-forecast)
        forecastList = data as DailyForecast[];
      } else if (data && typeof data === 'object') {
        // Проверяем, это WeeklyBackgroundForecast или DailyForecast
        if ('week_start' in data && 'background_text' in data) {
          // WeeklyBackgroundForecast - конвертируем в формат для визуализации
          const weekly = data as WeeklyBackgroundForecast;
          // Создаем один DailyForecast для недели на основе фона
          forecastList = [{
            date: weekly.week_start,
            transits: weekly.key_transits || [],
            tensions: [],
            resources: [],
            psychological_insights: [],
            conscious_actions: [],
            intensity_score: weekly.intensity_score,
          }];
        } else if ('date' in data) {
          // Одиночный DailyForecast
          forecastList = [data as DailyForecast];
        }
      }
      
      console.log("TransitTimeline: Loaded forecasts:", {
        count: forecastList.length,
        first: forecastList[0],
      });
      
      setForecasts(forecastList);
    } catch (err: any) {
      console.error("TransitTimeline: Error loading forecast:", err);
      // Show user-friendly error
      if (err.status === 404) {
        setError("Forecast data not available. Please ensure your birth chart is set up.");
      } else if (err.status === 403) {
        setError("Forecast access requires a paid subscription.");
      } else {
        setError(err.message || "Failed to load forecast");
      }
    } finally {
      setLoading(false);
    }
  }

  // Calculate periods from forecasts based on intensity_score
  const calculatePeriods = (): TransitPeriod[] => {
    if (forecasts.length === 0) return [];

    const periods: TransitPeriod[] = [];
    const threshold = 0.5; // Intensity threshold for "high" periods
    let currentPeriodStart: string | null = null;
    let currentPeriodEnd: string | null = null;
    let currentIntensity: "high" | "low" | null = null;

    for (let i = 0; i < forecasts.length; i++) {
      const forecast = forecasts[i];
      const intensity = forecast.intensity_score || 0;
      const isHigh = intensity >= threshold;

      if (currentIntensity === null) {
        // Start new period
        currentPeriodStart = forecast.date;
        currentPeriodEnd = forecast.date;
        currentIntensity = isHigh ? "high" : "low";
      } else if ((isHigh && currentIntensity === "high") || (!isHigh && currentIntensity === "low")) {
        // Continue current period
        currentPeriodEnd = forecast.date;
      } else {
        // End current period, start new one
        if (currentPeriodStart && currentPeriodEnd) {
          periods.push({
            start_date: currentPeriodStart,
            end_date: currentPeriodEnd,
            intensity: currentIntensity,
            description: currentIntensity === "high" ? "High intensity period" : "Low intensity period",
            themes: [],
          });
        }
        currentPeriodStart = forecast.date;
        currentPeriodEnd = forecast.date;
        currentIntensity = isHigh ? "high" : "low";
      }
    }

    // Add final period
    if (currentPeriodStart && currentPeriodEnd && currentIntensity) {
      periods.push({
        start_date: currentPeriodStart,
        end_date: currentPeriodEnd,
        intensity: currentIntensity,
        description: currentIntensity === "high" ? "High intensity period" : "Low intensity period",
        themes: [],
      });
    }

    return periods;
  };

  const periods = calculatePeriods();
  const peaks = periods.filter(p => p.intensity === "high");

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: "var(--orbit-space-xl)" }}>
        <LoadingSpinner size="md" />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "var(--orbit-space-lg)", textAlign: "center", color: "var(--orbit-color-text-secondary)" }}>
        <p>{error}</p>
      </div>
    );
  }

  if (!forecasts || forecasts.length === 0) {
    return (
      <div style={{ padding: "var(--orbit-space-lg)", textAlign: "center", color: "var(--orbit-color-text-secondary)" }}>
        <p>{t("natalChart.forecasts.noData", "No forecast data available")}</p>
      </div>
    );
  }

  // Calculate timeline dimensions
  const timelineWidth = 100; // percentage
  const timelineHeight = 200; // pixels
  const minDate = new Date(forecasts[0]?.date || Date.now());
  const maxDate = new Date(forecasts[forecasts.length - 1]?.date || Date.now());
  const totalDays = Math.ceil((maxDate.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;

  // Calculate position on timeline
  const getDatePosition = (dateStr: string) => {
    const date = new Date(dateStr);
    const daysFromStart = Math.ceil((date.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24));
    return (daysFromStart / totalDays) * 100;
  };

  return (
    <div style={{ marginTop: "var(--orbit-space-lg)" }}>
      <h3 style={{ fontSize: "var(--orbit-font-size-lg)", fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
        {t("natalChart.forecasts.timeline", "Transit Timeline")}
      </h3>

      {/* Timeline visualization */}
      <div style={{ 
        position: "relative", 
        width: "100%", 
        height: `${timelineHeight}px`,
        background: "var(--orbit-color-bg-secondary)",
        borderRadius: "var(--orbit-border-radius-md)",
        padding: "var(--orbit-space-md)",
        marginBottom: "var(--orbit-space-lg)"
      }}>
        {/* Timeline axis */}
        <div style={{
          position: "absolute",
          bottom: "40px",
          left: "var(--orbit-space-md)",
          right: "var(--orbit-space-md)",
          height: "2px",
          background: "var(--orbit-color-border)",
        }} />

        {/* Date labels */}
        <div style={{
          position: "absolute",
          bottom: "10px",
          left: "var(--orbit-space-md)",
          right: "var(--orbit-space-md)",
          display: "flex",
          justifyContent: "space-between",
          fontSize: "var(--orbit-font-size-xs)",
          color: "var(--orbit-color-text-secondary)"
        }}>
          <span>{minDate.toLocaleDateString("en-US", { month: "short", day: "numeric" })}</span>
          <span>{maxDate.toLocaleDateString("en-US", { month: "short", day: "numeric" })}</span>
        </div>

        {/* Intensity bars for each day */}
        {forecasts.map((dayForecast, idx) => {
          const position = getDatePosition(dayForecast.date);
          const intensity = dayForecast.intensity_score || 0;
          const barHeight = intensity * 100; // Scale to 0-100px
          const isPeak = peaks.some(p => {
            const peakStart = new Date(p.start_date);
            const peakEnd = new Date(p.end_date);
            const dayDate = new Date(dayForecast.date);
            return dayDate >= peakStart && dayDate <= peakEnd;
          });

          return (
            <div
              key={idx}
              style={{
                position: "absolute",
                left: `${position}%`,
                bottom: "40px",
                width: "2px",
                height: `${barHeight}px`,
                background: isPeak 
                  ? "var(--orbit-color-primary)" 
                  : intensity > 0.5 
                    ? "var(--orbit-color-warning)" 
                    : "var(--orbit-color-border)",
                borderRadius: "1px",
                transform: "translateX(-50%)",
                transition: "all 0.2s"
              }}
              title={`${dayForecast.date}: Intensity ${Math.round(intensity * 100)}%`}
            />
          );
        })}

        {/* Period markers */}
        {periods.map((period, idx) => {
          const startPos = getDatePosition(period.start_date);
          const endPos = getDatePosition(period.end_date);
          const width = endPos - startPos;

          return (
            <div
              key={`period-${idx}`}
              style={{
                position: "absolute",
                left: `${startPos}%`,
                bottom: "120px",
                width: `${width}%`,
                height: "20px",
                background: period.intensity === "high" 
                  ? "rgba(184, 115, 51, 0.2)" 
                  : "rgba(212, 197, 176, 0.1)",
                border: `1px solid ${period.intensity === "high" ? "#b87333" : "#d4c5b0"}`,
                borderRadius: "var(--orbit-border-radius-sm)",
                display: "flex",
                alignItems: "center",
                padding: "0 var(--orbit-space-xs)",
                fontSize: "var(--orbit-font-size-xs)"
              }}
              title={period.description}
            >
              <span style={{ 
                overflow: "hidden", 
                textOverflow: "ellipsis", 
                whiteSpace: "nowrap",
                color: "var(--orbit-color-text-secondary)"
              }}>
                {period.description}
              </span>
            </div>
          );
        })}
      </div>

      {/* Periods list */}
      {periods.length > 0 && (
        <div style={{ marginTop: "var(--orbit-space-lg)" }}>
          <h4 style={{ fontSize: "var(--orbit-font-size-base)", fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
            {t("natalChart.forecasts.periods", "Key Periods")}
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-sm)" }}>
            {periods.map((period, idx) => (
              <div 
                key={idx}
                style={{
                  padding: "var(--orbit-space-md)",
                  background: "var(--orbit-color-bg-secondary)",
                  borderRadius: "var(--orbit-border-radius-sm)",
                  borderLeft: `3px solid ${period.intensity === "high" ? "var(--orbit-color-primary)" : "var(--orbit-color-border)"}`
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)", fontSize: "var(--orbit-font-size-sm)" }}>
                  {new Date(period.start_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })} - {new Date(period.end_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                </div>
                <div style={{ fontSize: "var(--orbit-font-size-sm)", color: "var(--orbit-color-text-secondary)", marginBottom: "var(--orbit-space-xs)" }}>
                  {period.description}
                </div>
                {period.themes && period.themes.length > 0 && (
                  <div style={{ fontSize: "var(--orbit-font-size-xs)", color: "var(--orbit-color-text-secondary)" }}>
                    {period.themes.join(" • ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Peaks */}
      {peaks.length > 0 && (
        <div style={{ marginTop: "var(--orbit-space-lg)" }}>
          <h4 style={{ fontSize: "var(--orbit-font-size-base)", fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
            {t("natalChart.forecasts.peaks", "Peak Intensity Periods")}
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-sm)" }}>
            {peaks.map((peak, idx) => (
              <div 
                key={idx}
                style={{
                  padding: "var(--orbit-space-md)",
                  background: "linear-gradient(135deg, rgba(184, 115, 51, 0.1) 0%, rgba(184, 115, 51, 0.05) 100%)",
                  borderRadius: "var(--orbit-border-radius-sm)",
                  borderLeft: "3px solid #b87333"
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)", fontSize: "var(--orbit-font-size-sm)", color: "var(--orbit-color-primary)" }}>
                  {new Date(peak.start_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })} - {new Date(peak.end_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                </div>
                <div style={{ fontSize: "var(--orbit-font-size-sm)", color: "var(--orbit-color-text-secondary)" }}>
                  {peak.description}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

