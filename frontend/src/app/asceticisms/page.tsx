"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { useAuth } from "@/lib/useAuth";
import { getJson } from "@/lib/api";

type Asceticism = {
  id: string;
  title: string;
  description: string;
  goal?: string;
  direction?: string;
};

type GoalCategory = {
  id: string;
  name: string;
  description: string;
  asceticisms: Asceticism[];
};

export default function AsceticismsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState<"goal" | "select" | "track">("goal");
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null);
  const [customGoal, setCustomGoal] = useState("");
  const [asceticisms, setAsceticisms] = useState<Asceticism[]>([]);
  const [filteredAsceticisms, setFilteredAsceticisms] = useState<Asceticism[]>([]);
  const [selectedAsceticism, setSelectedAsceticism] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const goalCategories: GoalCategory[] = [
    {
      id: "focus",
      name: "Фокус и концентрация",
      description: "Помогает убрать отвлечения и сфокусироваться на важном",
      asceticisms: [],
    },
    {
      id: "energy",
      name: "Энергия и активность",
      description: "Повышает уровень энергии и мотивации",
      asceticisms: [],
    },
    {
      id: "calm",
      name: "Спокойствие и баланс",
      description: "Помогает снизить тревожность и найти внутренний баланс",
      asceticisms: [],
    },
    {
      id: "discipline",
      name: "Дисциплина и контроль",
      description: "Укрепляет самоконтроль и дисциплину",
      asceticisms: [],
    },
    {
      id: "connection",
      name: "Связь с собой",
      description: "Помогает лучше понимать себя и свои потребности",
      asceticisms: [],
    },
  ];

  useEffect(() => {
    if (!isAuthenticated) return;
    void loadAsceticisms();
  }, [isAuthenticated]);

  const loadAsceticisms = async () => {
    try {
      setLoading(true);
      const data = await getJson<Asceticism[]>("/practices/asceticisms");
      setAsceticisms(data);
    } catch (err) {
      console.error("Error loading asceticisms:", err);
      setError("Не удалось загрузить аскезы");
    } finally {
      setLoading(false);
    }
  };

  const handleGoalSelect = (goalId: string) => {
    setSelectedGoal(goalId);
    const category = goalCategories.find((c) => c.id === goalId);
    if (category) {
      const filtered = asceticisms.filter((a) => {
        const desc = a.description?.toLowerCase() || "";
        const title = a.title?.toLowerCase() || "";
        const goalKeywords: Record<string, string[]> = {
          focus: ["фокус", "концентрация", "отвлечение", "внимание", "соцсети"],
          energy: ["энергия", "активность", "мотивация", "движение", "усталость"],
          calm: ["спокойствие", "баланс", "тревога", "стресс", "расслабление"],
          discipline: ["дисциплина", "контроль", "самоконтроль", "сила воли"],
          connection: ["связь", "понимание", "осознанность", "себя", "потребности"],
        };
        const keywords = goalKeywords[goalId] || [];
        return keywords.some((keyword) => desc.includes(keyword) || title.includes(keyword));
      });
      setFilteredAsceticisms(filtered.length > 0 ? filtered : asceticisms.slice(0, 5));
    } else {
      setFilteredAsceticisms(asceticisms.slice(0, 5));
    }
    setStep("select");
  };

  const handleCustomGoal = () => {
    if (customGoal.trim()) {
      setSelectedGoal("custom");
      setFilteredAsceticisms(asceticisms.slice(0, 5));
      setStep("select");
    }
  };

  const handleAsceticismSelect = (id: string) => {
    setSelectedAsceticism(id);
    setStep("track");
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="asceticisms-page"
        title="Аскезы"
        loading
        loadingLabel="Загрузка каталога…"
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="asceticisms-page"
        title="Аскезы"
        guest={{
          message: "Войдите, чтобы использовать аскезы",
          ctaHref: "/auth?redirect=/asceticisms",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  if (error) {
    return (
      <ProductPageScreen
        testId="asceticisms-page"
        title="Аскезы"
        contentClassName={pl.content}
      >
        <div className={pl.panel}>
          <DsBody size="sm">{error}</DsBody>
        </div>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="asceticisms-page"
      title="Аскезы"
      subtitle="Осознанные ограничения для подтверждения контроля. Выбери цель, и мы подберём аскезу, которая поможет её достичь."
      contentClassName={pl.content}
    >
      {step === "goal" ? (
        <>
          <h2 className={v2.sectionTitle}>Какую цель ты хочешь достичь?</h2>
          <div className={pl.modeGrid}>
            {goalCategories.map((category) => (
              <button
                key={category.id}
                type="button"
                onClick={() => handleGoalSelect(category.id)}
                className={pl.modeCard}
              >
                <p className={pl.modeTitle}>{category.name}</p>
                <p className={pl.modeHint}>{category.description}</p>
              </button>
            ))}
          </div>

          <section className={pl.panel}>
            <h3 className={v2.sectionTitle}>Или опиши свою цель</h3>
            <div className={pl.formStack} style={{ marginTop: "0.75rem" }}>
              <textarea
                value={customGoal}
                onChange={(e) => setCustomGoal(e.target.value)}
                placeholder="Например: хочу лучше спать, хочу больше успевать, хочу чувствовать себя увереннее…"
                className={pl.fieldTextarea}
                rows={4}
              />
              <DsButton onClick={handleCustomGoal} disabled={!customGoal.trim()}>
                Продолжить
              </DsButton>
            </div>
          </section>
        </>
      ) : null}

      {step === "select" ? (
        <>
          <div className={pl.toolbar}>
            <button
              type="button"
              onClick={() => {
                setStep("goal");
                setSelectedGoal(null);
                setCustomGoal("");
              }}
              className={pl.textLink}
              style={{ background: "none", border: "none", cursor: "pointer", padding: 0 }}
            >
              ← Назад
            </button>
            <h2 className={v2.sectionTitle} style={{ margin: 0 }}>
              Выбери аскезу для своей цели
            </h2>
          </div>

          {selectedGoal === "custom" && customGoal ? (
            <div className={pl.panel}>
              <DsBody size="sm" muted>
                Твоя цель:
              </DsBody>
              <DsBody className={`${pl.bodyMtXs} ${pl.bodyItalic}`}>
                &ldquo;{customGoal}&rdquo;
              </DsBody>
            </div>
          ) : null}

          <div className={pl.gridHub}>
            {filteredAsceticisms.map((asceticism) => (
              <button
                key={asceticism.id}
                type="button"
                onClick={() => handleAsceticismSelect(asceticism.id)}
                className={`${pl.hubCard} ${pl.modeCard}`}
                style={{ width: "100%", textAlign: "left" }}
              >
                <p className={pl.modeTitle}>{asceticism.title}</p>
                <p className={pl.modeHint}>{asceticism.description}</p>
              </button>
            ))}
          </div>
        </>
      ) : null}

      {step === "track" && selectedAsceticism ? (
        <>
          <div className={pl.toolbar}>
            <button
              type="button"
              onClick={() => setStep("select")}
              className={pl.textLink}
              style={{ background: "none", border: "none", cursor: "pointer", padding: 0 }}
            >
              ← Назад
            </button>
            <h2 className={v2.sectionTitle} style={{ margin: 0 }}>
              Начни отслеживать аскезу
            </h2>
          </div>

          {(() => {
            const asceticism = asceticisms.find((a) => a.id === selectedAsceticism);
            if (!asceticism) return null;

            return (
              <section className={pl.panel}>
                <h3 className={v2.sectionTitle}>{asceticism.title}</h3>
                <DsBody className={pl.bodyMtLg}>{asceticism.description}</DsBody>
                <div className={pl.panel} style={{ marginTop: "1rem", padding: "1rem" }}>
                  <DsBody size="sm" muted>
                    <strong>Короткий шаг:</strong> Каждый день отмечай аскезу на карте — так складывается
                    история, а не таблица галочек.
                  </DsBody>
                </div>
                <div style={{ marginTop: "1.25rem" }}>
                  <DsButton href={`/asceticisms/tracker?asceticism=${selectedAsceticism}`}>
                    Открыть карту аскез →
                  </DsButton>
                </div>
              </section>
            );
          })()}
        </>
      ) : null}

      <Link href="/maps/ascetic" className={pl.textLink}>
        Карта аскез →
      </Link>
    </ProductPageScreen>
  );
}
