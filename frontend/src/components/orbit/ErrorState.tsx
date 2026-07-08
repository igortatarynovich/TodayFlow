"use client";

import React from "react";
import { t } from "@/lib/i18n";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title,
  message,
  onRetry,
  className = "",
}: ErrorStateProps) {
  const defaultTitle = title || t("errors.somethingWentWrong", "Что-то пошло не так");
  const defaultMessage = message || t("errors.loadError", "Произошла ошибка при загрузке данных. Пожалуйста, попробуйте позже.");
  return (
    <div className={`orbit-error-state ${className}`}>
      <div className="orbit-error-state__icon">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h3 className="orbit-error-state__title">{defaultTitle}</h3>
      <p className="orbit-error-state__message">{defaultMessage}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="orbit-button orbit-button-primary"
        >
          {t("errors.tryAgain", "Попробовать снова")}
        </button>
      )}
    </div>
  );
}

