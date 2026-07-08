"use client";

import "./compatibility-premium.css";

import { useEffect, useMemo, useRef, useState, useCallback, type CSSProperties, type ReactNode } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { CompatibilityWebScreen } from "@/components/product-ui/CompatibilityWebScreen";
import {
  CompatibilityWebHub,
  CompatibilityWebHubRail,
  type CompatWebModeId,
} from "@/components/product-ui/CompatibilityWebHub";
import {
  compatibilityWebChromeBundle,
} from "@/components/product-ui/compatibilityWebChrome";
import {
  CompatibilityWebResult,
  CompatibilityWebResultRail,
  potentialLabelFromScore,
} from "@/components/product-ui/CompatibilityWebResult";
import { buildCompatibilityMetaChips } from "@/lib/product-ui/buildCompatibilityMetaChips";
import l from "@/design-system/layouts/dsLayouts.module.css";
import { CompatibilityFunnelSection, type CompatibilityFunnelArtifact } from "@/components/compatibility/CompatibilityFunnelSection";
import { buildExplorationFromPairInput } from "@/lib/buildCompatibilityExplorationModel";
import {
  buildCompatibilityDeepOpenEvent,
  buildCompatibilityScenarioSwitchEvent,
  type CompatibilityLearningMeta,
} from "@/lib/compatibilityEcho";
import { getScenarioSkin, resolveScenarioId } from "@/lib/compatibilityScenarioSkins";
import { LoadingSpinner } from "@/components/orbit";
import { getJson, postJson } from "@/lib/api";
import { inferCompatibilityDefaultsFromJTBD, logActiveJTBDAction } from "@/lib/jtbdFeedback";
import { useToast } from "@/components/ToastProvider";
import { useAuth } from "@/lib/useAuth";
import type { AstroProfile, CompactUserModel, QuestionsHubContextResponse } from "@/lib/types";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { fetchCompactUserModelCached } from "@/lib/compactUserModelCache";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";

type CompatibilityAspect = {
  type: string;
  description: string;
  score: number;
};

type CompatibilityResult = {
  overall_score: number;
  aspects: CompatibilityAspect[];
  synastry?: Record<string, unknown> | null;
  profile_1?: Record<string, unknown> | null;
  profile_2?: Record<string, unknown> | null;
  summary?: string | null;
  relationship_type?: string | null;
  recommendations?: string[];
  editorial?: {
    mode_focus?: string | null;
    pair_thesis?: string | null;
    strengths?: string[];
    tensions?: string[];
    next_step?: string | null;
  } | null;
  deep_dive?: {
    relationship_archetype?: string | null;
    strongest_axis?: string | null;
    tension_axis?: string | null;
    dimensions?: Array<{
      key: string;
      label: string;
      score: number;
      summary: string;
      indicators?: string[];
    }>;
    strengths?: string[];
    challenges?: string[];
    guidance?: string[];
    knowledge?: {
      relationship_mode?: string | null;
      mode_title?: string | null;
      mode_summary?: string | null;
      sign_pair_summary?: string | null;
      elemental_dynamic?: string | null;
      modality_dynamic?: string | null;
      rulers?: string[];
      themes?: string[];
      stones?: string[];
      life_path_pair?: string | null;
    };
  } | null;
};

type ProfilesResponse = {
  profiles: AstroProfile[];
};

type RelationMode = "romantic" | "family" | "parent_child" | "business";

const RELATION_MODE_OPTIONS: Array<{ id: RelationMode; label: string; description: string }> = [
  { id: "romantic", label: "Любовь", description: "Пара" },
  { id: "family", label: "Семья", description: "Дом" },
  { id: "parent_child", label: "Родитель/ребенок", description: "Дети" },
  { id: "business", label: "Работа/бизнес", description: "Команда" },
];

const MODE_COPY: Record<RelationMode, { heroTitle: string; heroDescription: string; compareLabel: string; emptyText: string; essenceTitle: string; nextStepTitle: string }> = {
  romantic: {
    heroTitle: "Связь между вами",
    heroDescription: "",
    compareLabel: "С кем связь",
    emptyText: "Запусти расчёт.",
    essenceTitle: "Между вами",
    nextStepTitle: "Следующий шаг",
  },
  family: {
    heroTitle: "Семейная связь",
    heroDescription: "",
    compareLabel: "С кем из семьи",
    emptyText: "Запусти расчёт.",
    essenceTitle: "В семье",
    nextStepTitle: "Следующий шаг",
  },
  parent_child: {
    heroTitle: "Родитель и ребёнок",
    heroDescription: "",
    compareLabel: "Кто второй в паре",
    emptyText: "Запусти расчёт.",
    essenceTitle: "Эта связь",
    nextStepTitle: "Следующий шаг",
  },
  business: {
    heroTitle: "Рабочая совместимость",
    heroDescription: "",
    compareLabel: "С кем работать",
    emptyText: "Запусти расчёт.",
    essenceTitle: "Ваша связка",
    nextStepTitle: "Следующий шаг",
  },
};

const RESULT_SURFACE_COPY: Record<
  RelationMode,
  {
    strongestTitle: string;
    strongestFallback: string;
    tensionTitle: string;
    tensionFallback: string;
    helpTitle: string;
    helpFallback: string;
    nextTitle: string;
    strengthsListTitle: string;
    challengesListTitle: string;
  }
