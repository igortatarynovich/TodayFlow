"use client";

import Link from "next/link";

interface FullReportUpsellProps {
  context: "pattern" | "domain" | "system" | "global";
  patternName?: string;
  domainName?: string;
  hasFullReport?: boolean;
}

/**
 * Компонент для продажи Full Report
 * Используется в паттернах, сферах, системах и глобально
 */
export function FullReportUpsell({ 
  context, 
  patternName, 
  domainName,
  hasFullReport = false 
}: FullReportUpsellProps) {
  // Если у пользователя уже есть Full Report, не показываем апселл
  if (hasFullReport) {
    return null;
  }

  const getMessage = () => {
    switch (context) {
      case "pattern":
        return `Хочешь увидеть, как этот паттерн связан с остальными?`;
      case "domain":
        return `В полном разборе эта сфера раскрыта детально.`;
      case "system":
        return `Здесь показана лишь часть связей.`;
      case "global":
        return `Ты видишь фрагменты своей карты. Полный разбор собирает их в одну систему.`;
      default:
        return `Полный разбор раскрывает все связи и глубину.`;
    }
  };

  const getCTAText = () => {
    switch (context) {
      case "pattern":
        return "→ Полный разбор личности";
      case "domain":
        return "→ Посмотреть полный разбор";
      case "system":
        return "→ Открыть полную карту";
      case "global":
        return "Получить полный разбор →";
      default:
        return "→ Полный разбор";
    }
  };

  const isGlobal = context === "global";

  return (
    <div
      style={{
        padding: isGlobal ? "var(--orbit-space-xl)" : "var(--orbit-space-md)",
        background: isGlobal ? "#fefcf9" : "#faf9f7",
        border: isGlobal ? "2px solid #b87333" : "1px solid #e5e0d8",
        borderRadius: "var(--orbit-radius-md)",
        marginTop: isGlobal ? "var(--orbit-space-2xl)" : "var(--orbit-space-md)",
        textAlign: isGlobal ? "center" : "left"
      }}
    >
      <p 
        className={isGlobal ? "orbit-body" : "orbit-body-sm"}
        style={{
          marginBottom: isGlobal ? "var(--orbit-space-lg)" : "var(--orbit-space-sm)",
          color: "#334155",
          lineHeight: 1.6
        }}
      >
        {getMessage()}
      </p>
      <Link
        href="/reports/full"
        className={isGlobal ? "orbit-button orbit-button-primary" : "orbit-link"}
        style={{
          textDecoration: "none",
          display: isGlobal ? "inline-block" : "inline",
          fontSize: isGlobal ? undefined : "var(--orbit-text-body-sm)",
          fontWeight: 500,
          color: isGlobal ? undefined : "#b87333"
        }}
      >
        {getCTAText()}
      </Link>
    </div>
  );
}

