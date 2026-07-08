"use client";

import { Component, ReactNode } from "react";
import Link from "next/link";
import { t } from "@/lib/i18n";
import { captureException } from "@/lib/sentry";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    captureException(error, {
      componentStack: errorInfo.componentStack,
      errorBoundary: true,
    });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <main className="orbit-page">
          <section className="orbit-card orbit-card-highlight">
            <h1 className="orbit-display">{t("error.boundary.title", "Что-то пошло не так")}</h1>
            <p className="orbit-body orbit-text-muted">
              {t("error.boundary.description", "Произошла ошибка при загрузке страницы. Пожалуйста, попробуйте обновить страницу или вернуться на главную.")}
            </p>
            {this.state.error && (
              <details className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-md)" }}>
                <summary>{t("error.boundary.details", "Детали ошибки")}</summary>
                <pre style={{ marginTop: "var(--orbit-space-sm)", padding: "var(--orbit-space-sm)", background: "var(--orbit-color-mist)", borderRadius: "2px", overflow: "auto" }}>
                  {this.state.error.message}
                </pre>
              </details>
            )}
            <div className="orbit-card-actions" style={{ marginTop: "var(--orbit-space-md)" }}>
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  window.location.reload();
                }}
                className="orbit-button orbit-button-primary"
              >
                {t("error.boundary.reload", "Обновить страницу")}
              </button>
              <Link href="/" className="orbit-button orbit-button-secondary">
                {t("error.boundary.home", "На главную")}
              </Link>
            </div>
          </section>
        </main>
      );
    }

    return this.props.children;
  }
}

