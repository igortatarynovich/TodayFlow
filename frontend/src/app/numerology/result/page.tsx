"use client";

import Link from "next/link";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { useSearchParams } from "next/navigation";
import { useState, useEffect, Suspense } from "react";
import { getJson, postJson } from "@/lib/api";

type NumerologyResult = {
  type: "life-path" | "birthday-number" | "name" | "day" | "year";
  number: number;
  is_master: boolean;
  interpretation: string;
  data: {
    birth_date?: string;
    birth_day?: number;
    birth_month?: number;
    full_name?: string;
    date?: string;
    year?: number;
  };
};

function normalizeNumerologyType(type: string | null): NumerologyResult["type"] | null {
  if (!type) return null;
  const normalized = type.trim().toLowerCase();
  if (normalized === "life-path" || normalized === "life_path") return "life-path";
  if (normalized === "birthday-number" || normalized === "birthday_number") return "birthday-number";
  if (normalized === "name" || normalized === "name-number" || normalized === "name_number") return "name";
  if (normalized === "day" || normalized === "day-number" || normalized === "day_number") return "day";
  if (normalized === "year" || normalized === "year-number" || normalized === "year_number" || normalized === "personal_year" || normalized === "personal-year") return "year";
  return null;
}

function NumerologyResultContent() {
  const searchParams = useSearchParams();
  const rawType = searchParams?.get("type") || null;
  const type = normalizeNumerologyType(rawType);
  const numberParam = searchParams?.get("number");
  
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<NumerologyResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [shareCopied, setShareCopied] = useState(false);

  useEffect(() => {
    if (!type || !numberParam) {
      setError("Не указаны параметры");
      setLoading(false);
      return;
    }

    const loadResult = async () => {
      try {
        const num = parseInt(numberParam, 10);
        if (type === "life-path") {
          const birthDate = searchParams?.get("date");
          if (!birthDate) throw new Error("Нужна дата рождения");
          const response = await postJson<any>("/numerology/life-path", { birth_date: birthDate });
          const number = response?.output?.number ?? num;
          setResult({
            type: "life-path",
            number,
            is_master: !!response?.is_master,
            interpretation: `Число пути: ${number}. ${response?.output?.steps?.length ? "Используй его как опору для ежедневных решений." : "Это твоя базовая линия развития."}`,
            data: { birth_date: birthDate },
          });
        } else if (type === "birthday-number") {
          const birthDay = Number(searchParams?.get("birth_day") || searchParams?.get("day"));
          if (!birthDay) throw new Error("Нужен день рождения");
          const response = await postJson<any>("/numerology/birthday-number", { birth_day: birthDay });
          const number = response?.output?.number ?? num;
          setResult({
            type: "birthday-number",
            number,
            is_master: !!response?.is_master,
            interpretation: `Число дня рождения: ${number}. Это врожденный стиль твоего самопроявления и естественный способ входить в контакт с миром.`,
            data: { birth_day: birthDay },
          });
        } else if (type === "name") {
          const fullName = searchParams?.get("name");
          const birthDate = searchParams?.get("date");
          if (!fullName || !birthDate) throw new Error("Нужны имя и дата рождения");
          const response = await postJson<any>("/numerology/name", { full_name: fullName, birth_date: birthDate });
          const number = response?.expression?.value || response?.expression?.reduced_value || num;
          setResult({
            type: "name",
            number,
            is_master: !!response?.expression?.is_master,
            interpretation: response?.expression?.summary || `Число имени: ${number}`,
            data: { full_name: fullName, birth_date: birthDate },
          });
        } else if (type === "day") {
          const response = await getJson<any>("/numerology/daily");
          const number = response?.number?.value || response?.number?.reduced_value || num;
          setResult({
            type: "day",
            number,
            is_master: !!response?.number?.is_master,
            interpretation: response?.number?.summary || `Число дня: ${number}`,
            data: { date: response?.date || searchParams?.get("date") || undefined },
          });
        } else if (type === "year") {
          const birthDay = Number(searchParams?.get("birth_day"));
          const birthMonth = Number(searchParams?.get("birth_month"));
          const year = Number(searchParams?.get("year") || new Date().getFullYear());
          if (!birthDay || !birthMonth) throw new Error("Нужны день и месяц рождения");
          const response = await postJson<any>("/numerology/personal-year", { birth_day: birthDay, birth_month: birthMonth, year });
          const number = response?.output?.number ?? num;
          setResult({
            type: "year",
            number,
            is_master: !!response?.is_master,
            interpretation: `Личный год ${year}: число ${number}.`,
            data: { birth_day: birthDay, birth_month: birthMonth, year },
          });
        } else {
          throw new Error("Неизвестный тип расчета");
        }
        setLoading(false);
      } catch (err) {
        console.error("Failed to load result", err);
        setError("Не удалось загрузить результат");
        setLoading(false);
      }
    };

    loadResult();
  }, [type, numberParam, searchParams]);

  const handleShare = async () => {
    const url = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Результат нумерологии",
          text: `Число ${result?.number}`,
          url: url,
        });
      } catch (err) {
        // Пользователь отменил шаринг
      }
    } else {
      await navigator.clipboard.writeText(url);
      setShareCopied(true);
      window.setTimeout(() => setShareCopied(false), 1600);
    }
  };

  if (loading) {
    return (
      <ProductPageScreen testId="numerology-result-page" title="Результат" loading loadingLabel="Загрузка…" />
    );
  }

  if (error || !result) {
    return (
      <ProductPageScreen testId="numerology-result-page" title="Результат" contentClassName={`${pl.content} ${pl.legacyHost}`}>
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <h1 className="orbit-display-sm">{error || "Результат не найден"}</h1>
          <Link href="/numerology/life-path" className={pl.textLink}>
            Вернуться к нумерологии
          </Link>
        </section>
      </ProductPageScreen>
    );
  }

  const typeNames: Record<string, string> = {
    "life-path": "Число жизненного пути",
    "birthday-number": "Число дня рождения",
    "name": "Число имени",
    "day": "Число дня",
    "year": "Число года"
  };

  return (
    <ProductPageScreen
      testId="numerology-result-page"
      title={typeNames[result.type] || "Результат"}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section style={{
        paddingTop: "var(--orbit-space-2xl)",
        paddingBottom: "var(--orbit-space-4xl)",
        background: "#ffffff"
      }}>
        <div style={{
          maxWidth: "600px",
          margin: "0 auto",
          padding: "0 var(--orbit-space-xl)"
        }}>
          <div className="orbit-card" style={{
            padding: "var(--orbit-space-xl)",
            background: "#FAF9F7",
            textAlign: "center"
          }}>
            <div style={{
              fontSize: "5rem",
              fontWeight: 600,
              color: "#0f172a",
              marginBottom: "var(--orbit-space-md)",
              lineHeight: 1
            }}>
              {result.number}
              {result.is_master && <span style={{ fontSize: "2rem", verticalAlign: "super" }}>★</span>}
            </div>
            {result.is_master && (
              <p className="orbit-body-sm" style={{
                color: "#64748b",
                marginBottom: "var(--orbit-space-lg)"
              }}>
                Мастер-число
              </p>
            )}
            <p className="orbit-body" style={{
              fontSize: "1.125rem",
              lineHeight: 1.7,
              color: "#334155",
              margin: 0
            }}>
              {result.interpretation}
            </p>
          </div>

          {/* Share button */}
          <div style={{ textAlign: "center", marginTop: "var(--orbit-space-xl)" }}>
            <button
              onClick={handleShare}
              className="orbit-button orbit-button-secondary"
              style={{
                fontSize: "1rem",
                padding: "var(--orbit-space-md) var(--orbit-space-xl)"
              }}
            >
              Поделиться результатом
            </button>
            {shareCopied && (
              <p className="orbit-body-xs" style={{ marginTop: "0.5rem", color: "#64748b" }}>
                Ссылка скопирована
              </p>
            )}
          </div>
        </div>
      </section>

      {/* CTA: Continue in app */}
      <section style={{
        paddingTop: "var(--orbit-space-4xl)",
        paddingBottom: "var(--orbit-space-4xl)",
        background: "#FAF9F7",
        textAlign: "center"
      }}>
        <div style={{
          maxWidth: "600px",
          margin: "0 auto",
          padding: "0 var(--orbit-space-xl)"
        }}>
          <p className="orbit-body" style={{
            fontSize: "1.25rem",
            lineHeight: 1.7,
            marginBottom: "var(--orbit-space-xl)",
            color: "#334155"
          }}>
            Дальше это число полезно читать не отдельно, а внутри общей карты профиля.
          </p>
          <Link
            href="/profile?focus=numerology"
            className="orbit-button orbit-button-primary"
            style={{
              fontSize: "1.125rem",
              padding: "var(--orbit-space-lg) var(--orbit-space-2xl)",
              textDecoration: "none",
              display: "inline-block"
            }}
          >
            Открыть внутри профиля
          </Link>
        </div>
      </section>
    </ProductPageScreen>
  );
}

export default function NumerologyResultPage() {
  return (
    <Suspense fallback={
      <ProductPageScreen testId="numerology-result-page" title="Результат" loading loadingLabel="Загрузка…" />
    }>
      <NumerologyResultContent />
    </Suspense>
  );
}
