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

export default function NumerologyLifePathPage() {
  const { isAuthenticated } = useAuth();
  const [birthDate, setBirthDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NumerologyCalcResult | null>(null);
  const [savedKeys, setSavedKeys] = useState<Set<string>>(new Set());
  const [toggleLoading, setToggleLoading] = useState(false);

  const key = result ? `life_path:${result.input?.birth_date ?? ""}` : "";

  useEffect(() => {
    if (!isAuthenticated || !result) return;
    const load = async () => {
      try {
        const res = await getJson<{ saved: { calc_type: string; key: string }[] }>("/library/calculations");
        setSavedKeys(new Set((res?.saved ?? []).map((s) => s.key)));
      } catch {
        setSavedKeys(new Set());
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, result?.input?.birth_date]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!birthDate) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await postJson<NumerologyCalcResult>("/numerology/life-path", { birth_date: birthDate });
      setResult(data);
    } catch (err) {
      console.error("Failed to calculate life path", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSave = async () => {
    if (!result || toggleLoading || !isAuthenticated) return;
    setToggleLoading(true);
    try {
      const payload = {
        calc_type: "life_path",
        key: `life_path:${result.input?.birth_date}`,
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
    setBirthDate("");
  };

  if (result) {
    const num = result.output?.number ?? 0;
    const steps = result.output?.steps ?? [];
    const isSaved = key && savedKeys.has(key);

    return (
      <ProductPageScreen
        testId="numerology-life-path-page"
        title="Число жизненного пути"
        hideHeader
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section style={{ padding: "var(--orbit-space-4xl) var(--orbit-space-xl) var(--orbit-space-2xl)", textAlign: "center" }}>
          <div style={{ maxWidth: "640px", margin: "0 auto" }}>
            <h1 className="orbit-display" style={{ fontSize: "clamp(2rem, 4vw, 3rem)", marginBottom: "var(--orbit-space-md)", color: "#0f172a", fontWeight: 500 }}>
              Число жизненного пути
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
                Другая дата
              </button>
              <Link href="/profile?focus=numerology" className="orbit-button orbit-button-primary" style={{ textDecoration: "none" }}>
                Открыть внутри профиля
              </Link>
            </div>
          </div>
        </section>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="numerology-life-path-page"
      title="Число жизненного пути"
      subtitle="Быстрый вход в numerology-слой профиля. Само число важно не отдельно, а как часть личной карты."
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section style={{ padding: "0 var(--orbit-space-xl) var(--orbit-space-4xl)" }}>
        <div style={{ maxWidth: "600px", margin: "0 auto" }}>
          <form onSubmit={handleSubmit} className="orbit-card" style={{ padding: "var(--orbit-space-xl)" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-lg)" }}>
              <div>
                <label className="orbit-body" style={{ display: "block", marginBottom: "var(--orbit-space-sm)", fontWeight: 500 }}>Дата рождения</label>
                <input
                  type="date"
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                  required
                  style={{ width: "100%", padding: "var(--orbit-space-md)", border: "1px solid var(--orbit-color-border)", borderRadius: "var(--orbit-radius-md)", fontSize: "1rem" }}
                />
              </div>
              <button type="submit" className="orbit-button orbit-button-primary" disabled={loading} style={{ padding: "var(--orbit-space-lg) var(--orbit-space-2xl)" }}>
                {loading ? "Рассчитываю…" : "Рассчитать"}
              </button>
            </div>
          </form>
          <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)", marginTop: "var(--orbit-space-xl)", background: "rgba(255,255,255,0.9)" }}>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.7 }}>
              После расчета число пути лучше читать в{" "}
              <Link href="/profile?focus=numerology" style={{ color: "var(--orbit-color-primary)" }}>
                профиле
              </Link>
              , где оно соединяется с знаком, ритмом и жизненными сферами, а не спорит с ними как отдельный сервис.
            </p>
          </div>
          <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-xl)", textAlign: "center" }}>
            Также: <Link href="/numerology/birthday-number" style={{ color: "var(--orbit-color-primary)" }}>Число дня рождения</Link>
            {" · "}
            <Link href="/numerology/year-number" style={{ color: "var(--orbit-color-primary)" }}>Личный год</Link>
          </p>
        </div>
      </section>
    </ProductPageScreen>
  );
}