> = {
  romantic: {
    strongestTitle: "Сильная сторона",
    strongestFallback: "Здесь контакт даётся естественнее.",
    tensionTitle: "Трение",
    tensionFallback: "Здесь чаще всего расходятся ожидания и темп.",
    helpTitle: "Что помогает",
    helpFallback: "Прояснять ожидания и границы заранее.",
    nextTitle: "Дальше",
    strengthsListTitle: "Усиливает связь",
    challengesListTitle: "Риски",
  },
  family: {
    strongestTitle: "Опора",
    strongestFallback: "Здесь семья чувствует поддержку сильнее.",
    tensionTitle: "Напряжение",
    tensionFallback: "Здесь чаще включается старый сценарий.",
    helpTitle: "Что помогает",
    helpFallback: "Договариваться о границах и поддержке прямо.",
    nextTitle: "Дальше",
    strengthsListTitle: "Удерживает",
    challengesListTitle: "Повтор",
  },
  parent_child: {
    strongestTitle: "Где проще",
    strongestFallback: "Здесь контакт безопаснее и ровнее.",
    tensionTitle: "Где сложнее",
    tensionFallback: "Здесь чаще рвётся из‑за темпа или чувствительности.",
    helpTitle: "Что помогает",
    helpFallback: "Опора без давления и ясный ритм.",
    nextTitle: "Дальше",
    strengthsListTitle: "Усиливает",
    challengesListTitle: "Болит сильнее",
  },
  business: {
    strongestTitle: "Сильная сторона",
    strongestFallback: "Здесь роли и темп совпадают лучше.",
    tensionTitle: "Сбой",
    tensionFallback: "Здесь путаются роли и решения.",
    helpTitle: "Что помогает",
    helpFallback: "Зоны ответственности и регулярные сверки.",
    nextTitle: "Дальше",
    strengthsListTitle: "Усиливает связку",
    challengesListTitle: "Слабое место",
  },
};

type CompatibilityLayerCard = {
  id: "dynamics" | "signs" | "birthdates" | "profiles";
  title: string;
  href: string;
  cta: string;
  requiresAuth?: boolean;
};

const COMPATIBILITY_LAYER_CARDS: CompatibilityLayerCard[] = [
  {
    id: "dynamics",
    title: "Разбор динамики",
    href: "/compatibility/analyze",
    cta: "Открыть",
  },
  {
    id: "signs",
    title: "По знакам",
    href: "/compatibility/signs",
    cta: "Открыть",
  },
  {
    id: "birthdates",
    title: "По датам",
    href: "/compatibility/birthdates",
    cta: "Открыть",
  },
  {
    id: "profiles",
    title: "По профилям",
    href: "/compatibility?open=profiles",
    cta: "Открыть",
    requiresAuth: true,
  },
];

function CompatibilityLayerSelector({
  isAuthenticated,
  emphasizeProfiles = false,
}: {
  isAuthenticated: boolean;
  emphasizeProfiles?: boolean;
}) {
  return (
    <section className="compat-desktop-card">
      <p className="compat-hero-eyebrow">С чего начать</p>
      <h2 className="compat-section-title" style={{ margin: "0.35rem 0 0.65rem" }}>
        Входы в совместимость
      </h2>
      <p className="orbit-body-xs compat-desktop-muted" style={{ margin: "0 0 0.85rem", maxWidth: "42rem" }}>
        Десктопный разбор динамики пары, быстрый ориентир по знакам или датам — бесплатно. Полный расчёт — из сохранённых профилей.
      </p>
      <div className="todayflow-layer-grid">
        {COMPATIBILITY_LAYER_CARDS.map((card) => {
          const locked = card.requiresAuth && !isAuthenticated;
          const highlighted = emphasizeProfiles && card.id === "profiles";
          const href = locked ? "/auth?redirect=/compatibility" : card.href;
          return (
            <Link
              key={card.id}
              href={href}
              className="orbit-button orbit-button-secondary orbit-button-sm"
              style={{
                textDecoration: "none",
                borderRadius: "18px",
                border: highlighted ? "2px solid rgba(190, 148, 88, 0.45)" : "1px solid rgba(198, 166, 119, 0.22)",
                background: highlighted
                  ? "linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,248,236,0.92) 100%)"
                  : "rgba(255,255,255,0.9)",
                padding: "0.9rem",
                display: "block",
                textAlign: "left",
                height: "100%",
              }}
            >
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                {card.title}
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: locked ? "#9a6700" : "#7c5a33", fontWeight: 700 }}>
                {locked ? "Войди, чтобы открыть" : card.cta}
              </p>
            </Link>
          );
        })}
      </div>
    </section>
  );
}

function normalizeTypeLabel(type: string) {
  const normalized = type.trim();
  if (!normalized) return "Ключевой слой";
  return normalized;
}

function cleanCompatibilityLine(value: string | null | undefined): string {
  const text = (value || "").trim();
  if (!text) return "";
  return text
    .replace(/\bRelationship Lens\b/gi, "Режим связи")
    .replace(/\bPair Setup\b/gi, "Настройка пары")
    .replace(/\bCore Match\b/gi, "Основа связи")
    .replace(/\bResult\b/gi, "Разбор")
    .replace(/\bQuick layer\b/gi, "Быстрый слой")
    .replace(/\bdeep-mode\b/gi, "глубокого режима")
    .replace(/\bdeep-анализ\b/gi, "глубокий разбор")
    .replace(/\brelationship lens\b/gi, "режим связи")
    .replace(/\s+/g, " ")
    .trim();
}

