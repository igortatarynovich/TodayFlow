"use client";

import { useEffect, useState } from "react";

export function PWAInstaller() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showInstallButton, setShowInstallButton] = useState(false);

  useEffect(() => {
    const isProd = process.env.NODE_ENV === "production";
    const isLocalhost =
      typeof window !== "undefined" &&
      (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");
    const shouldEnableSw = isProd && !isLocalhost;

    // В dev Service Worker часто ломает Next.js RSC-навигацию и дает 404/дерганье.
    if (typeof window !== "undefined" && "serviceWorker" in navigator) {
      if (!shouldEnableSw) {
        navigator.serviceWorker.getRegistrations()
          .then((registrations) => Promise.all(registrations.map((r) => r.unregister())))
          .then(async () => {
            if ("caches" in window) {
              const keys = await caches.keys();
              await Promise.all(keys.map((key) => caches.delete(key)));
            }
          })
          .catch((error) => {
            console.warn("[PWA] Не удалось очистить Service Worker:", error);
          });
      } else {
        navigator.serviceWorker
          .register("/sw.js")
          .then((registration) => {
            console.log("[PWA] Service Worker зарегистрирован:", registration);
          })
          .catch((error) => {
            console.error("[PWA] Ошибка регистрации Service Worker:", error);
          });
      }
    }

    // Обработка события beforeinstallprompt для показа кнопки установки
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallButton(true);
    };

    if (shouldEnableSw) {
      window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
    }

    // Проверка, установлено ли приложение
    if (window.matchMedia("(display-mode: standalone)").matches) {
      console.log("[PWA] Приложение запущено в standalone режиме");
    }

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      return;
    }

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === "accepted") {
      console.log("[PWA] Пользователь принял установку");
    } else {
      console.log("[PWA] Пользователь отклонил установку");
    }

    setDeferredPrompt(null);
    setShowInstallButton(false);
  };

  const isLocalhost =
    typeof window !== "undefined" &&
    (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");

  if (process.env.NODE_ENV !== "production" || isLocalhost || !showInstallButton) {
    return null;
  }

  return (
    <div
      style={{
        position: "fixed",
        bottom: "20px",
        right: "20px",
        zIndex: 1000,
        background: "white",
        padding: "12px 20px",
        borderRadius: "8px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
        display: "flex",
        alignItems: "center",
        gap: "12px",
      }}
    >
      <span style={{ fontSize: "14px", color: "#333" }}>
        Установить TodayFlow
      </span>
      <button
        onClick={handleInstallClick}
        style={{
          padding: "8px 16px",
          background: "#667eea",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "14px",
          fontWeight: "600",
        }}
      >
        Установить
      </button>
    </div>
  );
}
