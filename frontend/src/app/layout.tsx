import "./globals.css";
import "@/styles/section-atmosphere.css";
import "@/styles/day-phase-atmosphere.css";
import "@/styles/mood-themes.css";
import "@/styles/premium-ui.css";
import type { ReactNode } from "react";
import type { Viewport } from "next";
import { Suspense } from "react";
import dynamic from "next/dynamic";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ToastProvider } from "@/components/ToastProvider";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PWAInstaller } from "@/components/PWAInstaller";
import { JTBDRouteArrivalLogger } from "@/components/questions/JTBDRouteArrivalLogger";
import { SectionAtmosphereBridge } from "@/components/SectionAtmosphereBridge";
import { ProductWebShellBridge } from "@/components/product-ui/ProductWebShellBridge";
import { ProductWebShellConfigProvider } from "@/components/product-ui/productWebShellConfig";
import { ProductWebShellLayout } from "@/components/product-ui/ProductWebShellLayout";
import { TodayCycleProvider } from "@/components/providers/TodayCycleProvider";

const GlobalLevelStrip = dynamic(
  () => import("@/components/rewards/GlobalLevelStrip").then((m) => m.GlobalLevelStrip),
  { ssr: false },
);

/** Корректная ширина и масштаб на телефонах и в iOS WKWebView; safe-area для «чёлки» и нижней зоны. */
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#fff9f5",
};

export const metadata = {
  title: {
    default: "TodayFlow - Эра самопознания",
    template: "%s | TodayFlow"
  },
  description: "Понимай себя. Живи осознанно. Персонализированные астрологические инсайты для самопознания и личностного роста.",
  keywords: ["астрология", "карта рождения", "натальная карта", "самопознание", "личность", "TodayFlow"],
  authors: [{ name: "TodayFlow" }],
  creator: "TodayFlow",
  publisher: "TodayFlow",
  manifest: "/manifest.json",
  icons: {
    icon: "/icon.svg",
    shortcut: "/icon.svg",
    apple: "/images/hero-meditation.png",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "TodayFlow",
  },
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"),
  openGraph: {
    type: "website",
    locale: "ru_RU",
    url: "/",
    siteName: "TodayFlow",
    title: "TodayFlow - Эра самопознания",
    description: "Понимай себя. Живи осознанно. Персонализированные астрологические инсайты для самопознания и личностного роста.",
    images: [
      {
        url: "/images/hero-meditation.png",
        width: 1920,
        height: 1080,
        alt: "TodayFlow - Эра самопознания",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "TodayFlow - Эра самопознания",
    description: "Понимай себя. Живи осознанно.",
    images: ["/images/hero-meditation.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#fff9f5" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="TodayFlow" />
        <link rel="apple-touch-icon" href="/images/hero-meditation.png" />
      </head>
      <body>
        <ErrorBoundary>
          <ToastProvider>
            <Suspense fallback={null}>
              <JTBDRouteArrivalLogger />
              <SectionAtmosphereBridge />
              <ProductWebShellBridge />
            </Suspense>
            <TodayCycleProvider>
              <ProductWebShellConfigProvider>
                <div className="tf-shell">
                  <Header />
                  <GlobalLevelStrip />
                  <ProductWebShellLayout>
                    <div className="tf-content">{children}</div>
                  </ProductWebShellLayout>
                  <Footer />
                </div>
              </ProductWebShellConfigProvider>
            </TodayCycleProvider>
            <PWAInstaller />
          </ToastProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