function dedupeCompatibilityLine(primary: string, secondary: string) {
  const a = cleanCompatibilityLine(primary);
  const b = cleanCompatibilityLine(secondary);
  if (!a) return b;
  if (!b) return a;
  if (a.toLowerCase() === b.toLowerCase()) return a;
  if (a.toLowerCase().includes(b.toLowerCase()) || b.toLowerCase().includes(a.toLowerCase())) return a.length >= b.length ? a : b;
  return a;
}

function buildCompatibilitySummary(score: number) {
  if (score >= 78) return "Сильная связь — контакт даётся легче, опору всё равно нужно поддерживать.";
  if (score >= 58) return "База есть — лучше заранее договариваться о темпе и ожиданиях.";
  return "Непростая связь — важны границы и прямой разговор.";
}

function relationHint(label: string) {
  const normalized = label.toLowerCase();
  if (normalized.includes("я")) return "Твой основной профиль";
  if (normalized.includes("муж") || normalized.includes("жена") || normalized.includes("парт")) return "Партнер и личные отношения";
  if (normalized.includes("реб") || normalized.includes("сын") || normalized.includes("дочь")) return "Ребенок и семейная динамика";
  if (normalized.includes("мама") || normalized.includes("пап")) return "Семья и родовые связи";
  return "Человек из твоего круга";
}

function buildNextStep(score: number, type: "sign" | "full", relationMode: RelationMode) {
  if (type === "sign") {
    return "Для глубины открой полный разбор по профилям.";
  }
  if (relationMode === "business") {
    if (score >= 78) return "Закрепи роли и регулярные сверки.";
    if (score >= 58) return "Разведи зоны ответственности и финальное решение.";
    return "Сначала рамка и роли, не энтузиазм.";
  }
  if (relationMode === "family") {
    if (score >= 78) return "Договорись о границах, не только о тепле.";
    if (score >= 58) return "Назови повторяющийся сценарий и новую реакцию.";
    return "Прямой разговор о границах и поддержке.";
  }
  if (relationMode === "parent_child") {
    if (score >= 78) return "Береги доверие — меньше лишнего контроля.";
    if (score >= 58) return "Подстрой ритм: отклик, дистанция, структура.";
    return "Ищи поддержку, которая снижает напряжение.";
  }
  if (score >= 78) return "Простые правила вместо контроля.";
  if (score >= 58) return "Проясни ожидания и темп заранее.";
  return "Найди трение и лишние ожидания.";
}

function scoreTone(score: number) {
  if (score >= 78) return { label: "Идет легко", accent: "#166534", bg: "rgba(240,253,244,0.95)" };
  if (score >= 58) return { label: "Требует настройки", accent: "#9a6700", bg: "rgba(255,251,235,0.95)" };
  return { label: "Нужна осторожность", accent: "#991b1b", bg: "rgba(254,242,242,0.95)" };
}

function actionFromGuidance(guidance: string[] | undefined, fallback: string) {
  return guidance?.find((item) => item && item.trim().length > 0) || fallback;
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === "string" && item.trim().length > 0);
}

