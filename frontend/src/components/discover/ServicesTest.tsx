"use client";

import { useState } from "react";
import Link from "next/link";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";
import { LoadingSpinner } from "@/components/orbit";
import { useAuth } from "@/lib/useAuth";

interface Service {
  id: string;
  name: string;
  description: string;
  icon: string;
  path: string;
  category: "reports" | "daily" | "practices" | "tools" | "account";
  requiresAuth?: boolean;
}

const SERVICES: Service[] = [
  // Отчёты
  {
    id: "birth-chart",
    name: "Разбор натальной карты",
    description: "Полный астрологический разбор",
    icon: "🌟",
    path: "/onboarding/core",
    category: "reports",
  },
  {
    id: "full-report",
    name: "Полный разбор",
    description: "Детальный разбор всех паттернов",
    icon: "📊",
    path: "/reports/full",
    category: "reports",
    requiresAuth: true,
  },
  {
    id: "thematic-career",
    name: "Разбор: Карьера",
    description: "Тематический разбор карьерных паттернов",
    icon: "💼",
    path: "/reports/thematic/career",
    category: "reports",
    requiresAuth: true,
  },
  {
    id: "thematic-love",
    name: "Разбор: Отношения",
    description: "Тематический разбор романтических паттернов",
    icon: "💕",
    path: "/reports/thematic/love",
    category: "reports",
    requiresAuth: true,
  },
  {
    id: "thematic-family",
    name: "Разбор: Семья",
    description: "Тематический разбор семейных паттернов",
    icon: "👨‍👩‍👧‍👦",
    path: "/reports/thematic/family",
    category: "reports",
    requiresAuth: true,
  },
  {
    id: "thematic-children",
    name: "Разбор: Дети",
    description: "Тематический разбор паттернов воспитания",
    icon: "👶",
    path: "/reports/thematic/children",
    category: "reports",
    requiresAuth: true,
  },
  {
    id: "compatibility",
    name: "Совместимость",
    description: "Сравнение двух натальных карт",
    icon: "💑",
    path: "/compatibility",
    category: "reports",
    requiresAuth: true,
  },
  
  // Ежедневные сервисы
  {
    id: "daily",
    name: "Я сегодня",
    description: "Персональная карта дня",
    icon: "📅",
    path: "/today",
    category: "daily",
    requiresAuth: true,
  },
  {
    id: "card-of-day",
    name: "Карта дня",
    description: "Таро карта дня и программа",
    icon: "🃏",
    path: "/today",
    category: "daily",
    requiresAuth: true,
  },
  {
    id: "tarot",
    name: "Таро",
    description: "Расклады и история карт",
    icon: "🔮",
    path: "/tarot",
    category: "daily",
  },
  {
    id: "celestial",
    name: "Небесные события",
    description: "Лунные фазы и планетарные события",
    icon: "🌙",
    path: "/lunar/today",
    category: "daily",
  },
  {
    id: "numerology",
    name: "Нумерология",
    description: "Числа имени и дня",
    icon: "🔢",
    path: "/profile",
    category: "daily",
  },
  {
    id: "weekly",
    name: "Недельный обзор",
    description: "Еженедельные инсайты",
    icon: "📆",
    path: "/weekly",
    category: "daily",
    requiresAuth: true,
  },
  
  // Практики
  {
    id: "practices",
    name: "Практики",
    description: "Персонализированные практики",
    icon: "🧘",
    path: "/practices",
    category: "practices",
    requiresAuth: true,
  },
  {
    id: "challenges",
    name: "Челленджи",
    description: "Карты, аскезы, цели, привычки",
    icon: "🎯",
    path: "/challenges",
    category: "practices",
    requiresAuth: true,
  },
  {
    id: "journal",
    name: "Журнал",
    description: "Дневник наблюдений и благодарности",
    icon: "📔",
    path: "/journal",
    category: "practices",
    requiresAuth: true,
  },
  
  // Инструменты
  {
    id: "horoscopes",
    name: "Гороскопы",
    description: "Китайский, зороастрийский, тибетский",
    icon: "⭐",
    path: PROFILE_CHART_DEEP_PATH,
    category: "tools",
  },
  {
    id: "aspects",
    name: "Аспекты",
    description: "Планетарные аспекты",
    icon: "⚡",
    path: "/discover",
    category: "tools",
    requiresAuth: true,
  },
  
  // Аккаунт
  {
    id: "account",
    name: "Аккаунт",
    description: "Настройки и профили",
    icon: "👤",
    path: "/account",
    category: "account",
    requiresAuth: true,
  },
  {
    id: "subscriptions",
    name: "Подписки",
    description: "Управление подписками",
    icon: "💳",
    path: "/account/subscriptions",
    category: "account",
    requiresAuth: true,
  },
];

