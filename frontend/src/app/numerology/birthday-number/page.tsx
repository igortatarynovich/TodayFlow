"use client";

import Link from "next/link";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { useState, useEffect } from "react";
import { postJson, getJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";

type CalcStep = { expression: string; sum: number };
type NumerologyCalcResult = {
  calc_type: string;
  input: Record<string, unknown>;
  output: { number: number; steps: CalcStep[] };
  is_master: boolean;
  master_numbers: number[];
};

const CALC_VERSION = "v1";

export default function BirthdayNumberPage() {
  const { isAuthenticated } = useAuth();
  const [birthDay, setBirthDay] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NumerologyCalcResult | null>(null);
  const [savedKeys, setSavedKeys] = useState<Set<string>>(new Set());
  const [toggleLoading, setToggleLoading] = useState(false);

  const key = result ? `birthday_number:${result.input?.birth_day ?? ""}` : "";

  useEffect(() => {
    if (!isAuthenticated || !result) return;
    const load = async () => {
      try {
        const res = await getJson<{ saved: { key: string }[] }>("/library/calculations");
        setSavedKeys(new Set((res?.saved ?? []).map((s) => s.key)));
      } catch {
        setSavedKeys(new Set());
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, result?.input?.birth_day]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const data = await postJson<NumerologyCalcResult>("/numerology/birthday-number", { birth_day: birthDay });
      setResult(data);
    } catch (err) {
      console.error("Failed to calculate birthday number", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSave = async () => {
    if (!result || toggleLoading || !isAuthenticated) return;
    setToggleLoading(true);
    try {
      const payload = {
        calc_type: "birthday_number",
        key: `birthday_number:${result.input?.birth_day}`,
        payload: { input: result.input, output: result.output, version: CALC_VERSION },
      };
      const res = await postJson<{ saved: { key: string }[] }>("/library/calculations/toggle", payload);
      setSavedKeys(new Set((res?.saved ?? []).map((s) => s.key)));
    } catch (e) {
      console.error("Toggle save failed", e);
    } finally {
      setToggleLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
  };

  if (result) {
    const num = result.output?.number ?? 0;
    const steps = result.output?.steps ?? [];
    const isSaved = key && savedKeys.has(key);

    return (
      <ProductPageScreen
        testId="numerology-birthday-number-page"
        title="Число дня рождения"
        hideHeader
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section style={{ padding: "var(--orbit-space-4xl) var(--orbit-space-xl) var(--orbit-space-2xl)", textAlign: "center" }}>
          <div style={{ maxWidth: "640px", margin: "0 auto" }}>
            <h1 className="orbit-display" style={{ fontSize: "clamp(2rem, 4vw, 3rem)", marginBottom: "var(--orbit-space-md)", color: "#0f172a", fontWeight: 500 }}>
              Число дня рождения
            </h1>
          </div>
        </section>
        <section style={{ padding: "0 var(--orbit-space-xl) var(--orbit-space-4xl)" }}>
          <div style={{ maxWidth: "600px", margin: "0 auto" }}>
            <div className="orbit-card" style={{ padding: "var(--orbit-space-xl)", background: "#fff", marginBottom: "var(--orbit-space-xl)" }}>
              <div style={{ fontSize: "4rem", fontWeight: 600, color: "#0f172a", marginBottom: "var(--orbit-space-sm)", lineHeight: 1 }}>
                {num}
                {result.is_master && <span style={{ fontSize: "1.5rem", verticalAlign: "super" }}> ★</span>}
              </div>
              {result.is_master && (
                <p className="orbit-body-sm" style={{ color: "#64748b", marginBottom: "var(--orbit-space-md)" }}>Мастер-число</p>
              )}
              {steps.length > 0 && (
                <div style={{ textAlign: "left", marginTop: "var(--orbit-space-lg)" }}>
                  <p className="orbit-body-sm" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)" }}>Шаги расчёта</p>
                  <ol style={{ margin: 0, paddingLeft: "1.25rem" }}>
                    {steps.map((s, i) => (
                      <li key={i} className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                        {s.expression} = {s.sum}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-md)", justifyContent: "center" }}>
              {isAuthenticated ? (
                <button
                  type="button"
                  className={isSaved ? "orbit-button orbit-button-primary" : "orbit-button orbit-button-secondary"}
                  onClick={handleToggleSave}
                  disabled={toggleLoading}
                >
                  {isSaved ? "Сохранено" : "Сохранить"}
                </button>
              ) : (
                <Link href="/auth" className="orbit-button orbit-button-primary" style={{ textDecoration: "none" }}>
                  Войти, чтобы сохранить
                </Link>
              )}
              <button type="button" className="orbit-button orbit-button-secondary" onClick={handleReset}>
                Другой день
              </button>
              <Link href="/numerology/life-path" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                К нумерологии
              </Link>
            </div>
          </div>
        </section>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="numerology-birthday-number-page"
      title="Число дня рождения"
      subtitle="День месяца рождения (1–31) → редукция, мастер-числа 11, 22, 33"
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section style={{ padding: "0 var(--orbit-space-xl) var(--orbit-space-4xl)" }}>
        <div style={{ maxWidth: "600px", margin: "0 auto" }}>
          <form onSubmit={handleSubmit} className="orbit-card" style={{ padding: "var(--orbit-space-xl)" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-lg)" }}>
              <div>
                <label className="orbit-body" style={{ display: "block", marginBottom: "var(--orbit-space-sm)", fontWeight: 500 }}>День рождения (1–31)</label>
                <input
                  type="number"
                  min={1}
                  max={31}
                  value={birthDay}
                  onChange={(e) => setBirthDay(Math.max(1, Math.min(31, parseInt(e.target.value, 10) || 1)))}
                  required
                  style={{ width: "100%", padding: "var(--orbit-space-md)", border: "1px solid var(--orbit-color-border)", borderRadius: "var(--orbit-radius-md)", fontSize: "1rem" }}
                />
              </div>
              <button type="submit" className="orbit-button orbit-button-primary" disabled={loading} style={{ padding: "var(--orbit-space-lg) var(--orbit-space-2xl)" }}>
                {loading ? "Рассчитываю…" : "Рассчитать"}
              </button>
            </div>
          </form>
        </div>
      </section>
    </ProductPageScreen>
  );
}
