"use client";

import { useState } from "react";
import { useAuth } from "@/lib/useAuth";
import { LoadingSpinner } from "@/components/orbit";
import { postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";

type ForecastGenerationRequest = {
  forecast_type: string;
  date: string;
  locale: string;
  layers: string[];
  context?: string;
  params?: { trigger?: string; emotion?: string; reaction?: string };
  style?: { length?: number; structure?: string };
};

type GeneratedForecast = {
  theme: string;
  what_you_may_notice: string[];
  practical_scene: string[];
  micro_action: string;
  markers: { body: string[]; social: string[]; domestic: string[]; micro_action: string[] };
  tags: string[];
  quality: { score: number; violations: string[]; ok: boolean };
};

const FORECAST_TYPES = [
  { value: "daily_grounded", label: "Daily Grounded" },
  { value: "workday_focus", label: "Workday/Focus" },
  { value: "relationships_interaction", label: "Relationships/Interaction" },
  { value: "body_state", label: "Body/State" },
  { value: "decision_choice", label: "Decision/Choice" },
  { value: "money_resources", label: "Money/Resources" },
];

const LAYERS = ["L1", "L2", "L3", "L4", "L5"];
const CONTEXTS = [
  { value: "work", label: "Работа" },
  { value: "relationship", label: "Отношения" },
  { value: "money", label: "Деньги" },
  { value: "body", label: "Тело" },
];

export default function GenerateForecastPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [generating, setGenerating] = useState(false);
  const [forecast, setForecast] = useState<GeneratedForecast | null>(null);
  const [forecastType, setForecastType] = useState("daily_grounded");
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [layers, setLayers] = useState<string[]>(["L1", "L2"]);
  const [context, setContext] = useState<string>("");
  const [trigger, setTrigger] = useState<string>("");
  const [emotion, setEmotion] = useState<string>("");
  const [reaction, setReaction] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleGenerate = async () => {
    if (!isAuthenticated) {
      toast.error("Войдите, чтобы генерировать прогнозы");
      return;
    }
    try {
      setGenerating(true);
      setForecast(null);
      const request: ForecastGenerationRequest = {
        forecast_type: forecastType,
        date,
        locale: "ru",
        layers,
        context: context || undefined,
        params: (trigger || emotion || reaction) ? { trigger: trigger || undefined, emotion: emotion || undefined, reaction: reaction || undefined } : undefined,
      };
      const result = await postJson<GeneratedForecast>("/generate/forecast", request);
      setForecast(result);
    } catch (err) {
      console.error("Error generating forecast:", err);
      toast.error("Ошибка при генерации прогноза");
    } finally {
      setGenerating(false);
    }
  };

  const toggleLayer = (layer: string) => {
    setLayers(prev => prev.includes(layer) ? prev.filter(l => l !== layer) : [...prev, layer]);
  };

  const handleRegenerate = async () => {
    await handleGenerate();
  };

  const handleSave = async () => {
    if (!forecast) return;
    try {
      setSaving(true);
      const forecastData = {
        date,
        locale: "ru",
        blocks: {
          theme: forecast.theme,
          notice: forecast.what_you_may_notice,
          scene: forecast.practical_scene,
          micro_action: forecast.micro_action,
        },
        markers: forecast.markers,
        tags: forecast.tags,
        published: false,
      };
      await postJson("/admin/forecasts", forecastData);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      console.error("Error saving forecast:", err);
      const errorMessage = err?.response?.data?.detail || err?.message || "Ошибка при сохранении прогноза";
      if (errorMessage.includes("admin") || errorMessage.includes("403") || errorMessage.includes("Forbidden")) {
        toast.error("Для сохранения прогнозов требуются права администратора. Обратитесь к администратору.");
      } else {
        toast.error(`Ошибка при сохранении прогноза: ${errorMessage}`);
      }
    } finally {
      setSaving(false);
    }
  };

  if (authLoading) {
    return (
      <main className="orbit-page">
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "50vh" }}>
          <LoadingSpinner size="lg" />
        </div>
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="orbit-page">
        <div style={{ padding: "2rem", textAlign: "center" }}>
          <p>Войдите, чтобы генерировать прогнозы</p>
        </div>
      </main>
    );
  }

  return (
    <main className="orbit-page">
      <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "2rem" }}>
        <h1 style={{ fontSize: "2rem", marginBottom: "2rem" }}>Генерация прогноза</h1>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
          <div style={{ background: "#f9f9f9", padding: "2rem", borderRadius: "8px" }}>
            <h2 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>Параметры генерации</h2>
            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Тип прогноза</label>
              <select value={forecastType} onChange={(e) => setForecastType(e.target.value)} style={{ padding: "0.75rem", fontSize: "1rem", border: "1px solid #ddd", borderRadius: "4px", width: "100%" }}>
                {FORECAST_TYPES.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Дата</label>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} style={{ padding: "0.75rem", fontSize: "1rem", border: "1px solid #ddd", borderRadius: "4px", width: "100%" }} />
            </div>
            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Слои объяснения</label>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                {LAYERS.map((layer) => (
                  <label key={layer} style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer", padding: "0.5rem 1rem", background: layers.includes(layer) ? "#667eea" : "#fff", color: layers.includes(layer) ? "white" : "#333", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <input type="checkbox" checked={layers.includes(layer)} onChange={() => toggleLayer(layer)} style={{ width: "18px", height: "18px" }} />
                    {layer}
                  </label>
                ))}
              </div>
            </div>
            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Контекст (опционально)</label>
              <select value={context} onChange={(e) => setContext(e.target.value)} style={{ padding: "0.75rem", fontSize: "1rem", border: "1px solid #ddd", borderRadius: "4px", width: "100%" }}>
                <option value="">Не выбран</option>
                {CONTEXTS.map((ctx) => <option key={ctx.value} value={ctx.value}>{ctx.label}</option>)}
              </select>
            </div>
            <button onClick={handleGenerate} disabled={generating || layers.length === 0} style={{ padding: "0.75rem 2rem", fontSize: "1rem", background: "#667eea", color: "white", border: "none", borderRadius: "4px", cursor: generating || layers.length === 0 ? "not-allowed" : "pointer", opacity: generating || layers.length === 0 ? 0.6 : 1, width: "100%" }}>
              {generating ? "Генерация..." : "Сгенерировать прогноз"}
            </button>
          </div>
          <div>
            {generating ? (
              <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "400px" }}>
                <LoadingSpinner size="lg" />
              </div>
            ) : forecast ? (
              <div style={{ background: "#fff", padding: "2rem", borderRadius: "8px", border: "1px solid #ddd" }}>
                <div style={{ marginBottom: "1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
                  <h2 style={{ fontSize: "1.5rem", margin: 0 }}>Сгенерированный прогноз</h2>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                    <span style={{ padding: "0.25rem 0.75rem", background: forecast.quality.ok ? "#4caf50" : "#ff9800", color: "white", borderRadius: "4px", fontSize: "0.9rem" }}>
                      {forecast.quality.ok ? "✓ OK" : `⚠ ${forecast.quality.violations.length} ошибок`}
                    </span>
                    <button
                      onClick={handleRegenerate}
                      disabled={generating}
                      style={{
                        padding: "0.5rem 1rem",
                        fontSize: "0.9rem",
                        background: "#6c757d",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: generating ? "not-allowed" : "pointer",
                        opacity: generating ? 0.6 : 1,
                      }}
                    >
                      Перегенерировать
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={saving || saved}
                      title="Сохранить прогноз в админку (требуются права администратора)"
                      style={{
                        padding: "0.5rem 1rem",
                        fontSize: "0.9rem",
                        background: saved ? "#4caf50" : "#667eea",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: saving || saved ? "not-allowed" : "pointer",
                        opacity: saving || saved ? 0.6 : 1,
                      }}
                    >
                      {saving ? "Сохранение..." : saved ? "✓ Сохранено" : "Сохранить"}
                    </button>
                  </div>
                </div>
                <div style={{ marginBottom: "1.5rem" }}>
                  <h3 style={{ fontSize: "1.2rem", marginBottom: "0.5rem", fontWeight: "600" }}>Тема</h3>
                  <p style={{ lineHeight: "1.6", color: "#333" }}>{forecast.theme}</p>
                </div>
                <div style={{ marginBottom: "1.5rem" }}>
                  <h3 style={{ fontSize: "1.2rem", marginBottom: "0.5rem", fontWeight: "600" }}>Что ты можешь заметить</h3>
                  <ul style={{ paddingLeft: "1.5rem", lineHeight: "1.6", color: "#333" }}>
                    {forecast.what_you_may_notice.map((item, i) => <li key={i} style={{ marginBottom: "0.5rem" }}>{item}</li>)}
                  </ul>
                </div>
                <div style={{ marginBottom: "1.5rem" }}>
                  <h3 style={{ fontSize: "1.2rem", marginBottom: "0.5rem", fontWeight: "600" }}>Практическая сцена</h3>
                  <ul style={{ paddingLeft: "1.5rem", lineHeight: "1.6", color: "#333" }}>
                    {forecast.practical_scene.map((item, i) => <li key={i} style={{ marginBottom: "0.5rem" }}>{item}</li>)}
                  </ul>
                </div>
                <div style={{ marginBottom: "1.5rem" }}>
                  <h3 style={{ fontSize: "1.2rem", marginBottom: "0.5rem", fontWeight: "600" }}>Микро-действие</h3>
                  <p style={{ lineHeight: "1.6", color: "#333" }}>{forecast.micro_action}</p>
                </div>
                {forecast.quality.violations.length > 0 && (
                  <div style={{ marginTop: "1.5rem", padding: "1rem", background: "#fff3cd", borderRadius: "4px", border: "1px solid #ffc107" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                      <strong style={{ color: "#856404", fontSize: "1rem" }}>⚠ Ошибки валидации Quality Gate ({forecast.quality.violations.length}):</strong>
                    </div>
                    <ul style={{ marginTop: "0.5rem", paddingLeft: "1.5rem", marginBottom: 0 }}>
                      {forecast.quality.violations.map((v, i) => (
                        <li key={i} style={{ fontSize: "0.9rem", color: "#856404", marginBottom: "0.25rem", lineHeight: "1.4" }}>
                          {v}
                        </li>
                      ))}
                    </ul>
                    <div style={{ marginTop: "0.75rem", padding: "0.5rem", background: "#fff", borderRadius: "4px", fontSize: "0.85rem", color: "#856404" }}>
                      <strong>Примечание:</strong> Прогноз сгенерирован, но не прошёл полную валидацию. Рекомендуется перегенерировать или исправить вручную.
                    </div>
                  </div>
                )}
                {forecast.quality.ok && (
                  <div style={{ marginTop: "1.5rem", padding: "1rem", background: "#d4edda", borderRadius: "4px", border: "1px solid #28a745" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span style={{ fontSize: "1.2rem" }}>✓</span>
                      <strong style={{ color: "#155724", fontSize: "0.95rem" }}>Прогноз прошёл валидацию Quality Gate</strong>
                    </div>
                    <div style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "#155724" }}>
                      Все проверки пройдены: структура (4 блока), маркеры, стоп-слова, теги.
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ background: "#f9f9f9", padding: "3rem", borderRadius: "8px", textAlign: "center", color: "#666" }}>
                <p>Заполните параметры и нажмите &quot;Сгенерировать прогноз&quot;</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
