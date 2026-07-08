"use client";

import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { getLocale } from "@/lib/i18n";
import { flowTrackerChromeBundle } from "@/components/today/flowPracticesMainTabChrome";
import { ProductAuxWebScreen } from "@/components/product-ui/ProductAuxWebScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";

/**
 * Хаб карт. Основной сценарий — /tracking/calendar (создание сущностей на месте).
 * Дополнительно: карты аффирмаций и классический вид аскез.
 */
export default function ProgressTrackerHubPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const locale = getLocale() === "ru" ? "ru" : "en";
  const fc = flowTrackerChromeBundle(locale);

  if (authLoading) {
    return (
      <ProductAuxWebScreen
        title={fc.trackingProgressHubTitle}
        loading
        loadingLabel={fc.trackingProgressHubLoginTitle}
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductAuxWebScreen
        title={fc.trackingProgressHubTitle}
        guest={{
          message: fc.trackingProgressHubLoginBody,
          ctaHref: "/auth?redirect=/tracking/progress",
          ctaLabel: fc.trackingProgressHubLoginCta,
        }}
      />
    );
  }

  const cards: { href: string; title: string; desc: string; primary?: boolean }[] = [
    {
      href: "/tracking/calendar",
      title: fc.trackingProgressCardMainCalendarTitle,
      desc: fc.trackingProgressCardMainCalendarDesc,
      primary: true,
    },
    {
      href: "/tracking/calendar?create=goal",
      title: fc.trackingProgressCardQuickGoalTitle,
      desc: fc.trackingProgressCardQuickGoalDesc,
    },
    {
      href: "/tracking/calendar?create=habit",
      title: fc.trackingProgressCardQuickHabitTitle,
      desc: fc.trackingProgressCardQuickHabitDesc,
    },
    {
      href: "/tracking/calendar?create=ascetic",
      title: fc.trackingProgressCardQuickAsceticTitle,
      desc: fc.trackingProgressCardQuickAsceticDesc,
    },
    {
      href: "/asceticisms/tracker",
      title: fc.trackingProgressCardAsceticClassicTitle,
      desc: fc.trackingProgressCardAsceticClassicDesc,
    },
    {
      href: "/affirmations/tracker",
      title: fc.trackingProgressCardAffirmationsTitle,
      desc: fc.trackingProgressCardAffirmationsDesc,
    },
    {
      href: "/habits",
      title: fc.trackingProgressCardHabitsListTitle,
      desc: fc.trackingProgressCardHabitsListDesc,
    },
    {
      href: "/maps/mood",
      title: locale === "ru" ? "Карта настроения" : "Mood map",
      desc: locale === "ru" ? "Утренние отметки и история дня." : "Morning marks and day stories.",
    },
    {
      href: "/maps/energy",
      title: locale === "ru" ? "Карта энергии" : "Energy map",
      desc: locale === "ru" ? "Темп дня — история, не проценты." : "Day tempo as a story, not percentages.",
    },
    {
      href: "/maps/promise",
      title: locale === "ru" ? "Карта обещаний" : "Promise map",
      desc: locale === "ru" ? "Обещание дня и вечернее закрытие." : "Promise of the day and evening close.",
    },
    {
      href: "/maps/ascetic",
      title: locale === "ru" ? "Карта аскез" : "Ascetic map",
      desc: locale === "ru" ? "Тропа осознанной практики." : "Path of intentional practice.",
    },
    {
      href: "/maps/wish",
      title: locale === "ru" ? "Карта желаний" : "Wish map",
      desc: locale === "ru" ? "Якоря и маленькие шаги." : "Anchors and small steps.",
    },
    {
      href: "/maps/relationship",
      title: locale === "ru" ? "Карта связей" : "Relationship map",
      desc: locale === "ru" ? "Круги внимания, не рейтинг." : "Circles of attention, not a score.",
    },
    {
      href: "/maps/tarot",
      title: locale === "ru" ? "Карта таро" : "Tarot arc",
      desc: locale === "ru" ? "Архетипическое путешествие." : "Archetypal journey.",
    },
  ];

  return (
    <ProductAuxWebScreen
      testId="tracking-progress-hub"
      eyebrow={fc.trackingProgressHubEyebrow}
      title={fc.trackingProgressHubTitle}
      subtitle={fc.trackingProgressHubIntro}
      railTitle={locale === "ru" ? "Карты и трекеры" : "Maps & trackers"}
      railHint={
        locale === "ru"
          ? "Выбери карту — календарь, привычки, аскезы и персональные карты дня."
          : "Pick a map — calendar, habits, ascetics, and personal day maps."
      }
    >
      <div className={pl.gridHub}>
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className={`${pl.hubCard} ${card.primary ? pl.hubCardPrimary : ""}`.trim()}
          >
            <h2 className={pl.hubCardTitle}>{card.title} →</h2>
            <p className={pl.hubCardDesc}>{card.desc}</p>
          </Link>
        ))}
      </div>

      <div className={pl.footerLinks}>
        <Link href="/asceticisms" className={pl.footerLink}>
          {fc.trackingProgressFooterAsceticCatalog}
        </Link>
        <Link href="/affirmations" className={pl.footerLink}>
          {fc.trackingProgressFooterAffirmationsLibrary}
        </Link>
      </div>
    </ProductAuxWebScreen>
  );
}