function SynastryReadable({ synastry }: { synastry: Record<string, unknown> }) {
  const summaryRaw = synastry.compatibility_summary;
  const summary = isPlainObject(summaryRaw) ? summaryRaw : null;
  const strong = Array.isArray(synastry.strong_aspects) ? synastry.strong_aspects : [];
  const planets = Array.isArray(synastry.planet_aspects) ? synastry.planet_aspects : [];
  const angles = Array.isArray(synastry.angle_aspects) ? synastry.angle_aspects : [];
  const overlays = Array.isArray(synastry.house_overlays) ? synastry.house_overlays : [];

  const formatPlanetAspect = (raw: unknown) => {
    if (!isPlainObject(raw)) return null;
    const p1 = raw.planet1;
    const p2 = raw.planet2;
    const asp = raw.aspect;
    const orb = raw.orb;
    const strength = raw.strength;
    const desc = raw.description;
    const head =
      typeof p1 === "string" && typeof p2 === "string" && typeof asp === "string"
        ? `${p1} — ${asp} — ${p2}`
        : typeof desc === "string"
          ? desc
          : null;
    if (!head) return null;
    const meta = [typeof orb === "number" ? `орб ${orb.toFixed(1)}°` : null, typeof strength === "string" ? strength : null]
      .filter(Boolean)
      .join(" · ");
    return { head, meta, desc: typeof desc === "string" ? desc : "" };
  };

  const scrollBox: CSSProperties = {
    maxHeight: "280px",
    overflow: "auto",
    display: "grid",
    gap: "0.5rem",
    marginTop: "0.45rem",
    paddingRight: "0.25rem",
  };

  return (
    <div style={{ display: "grid", gap: "0.85rem" }}>
      {summary ? (
        <div
          style={{
            borderRadius: "18px",
            border: "1px solid rgba(198, 166, 119, 0.18)",
            background: "rgba(255,255,255,0.82)",
            padding: "0.95rem",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Синастрия: сводка
          </p>
          {typeof summary.relationship_type === "string" ? (
            <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", fontWeight: 700, color: "#0f172a" }}>
              {summary.relationship_type}
            </p>
          ) : null}
          {stringList(summary.strengths).length ? (
            <div style={{ marginTop: "0.5rem" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49" }}>
                Сильные стороны
              </p>
              <ul style={{ margin: "0.35rem 0 0", paddingLeft: "1.1rem", color: "#475569", lineHeight: 1.65, fontSize: "0.85rem" }}>
                {stringList(summary.strengths).map((t, idx) => (
                  <li key={`s-${idx}`}>{t}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {stringList(summary.triggers).length ? (
            <div style={{ marginTop: "0.5rem" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49" }}>
                Триггеры
              </p>
              <ul style={{ margin: "0.35rem 0 0", paddingLeft: "1.1rem", color: "#475569", lineHeight: 1.65, fontSize: "0.85rem" }}>
                {stringList(summary.triggers).map((t, idx) => (
                  <li key={`tr-${idx}`}>{t}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {stringList(summary.recommendations).length ? (
            <div style={{ marginTop: "0.5rem" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49" }}>
                Рекомендации синастрии
              </p>
              <ul style={{ margin: "0.35rem 0 0", paddingLeft: "1.1rem", color: "#475569", lineHeight: 1.65, fontSize: "0.85rem" }}>
                {stringList(summary.recommendations).map((t, idx) => (
                  <li key={`rec-${idx}`}>{t}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}

      {strong.length ? (
        <div
          style={{
            borderRadius: "18px",
            border: "1px solid rgba(198, 166, 119, 0.18)",
            background: "rgba(255,255,255,0.82)",
            padding: "0.95rem",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Сильные аспекты
          </p>
          <div style={scrollBox}>
            {strong.map((raw, index) => {
              const row = formatPlanetAspect(raw);
              if (!row) return null;
              return (
                <div key={`s-${index}`} style={{ borderRadius: "12px", border: "1px solid rgba(198,166,119,0.14)", padding: "0.65rem 0.75rem" }}>
                  <p className="orbit-body-xs" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                    {row.head}
                  </p>
                  {row.meta ? (
                    <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#8a6f49" }}>
                      {row.meta}
                    </p>
                  ) : null}
                  {row.desc && row.desc !== row.head ? (
                    <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                      {row.desc}
                    </p>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}

      {planets.length ? (
        <div
          style={{
            borderRadius: "18px",
            border: "1px solid rgba(198, 166, 119, 0.18)",
            background: "rgba(255,255,255,0.82)",
            padding: "0.95rem",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Аспекты планет (полный список)
          </p>
          <div style={scrollBox}>
            {planets.map((raw, index) => {
              const row = formatPlanetAspect(raw);
              if (!row) return null;
              return (
                <div key={`p-${index}`} style={{ borderRadius: "12px", border: "1px solid rgba(198,166,119,0.12)", padding: "0.55rem 0.65rem" }}>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#334155", lineHeight: 1.6 }}>
                    <span style={{ fontWeight: 600 }}>{row.head}</span>
                    {row.meta ? <span style={{ color: "#8a6f49" }}> · {row.meta}</span> : null}
                  </p>
                  {row.desc && row.desc !== row.head ? (
                    <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#64748b", lineHeight: 1.6 }}>
                      {row.desc}
                    </p>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}

      {angles.length ? (
        <div
          style={{
            borderRadius: "18px",
            border: "1px solid rgba(198, 166, 119, 0.18)",
            background: "rgba(255,255,255,0.82)",
            padding: "0.95rem",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Аспекты к углам (ASC / MC)
          </p>
          <div style={scrollBox}>
            {angles.map((raw, index) => {
              if (!isPlainObject(raw)) return null;
              const planet = raw.planet;
              const angle = raw.angle;
              const asp = raw.aspect;
              const head =
                typeof planet === "string" && typeof angle === "string" && typeof asp === "string"
                  ? `${planet} ${asp} ${angle}`
                  : typeof raw.description === "string"
                    ? raw.description
                    : null;
              if (!head) return null;
              return (
                <p key={`a-${index}`} className="orbit-body-xs" style={{ margin: 0, color: "#475569", lineHeight: 1.65 }}>
                  {head}
                  {typeof raw.description === "string" && raw.description !== head ? ` — ${raw.description}` : ""}
                </p>
              );
            })}
          </div>
        </div>
      ) : null}

      {overlays.length ? (
        <div
          style={{
            borderRadius: "18px",
            border: "1px solid rgba(198, 166, 119, 0.18)",
            background: "rgba(255,255,255,0.82)",
            padding: "0.95rem",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Заходы планет в дома
          </p>
          <div style={scrollBox}>
            {overlays.map((raw, index) => {
              if (!isPlainObject(raw)) return null;
              const planet = raw.planet;
              const house = raw.house;
              const head =
                typeof planet === "string" && typeof house === "number"
                  ? `${planet} → ${house}-й дом`
                  : typeof raw.description === "string"
                    ? raw.description
                    : null;
              if (!head) return null;
              return (
                <div key={`o-${index}`} style={{ borderRadius: "12px", border: "1px solid rgba(198,166,119,0.12)", padding: "0.55rem 0.65rem" }}>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#334155", fontWeight: 600 }}>
                    {head}
                  </p>
                  {typeof raw.description === "string" && raw.description !== head ? (
                    <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#64748b", lineHeight: 1.6 }}>
                      {raw.description}
                    </p>
                  ) : null}
                  {typeof raw.significance === "string" ? (
                    <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#8a6f49" }}>
                      {raw.significance}
                    </p>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function relationModeToWebMode(relationMode: RelationMode): CompatWebModeId {
  if (relationMode === "business") return "office";
  if (relationMode === "parent_child") return "parenting";
  if (relationMode === "family") return "family";
  return "love";
}

export default function CompatibilityPage() {
  const relationModeTouchedRef = useRef(false);
  const relationModeQueryRef = useRef(false);
  const router = useRouter();
  const toast = useToast();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { trackMeaningEvent } = useMeaningRuntime();
  const compatLocale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const compatChrome = useMemo(() => compatibilityWebChromeBundle(compatLocale), [compatLocale]);

  const [profiles, setProfiles] = useState<AstroProfile[]>([]);
  const [loadingProfiles, setLoadingProfiles] = useState(true);
  const [loadingResult, setLoadingResult] = useState(false);
  const [profile1Id, setProfile1Id] = useState<number | null>(null);
  const [profile2Id, setProfile2Id] = useState<number | null>(null);
  const [compatibilityType, setCompatibilityType] = useState<"sign" | "full">("full");
  const [relationMode, setRelationMode] = useState<RelationMode>("romantic");
  const [result, setResult] = useState<CompatibilityResult | null>(null);
  const [funnelArtifact, setFunnelArtifact] = useState<CompatibilityFunnelArtifact | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [questionsHubContext, setQuestionsHubContext] = useState<QuestionsHubContextResponse | null>(null);
  const [initialQuery, setInitialQuery] = useState<{ profile1: number | null; profile2: number | null }>({
    profile1: null,
    profile2: null,
  });
  const [urlSeries, setUrlSeries] = useState<string | null>(null);
  const [urlTopic, setUrlTopic] = useState<string | null>(null);
  const [scenarioContext, setScenarioContext] = useState<{
    format_id: string;
    display_score: number;
    subscores: Record<string, number>;
    tone_mode?: string | null;
    deep_block_order?: string[] | null;
  } | null>(null);
  const seriesAutoRunRef = useRef<string | null>(null);
  const [compatWebModeId, setCompatWebModeId] = useState<CompatWebModeId>("love");
  const deepOpenTracked = useRef(false);
  const [compactUserModel, setCompactUserModel] = useState<CompactUserModel | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setCompactUserModel(null);
      return;
    }
    void fetchCompactUserModelCached()
      .then((model) => setCompactUserModel(model))
      .catch(() => setCompactUserModel(null));
  }, [isAuthenticated]);

  useEffect(() => {
    getJson<QuestionsHubContextResponse>("/questions/context")
      .then(setQuestionsHubContext)
      .catch((error) => console.error("Failed to load questions context for compatibility", error));
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const queryProfile1 = Number(params.get("profile1") || "");
    const queryProfile2 = Number(params.get("profile2") || "");
    const queryMode = params.get("mode");
    const queryRelationMode = params.get("relation_mode");
    const querySeries = params.get("series");
    const queryTopic = params.get("topic");
    setInitialQuery({
      profile1: Number.isFinite(queryProfile1) && queryProfile1 > 0 ? queryProfile1 : null,
      profile2: Number.isFinite(queryProfile2) && queryProfile2 > 0 ? queryProfile2 : null,
    });
    setUrlSeries(querySeries);
    setUrlTopic(queryTopic);
    if (queryMode === "sign" || queryMode === "full") {
      setCompatibilityType(queryMode);
    }
    if (queryRelationMode === "romantic" || queryRelationMode === "family" || queryRelationMode === "parent_child" || queryRelationMode === "business") {
      relationModeQueryRef.current = true;
      setRelationMode(queryRelationMode);
      return;
    }

    const jtbdDefaults = inferCompatibilityDefaultsFromJTBD();
    if (jtbdDefaults) {
      setRelationMode(jtbdDefaults.relationMode);
      setCompatibilityType(jtbdDefaults.compatibilityType);
    }
  }, []);

  useEffect(() => {
    if (relationModeQueryRef.current || relationModeTouchedRef.current) return;

    const lane = questionsHubContext?.preferred_lane;
    if (lane === "love") {
      setRelationMode("romantic");
      return;
    }
    if (lane === "money_career") {
      setRelationMode("business");
    }
  }, [questionsHubContext?.preferred_lane]);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoadingProfiles(false);
      return;
    }

    const bootstrap = async () => {
      try {
        const data = await getJson<ProfilesResponse>("/account/astro-data");
        const safeProfiles = Array.isArray(data?.profiles) ? data.profiles : [];
        setProfiles(safeProfiles);

        const primary = safeProfiles.find((profile) => profile.is_primary) || safeProfiles[0] || null;
        const secondary =
          safeProfiles.find((profile) => profile.id !== primary?.id) || safeProfiles[1] || null;

        setProfile1Id(
          safeProfiles.some((profile) => profile.id === initialQuery.profile1)
            ? initialQuery.profile1
            : primary?.id ?? null,
        );
        setProfile2Id(
          safeProfiles.some((profile) => profile.id === initialQuery.profile2)
            ? initialQuery.profile2
            : secondary?.id ?? null,
        );
      } catch (err: any) {
        console.error("Error loading profiles:", err);
        setError(err?.message || "Не удалось загрузить профили");
      } finally {
        setLoadingProfiles(false);
      }
    };

    void bootstrap();
  }, [initialQuery.profile1, initialQuery.profile2, isAuthenticated]);

  const selectedProfile1 = useMemo(
    () => profiles.find((profile) => profile.id === profile1Id) || null,
    [profile1Id, profiles],
  );
  const selectedProfile2 = useMemo(
    () => profiles.find((profile) => profile.id === profile2Id) || null,
    [profile2Id, profiles],
  );
  const primaryProfile = useMemo(
    () => profiles.find((profile) => profile.is_primary) || profiles[0] || null,
    [profiles],
  );

  const suggestedPeople = useMemo(
    () => profiles.filter((profile) => profile.id !== profile1Id).slice(0, 4),
    [profile1Id, profiles],
  );
  const strongestAspect = useMemo(() => {
    if (!result?.aspects?.length) return null;
    return [...result.aspects].sort((a, b) => b.score - a.score)[0] || null;
  }, [result]);
  const tensionAspect = useMemo(() => {
    if (!result?.aspects?.length) return null;
    return [...result.aspects].sort((a, b) => a.score - b.score)[0] || null;
  }, [result]);
  const visibleAspects = useMemo(() => {
    if (!result?.aspects?.length) return [];
    const seen = new Set<string>();
    return result.aspects.filter((aspect) => {
      const key = `${aspect.type}|${aspect.description}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    }).slice(0, 4);
  }, [result]);
  const modeCopy = MODE_COPY[relationMode];
  const resultCopy = RESULT_SURFACE_COPY[relationMode];
  const scoreMeta = scoreTone(result?.overall_score || 0);
  const knowledge = result?.deep_dive?.knowledge || null;
  const editorial = result?.editorial || null;
  const editorialStrengths = editorial?.strengths || [];
  const editorialTensions = editorial?.tensions || [];
  const pairScenarioId = useMemo(() => {
    if (urlSeries || urlTopic) {
      return resolveScenarioId({ series: urlSeries, topic: urlTopic });
    }
    if (relationMode === "business") return "office";
    if (relationMode === "parent_child") return "parenting";
    if (relationMode === "family") return "living_together";
    return "love";
  }, [urlSeries, urlTopic, relationMode]);

  const buildPairScenarioHref = useCallback(
    (scenarioId: string) => {
      if (typeof window === "undefined") return `/compatibility?series=${scenarioId}`;
      const nextUrl = new URL(`${window.location.origin}/compatibility`);
      nextUrl.searchParams.set("series", scenarioId);
      if (profile1Id) nextUrl.searchParams.set("profile1", String(profile1Id));
      if (profile2Id) nextUrl.searchParams.set("profile2", String(profile2Id));
      nextUrl.searchParams.set("relation_mode", relationMode);
      nextUrl.searchParams.set("mode", compatibilityType);
      return `${nextUrl.pathname}${nextUrl.search}`;
    },
    [profile1Id, profile2Id, relationMode, compatibilityType],
  );

  const pairExplorationModel = useMemo(() => {
    if (!result || !selectedProfile1 || !selectedProfile2) return null;
    return buildExplorationFromPairInput(
      {
        name1: selectedProfile1.label,
        name2: selectedProfile2.label,
        overallScore: result.overall_score,
        summary: result.summary,
        aspects: result.aspects,
        editorial: result.editorial,
        deepDive: result.deep_dive,
        recommendations: result.recommendations,
      },
      pairScenarioId,
      {
        displayScore: scenarioContext?.display_score ?? result.overall_score,
        scenarioSubscores: scenarioContext?.subscores as Partial<
          Record<"attraction" | "stability" | "conflicts" | "sexuality", number>
        >,
        continuationHref: (id) => buildPairScenarioHref(id),
        deepBlockOrder: scenarioContext?.deep_block_order ?? undefined,
      },
    );
  }, [result, selectedProfile1, selectedProfile2, pairScenarioId, scenarioContext, buildPairScenarioHref]);

  const pairScenarioSkin = useMemo(() => getScenarioSkin(pairScenarioId), [pairScenarioId]);

  const pairLearningMeta = useMemo<CompatibilityLearningMeta>(
    () => ({
      surface: "pair_profiles",
      scenarioId: pairScenarioId,
      formatId: pairScenarioId,
      toneMode: pairScenarioSkin.toneMode,
      score: result?.overall_score ?? null,
      cumFocusTopic: compactUserModel?.current_state?.focus_topic_id ?? null,
    }),
    [pairScenarioId, pairScenarioSkin.toneMode, result?.overall_score, compactUserModel?.current_state?.focus_topic_id],
  );

  const handlePairDeepOpen = () => {
    if (deepOpenTracked.current) return;
    deepOpenTracked.current = true;
    trackMeaningEvent(buildCompatibilityDeepOpenEvent(pairLearningMeta));
  };

  useEffect(() => {
    setCompatWebModeId(relationModeToWebMode(relationMode));
  }, [relationMode]);

  const handleWebModeChange = (modeId: CompatWebModeId) => {
    const mode = compatChrome.modes.find((item) => item.id === modeId);
    if (!mode) return;
    relationModeTouchedRef.current = true;
    setCompatWebModeId(modeId);
    setRelationMode(mode.relationMode);
    setUrlSeries(mode.scenarioId);
    setUrlTopic(null);
    setResult(null);
    setScenarioContext(null);
    setFunnelArtifact(null);
    deepOpenTracked.current = false;
    seriesAutoRunRef.current = null;
  };

  const compatWebShell = (
    content: ReactNode,
    options?: {
      title?: string;
      subtitle?: string;
      railHint?: string;
      rail?: ReactNode;
      hideHeader?: boolean;
      contentClassName?: string;
    },
  ) => (
    <CompatibilityWebScreen
      title={options?.title}
      subtitle={options?.subtitle}
      railHint={options?.railHint}
      rail={options?.rail}
      hideHeader={options?.hideHeader}
      contentClassName={options?.contentClassName}
    >
      {options?.hideHeader ? (
        content
      ) : (
        <div className="compat-desktop-shell compat-desktop-stack" style={{ paddingBottom: "1.5rem" }}>
          {content}
        </div>
      )}
    </CompatibilityWebScreen>
  );

  const strongestDescription = cleanCompatibilityLine(
    strongestAspect?.description || result?.deep_dive?.strengths?.[0] || resultCopy.strongestFallback,
  );
  const tensionDescription = cleanCompatibilityLine(
    tensionAspect?.description || result?.deep_dive?.challenges?.[0] || resultCopy.tensionFallback,
  );
  const nextStepDescription = cleanCompatibilityLine(
    editorial?.next_step || buildNextStep(result?.overall_score ?? 0, compatibilityType, relationMode),
  );
  const extraStrengths = (result?.deep_dive?.strengths || []).filter((item) => {
    const cleaned = cleanCompatibilityLine(item);
    return cleaned && cleaned !== strongestDescription && !editorialStrengths.some((editorialItem) => cleanCompatibilityLine(editorialItem) === cleaned);
  });
  const extraChallenges = (result?.deep_dive?.challenges || []).filter((item) => {
    const cleaned = cleanCompatibilityLine(item);
    return cleaned && cleaned !== tensionDescription && !editorialTensions.some((editorialItem) => cleanCompatibilityLine(editorialItem) === cleaned);
  });
  const runCompatibility = async (formatOverride?: string) => {
    if (!profile1Id || !profile2Id || profile1Id === profile2Id) {
      setError("Выбери два разных профиля");
      return;
    }

    const activeFormatId = formatOverride ?? pairScenarioId;

    try {
      setLoadingResult(true);
      setError(null);
      setFunnelArtifact(null);
      setScenarioContext(null);
      deepOpenTracked.current = false;

      const endpoint = compatibilityType === "sign" ? "/compatibility/compare" : "/compatibility/synastry";
      const response = await postJson<any>(endpoint, {
        profile_id_1: profile1Id,
        profile_id_2: profile2Id,
        relation_mode: relationMode,
        format_id: activeFormatId,
      });

      setFunnelArtifact((response?.funnel_artifact as CompatibilityFunnelArtifact | null | undefined) ?? null);
      setScenarioContext(
        response?.scenario_context && typeof response.scenario_context === "object"
          ? response.scenario_context
          : null,
      );

      if (response?.compatibility) {
        setResult({
          overall_score: response.compatibility.overall_score || 0,
          aspects: Array.isArray(response.compatibility.aspects) ? response.compatibility.aspects : [],
          synastry: response.compatibility.synastry || null,
          summary: response.compatibility.summary || null,
          relationship_type: response.compatibility.relationship_type || null,
          recommendations: Array.isArray(response.compatibility.recommendations) ? response.compatibility.recommendations : [],
          editorial: response.compatibility.editorial || null,
          deep_dive: response.compatibility.deep_dive || null,
          profile_1: response.profile_1 || null,
          profile_2: response.profile_2 || null,
        });
      } else {
        setResult({
          overall_score: response?.overall_score || 0,
          aspects: Array.isArray(response?.aspects) ? response.aspects : [],
          synastry: response?.synastry || null,
          summary: response?.summary || null,
          relationship_type: response?.relationship_type || null,
          recommendations: Array.isArray(response?.recommendations) ? response.recommendations : [],
          editorial: response?.editorial || null,
          deep_dive: response?.deep_dive || null,
          profile_1: response?.profile_1 || null,
          profile_2: response?.profile_2 || null,
        });
      }

      const nextUrl = new URL(window.location.href);
      nextUrl.searchParams.set("profile1", String(profile1Id));
      nextUrl.searchParams.set("profile2", String(profile2Id));
      nextUrl.searchParams.set("relation_mode", relationMode);
      nextUrl.searchParams.set("mode", compatibilityType);
      nextUrl.searchParams.set("series", activeFormatId);
      nextUrl.searchParams.delete("topic");
      window.history.replaceState({}, "", nextUrl.toString());
      setUrlSeries(activeFormatId);
      setUrlTopic(null);

      await logActiveJTBDAction("compatibility_compare_completed", {
        relation_mode: relationMode,
        compatibility_type: compatibilityType,
        profile_1_id: profile1Id,
        profile_2_id: profile2Id,
      }).catch((error) => {
        console.error("Failed to log compatibility completion", error);
      });
      trackMeaningEvent({
        event_type: "compatibility_view",
        event_source: "compatibility",
        idempotency_key: `compatibility_view:pair:${relationMode}:${profile1Id}:${profile2Id}:${new Date().toISOString().slice(0, 10)}`,
        payload: {
          relation_mode: relationMode,
          compatibility_type: compatibilityType,
          profile_1_id: profile1Id,
          profile_2_id: profile2Id,
          overall_score:
            response?.compatibility?.overall_score ??
            response?.overall_score ??
            null,
        },
      });
    } catch (err: any) {
      console.error("Error calculating compatibility:", err);
      setError(err?.message || "Не удалось рассчитать совместимость. Проверь сеть и попробуй еще раз.");
      toast.error(err?.message || "Не удалось рассчитать совместимость. Проверь сеть и попробуй еще раз.");
    } finally {
      setLoadingResult(false);
    }
  };

  const handlePairScenarioSwitch = (toScenarioId: string, href: string) => {
    trackMeaningEvent(buildCompatibilityScenarioSwitchEvent(pairLearningMeta, toScenarioId, href));
    setUrlSeries(toScenarioId);
    setUrlTopic(null);
    void runCompatibility(toScenarioId);
  };

  useEffect(() => {
    if (!isAuthenticated || loadingProfiles || !urlSeries || !profile1Id || !profile2Id || profile1Id === profile2Id) {
      return;
    }
    if (loadingResult) return;
    if (result && scenarioContext?.format_id === pairScenarioId) return;
    const autoKey = `${urlSeries}:${profile1Id}:${profile2Id}`;
    if (seriesAutoRunRef.current === autoKey) return;
    seriesAutoRunRef.current = autoKey;
    void runCompatibility();
  }, [
    isAuthenticated,
    loadingProfiles,
    urlSeries,
    profile1Id,
    profile2Id,
    pairScenarioId,
    result,
    scenarioContext?.format_id,
    loadingResult,
  ]);

  const handleHubCalculate = () => {
    const mode = compatChrome.modes.find((item) => item.id === compatWebModeId);
    void runCompatibility(mode?.scenarioId);
  };

  const renderCompatHub = () => (
    <CompatibilityWebHub
      isAuthenticated={isAuthenticated}
      profiles={profiles.map((profile) => ({ id: profile.id, label: profile.label }))}
      profile1Id={profile1Id}
      profile2Id={profile2Id}
      selectedModeId={compatWebModeId}
      onModeChange={handleWebModeChange}
      onProfile1Change={setProfile1Id}
      onProfile2Change={setProfile2Id}
      onCalculate={handleHubCalculate}
      loading={loadingResult}
      error={error}
    />
  );

  if (authLoading || (isAuthenticated && loadingProfiles)) {
    return compatWebShell(
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "40vh" }}>
        <LoadingSpinner size="lg" />
      </div>,
    );
  }

  if (!isAuthenticated) {
    return compatWebShell(
      <>
        <CompatibilityLayerSelector isAuthenticated={false} />
      </>,
      { rail: <CompatibilityWebHubRail locale={compatLocale} /> },
    );
  }

  if (pairExplorationModel && result) {
    const worksBullets = [strongestDescription, ...editorialStrengths.map(cleanCompatibilityLine), ...extraStrengths]
      .map(cleanCompatibilityLine)
      .filter(Boolean)
      .filter((item, index, list) => list.indexOf(item) === index)
      .slice(0, 3);
    const failsBullets = [tensionDescription, ...editorialTensions.map(cleanCompatibilityLine), ...extraChallenges]
      .map(cleanCompatibilityLine)
      .filter(Boolean)
      .filter((item, index, list) => list.indexOf(item) === index)
      .slice(0, 3);
    const frictionTags = editorialTensions
      .map(cleanCompatibilityLine)
      .filter(Boolean)
      .slice(0, 4);
    const fallbackFriction = visibleAspects
      .filter((aspect) => aspect.score < 60)
      .map((aspect) => cleanCompatibilityLine(aspect.type))
      .filter(Boolean)
      .slice(0, 4);

    const metaChips = buildCompatibilityMetaChips({
      synastry: result.synastry,
      deep_dive: result.deep_dive,
      aspects: result.aspects,
    });

    return compatWebShell(
      <CompatibilityWebResult
        model={pairExplorationModel}
        name1={selectedProfile1?.label ?? "Профиль 1"}
        name2={selectedProfile2?.label ?? "Профиль 2"}
        activeScenarioId={pairScenarioId}
        works={worksBullets}
        fails={failsBullets}
        frictionTags={frictionTags.length ? frictionTags : fallbackFriction}
        potentialLabel={potentialLabelFromScore(pairExplorationModel.score, compatLocale)}
        nextStep={nextStepDescription}
        metaChips={metaChips}
        buildScenarioHref={buildPairScenarioHref}
        onScenarioSwitch={handlePairScenarioSwitch}
        onDeepOpen={handlePairDeepOpen}
        onShare={() => {
          if (typeof navigator !== "undefined" && navigator.share) {
            void navigator.share({ title: "TodayFlow — совместимость", text: pairExplorationModel.pairLine, url: window.location.href });
          }
        }}
        onSave={() => {
          void runCompatibility();
        }}
        extra={funnelArtifact ? <CompatibilityFunnelSection artifact={funnelArtifact} /> : null}
      />,
      {
        hideHeader: true,
        contentClassName: l.compatWebResultContent,
        rail: (
          <CompatibilityWebResultRail
            score={pairExplorationModel.score}
            dimensions={pairExplorationModel.dimensions}
            chrome={compatChrome}
          />
        ),
      },
    );
  }

  if (!profiles.length || profiles.length < 2) {
    return compatWebShell(renderCompatHub(), { rail: <CompatibilityWebHubRail locale={compatLocale} /> });
  }

  return compatWebShell(renderCompatHub(), { rail: <CompatibilityWebHubRail locale={compatLocale} /> });

}