export function ServicesTest() {
  const { isAuthenticated } = useAuth();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = Array.from(new Set(SERVICES.map(s => s.category)));
  const filteredServices = selectedCategory 
    ? SERVICES.filter(s => s.category === selectedCategory)
    : SERVICES;

  const visibleServices = filteredServices.filter(s => !s.requiresAuth || isAuthenticated);

  return (
    <section className="orbit-layer-secondary" style={{ 
      marginTop: "var(--orbit-space-4xl)",
      marginBottom: "var(--orbit-space-4xl)",
      padding: "var(--orbit-space-2xl)",
      background: "#ffffff",
      borderRadius: "var(--orbit-radius-md)",
      border: "1px solid #e5e0d8"
    }}>
      <h2 className="orbit-display-sm" style={{
        fontSize: "clamp(1.5rem, 3vw, 2rem)",
        marginBottom: "var(--orbit-space-md)",
        color: "#0f172a",
        fontWeight: 500
      }}>
        Все сервисы
      </h2>
      <p className="orbit-body-sm orbit-text-muted" style={{
        marginBottom: "var(--orbit-space-lg)",
        lineHeight: 1.6
      }}>
        Полный список доступных сервисов для тестирования
      </p>

      {/* Фильтры по категориям */}
      <div style={{ 
        display: "flex", 
        flexWrap: "wrap", 
        gap: "var(--orbit-space-sm)",
        marginBottom: "var(--orbit-space-lg)"
      }}>
        <button
          onClick={() => setSelectedCategory(null)}
          className={`orbit-button orbit-button-xs ${selectedCategory === null ? "orbit-button-primary" : "orbit-button-secondary"}`}
        >
          Все
        </button>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`orbit-button orbit-button-xs ${selectedCategory === cat ? "orbit-button-primary" : "orbit-button-secondary"}`}
          >
            {cat === "reports" ? "Отчёты" :
             cat === "daily" ? "Ежедневные" :
             cat === "practices" ? "Практики" :
             cat === "tools" ? "Инструменты" :
             cat === "account" ? "Аккаунт" : cat}
          </button>
        ))}
      </div>

      {/* Сетка сервисов */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
        gap: "var(--orbit-space-md)"
      }}>
        {visibleServices.map(service => (
          <Link
            key={service.id}
            href={service.path}
            className="orbit-card"
            style={{
              padding: "var(--orbit-space-lg)",
              textDecoration: "none",
              display: "block",
              border: "1px solid var(--orbit-color-border)",
              borderRadius: "var(--orbit-radius-sm)",
              transition: "transform 0.2s ease, box-shadow 0.2s ease",
              background: "#ffffff"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.1)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)", marginBottom: "var(--orbit-space-sm)" }}>
              <div style={{ fontSize: "2rem" }}>{service.icon}</div>
              <h3 className="orbit-body" style={{ fontWeight: 600, margin: 0, color: "#0f172a" }}>
                {service.name}
              </h3>
            </div>
            <p className="orbit-body-sm orbit-text-muted" style={{ 
              marginBottom: "var(--orbit-space-sm)",
              lineHeight: 1.5
            }}>
              {service.description}
            </p>
            {service.requiresAuth && !isAuthenticated && (
              <span className="orbit-badge-xs" style={{ 
                background: "var(--orbit-color-mist)",
                color: "var(--orbit-color-slate)"
              }}>
                Требуется вход
              </span>
            )}
            <div style={{ marginTop: "var(--orbit-space-sm)", textAlign: "right" }}>
              <span className="orbit-link" style={{ fontSize: "0.875rem" }}>
                Открыть →
              </span>
            </div>
          </Link>
        ))}
      </div>

      {visibleServices.length === 0 && (
        <div style={{ textAlign: "center", padding: "var(--orbit-space-xl)" }}>
          <p className="orbit-body-sm orbit-text-muted">
            {selectedCategory 
              ? `Нет доступных сервисов в категории "${selectedCategory}"`
              : "Нет доступных сервисов"}
          </p>
        </div>
      )}
    </section>
  );
}
