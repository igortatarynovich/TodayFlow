"use client";

import { DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";
import { useState } from "react";
import { postJson } from "@/lib/api";

type NumerologyNumber = {
  title: string;
  value: number;
  reduced_value: number;
  is_master: boolean;
  summary: string;
};

type NumerologyProfile = {
  name: string;
  birth_date: string;
  life_path: NumerologyNumber;
  expression: NumerologyNumber;
  soul_urge: NumerologyNumber;
  personality: NumerologyNumber;
};

export default function NumerologyNameNumberPage() {
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<NumerologyProfile | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !birthDate) return;
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const profile = await postJson<NumerologyProfile>("/numerology/name", {
        full_name: fullName.trim(),
        birth_date: birthDate,
      });
      setResult(profile);
    } catch (err: any) {
      console.error("Failed to calculate numerology profile", err);
      setError(err?.message || "Не удалось рассчитать профиль");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <ProductPageScreen
        testId="numerology-name-number-page"
        title="Нумерология имени"
        loading
        loadingLabel="Рассчитываем…"
      />
    );
  }

  if (result) {
    return (
      <ProductPageScreen
        testId="numerology-name-number-page"
        title="Нумерология имени"
        subtitle={`${result.name} • ${new Date(result.birth_date).toLocaleDateString("ru-RU")}`}
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
            <div style={{ display: "grid", gap: "var(--orbit-space-md)", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
              <NumerologyCard title="Число имени" number={result.expression.value || result.expression.reduced_value} summary={result.expression.summary} />
              <NumerologyCard title="Путь" number={result.life_path.value || result.life_path.reduced_value} summary={result.life_path.summary} />
              <NumerologyCard title="Душа" number={result.soul_urge.value || result.soul_urge.reduced_value} summary={result.soul_urge.summary} />
              <NumerologyCard title="Личность" number={result.personality.value || result.personality.reduced_value} summary={result.personality.summary} />
            </div>
            <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap" }}>
              <DsButton variant="secondary" onClick={() => setResult(null)}>
                Рассчитать заново
              </DsButton>
              <DsButton href="/today?slot=morning">Применить в Today</DsButton>
              <DsButton href={PROFILE_CHART_DEEP_PATH} variant="secondary">
                К натальной карте
              </DsButton>
            </div>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="numerology-name-number-page"
      title="Нумерология имени"
      subtitle="Базовый профиль: число имени, путь, душа и личность. Это ядро нумерологии пользователя."
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
          <form onSubmit={handleSubmit} className={pl.panel}>
            <div className={pl.formStack}>
              <div className={pl.fieldRow}>
                <label className={pl.fieldLabel} htmlFor="numerology-full-name">
                  Полное имя
                </label>
                <input
                  id="numerology-full-name"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Имя Фамилия"
                  required
                  className={pl.fieldInput}
                />
              </div>
              <div className={pl.fieldRow}>
                <label className={pl.fieldLabel} htmlFor="numerology-birth-date">
                  Дата рождения
                </label>
                <input
                  id="numerology-birth-date"
                  type="date"
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                  required
                  className={pl.fieldInput}
                />
              </div>
              {error && (
                <p className="orbit-body-sm" style={{ margin: 0, color: "#b91c1c" }}>
                  {error}
                </p>
              )}
              <DsButton type="submit">Рассчитать профиль</DsButton>
            </div>
          </form>
    </ProductPageScreen>
  );
}

function NumerologyCard({ title, number, summary }: { title: string; number: number; summary: string }) {
  return (
    <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)", background: "#FAF9F7", textAlign: "center" }}>
      <p className="orbit-body-sm" style={{ margin: 0, color: "#64748b" }}>{title}</p>
      <p className="orbit-display-sm" style={{ margin: "0.3rem 0 0.4rem", color: "#0f172a" }}>{number}</p>
      <p className="orbit-body-xs" style={{ margin: 0, color: "#475569", lineHeight: 1.55 }}>{summary}</p>
    </div>
  );
}
