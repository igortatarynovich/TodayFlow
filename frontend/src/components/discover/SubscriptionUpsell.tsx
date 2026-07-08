"use client";

import Link from "next/link";

interface SubscriptionUpsellProps {
  hasSubscription?: boolean;
  trigger?: "days" | "patterns" | "practices" | "return";
  daysCount?: number;
  patternsCount?: number;
  practicesCount?: number;
}

/**
 * Компонент для продажи подписки
 * Показывается только при определённых триггерах
 */
export function SubscriptionUpsell({ 
  hasSubscription = false,
  trigger,
  daysCount,
  patternsCount,
  practicesCount
}: SubscriptionUpsellProps) {
  // Если у пользователя уже есть подписка, не показываем
  if (hasSubscription) {
    return null;
  }

  // Показываем только при определённых триггерах
  const shouldShow = () => {
    if (!trigger) return false;
    
    switch (trigger) {
      case "days":
        return daysCount !== undefined && daysCount >= 5;
      case "patterns":
        return patternsCount !== undefined && patternsCount >= 3;
      case "practices":
        return practicesCount !== undefined && practicesCount >= 5;
      case "return":
        return true; // Показываем при возврате из dashboard
      default:
        return false;
    }
  };

  if (!shouldShow()) {
    return null;
  }

  return (
    <div
      style={{
        padding: "var(--orbit-space-lg)",
        background: "#fefcf9",
        border: "1px solid #e5e0d8",
        borderRadius: "var(--orbit-radius-md)",
        marginTop: "var(--orbit-space-xl)",
        textAlign: "center"
      }}
    >
      <p
        className="orbit-body"
        style={{
          marginBottom: "var(--orbit-space-md)",
          color: "#334155",
          lineHeight: 1.6,
        }}
      >
        Ты уже получаешь сигналы дня.
      </p>
      <p
        className="orbit-body-sm orbit-text-muted"
        style={{
          marginBottom: "var(--orbit-space-lg)",
          lineHeight: 1.6,
        }}
      >
        Подписка открывает глубину: объяснения, паттерны и более цельное чтение жизни — чтобы было ощущение, что тебя понимают.
      </p>
      <Link
        href="/pricing"
        className="orbit-button orbit-button-secondary"
        style={{
          textDecoration: "none",
        }}
      >
        Узнать про глубину инсайтов →
      </Link>
    </div>
  );
}
