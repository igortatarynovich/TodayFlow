"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";

// Справочник знаков зодиака
const ZODIAC_SIGNS: Record<string, { name: string; nameEn: string }> = {
  aries: { name: "Овен", nameEn: "Aries" },
  taurus: { name: "Телец", nameEn: "Taurus" },
  gemini: { name: "Близнецы", nameEn: "Gemini" },
  cancer: { name: "Рак", nameEn: "Cancer" },
  leo: { name: "Лев", nameEn: "Leo" },
  virgo: { name: "Дева", nameEn: "Virgo" },
  libra: { name: "Весы", nameEn: "Libra" },
  scorpio: { name: "Скорпион", nameEn: "Scorpio" },
  sagittarius: { name: "Стрелец", nameEn: "Sagittarius" },
  capricorn: { name: "Козерог", nameEn: "Capricorn" },
  aquarius: { name: "Водолей", nameEn: "Aquarius" },
  pisces: { name: "Рыбы", nameEn: "Pisces" },
};

type HoroscopeResponse = {
  sign: string;
  date: string;
  summary: string;
  sections?: {
    love?: string;
    career?: string;
    health?: string;
    money?: string;
  };
};

export default function HoroscopeTodaySignPage() {
  const params = useParams();
  const signId = params?.sign as string;
  const sign = ZODIAC_SIGNS[signId];
  
  const [loading, setLoading] = useState(true);
  const [horoscope, setHoroscope] = useState<HoroscopeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!signId || !sign) {
      setError("Знак зодиака не найден");
      setLoading(false);
      return;
    }

    const loadHoroscope = async () => {
      try {
        const summaries: Record<string, string> = {
          aries: "День требует инициативы: действуй короткими шагами и фиксируй результат.",
          taurus: "Лучше всего работают спокойный ритм и практичные решения без суеты.",
          gemini: "Сильный день для диалога и быстрых договоренностей, если держать фокус.",
          cancer: "Эмоциональная чувствительность высокая: опирайся на режим и ясные границы.",
          leo: "Твоя энергия заметна: направь ее в конкретную цель, а не в распыление.",
          virgo: "Хороший день для системности, чистки задач и наведения порядка в делах.",
          libra: "Баланс и дипломатия дают максимум: выбирай мягкие, но точные формулировки.",
          scorpio: "Глубокий фокус помогает продвинуть сложные темы, избегай резких реакций.",
          sagittarius: "День для расширения горизонтов, обучения и смелого, но расчетливого шага.",
          capricorn: "Работает дисциплина: приоритизируй 1-2 главные задачи и доводи до конца.",
          aquarius: "Сильны нестандартные решения; оформляй идеи сразу в понятные действия.",
          pisces: "Интуиция точная, но ей нужна структура: план + восстановление дадут лучший эффект.",
        };
        const love: Record<string, string> = {
          aries: "Инициируй разговор первым, но слушай не меньше, чем говоришь.",
          taurus: "Поддержка и стабильность сегодня ценятся больше громких жестов.",
          gemini: "Честный диалог снимает напряжение и быстро возвращает близость.",
          cancer: "Важны тепло и такт: избегай резких оценок в личных темах.",
          leo: "Покажи внимание к партнеру через конкретное действие, не только слова.",
          virgo: "Небольшая забота и пунктуальность укрепят доверие.",
          libra: "Компромисс сегодня легче, чем спор о принципах.",
          scorpio: "Глубина чувств полезна, если говорить прямо и без давления.",
          sagittarius: "Совместные планы и легкость в общении дадут лучший тон.",
          capricorn: "Надежность и последовательность скажут больше эмоциональных всплесков.",
          aquarius: "Уважай свободу партнера и формулируй ожидания заранее.",
          pisces: "Мягкость и эмпатия помогут восстановить контакт даже после сложного дня.",
        };
        setHoroscope({
          sign: sign.nameEn,
          date: new Date().toISOString().split("T")[0],
          summary: summaries[signId] || "День для спокойного, осознанного движения вперед.",
          sections: {
            love: love[signId] || "Поддерживай честный и бережный контакт.",
            career: "Сфокусируйся на одной ключевой задаче и закрой ее до конца дня.",
            health: "Сохраняй режим сна и делай короткие паузы на восстановление в течение дня.",
            money: "Избегай импульсивных трат, сверяй решения с недельными приоритетами.",
          },
        });
        setLoading(false);
      } catch (err) {
        console.error("Failed to load horoscope", err);
        setError("Не удалось загрузить гороскоп");
        setLoading(false);
      }
    };

    loadHoroscope();
  }, [signId, sign]);

  if (!sign) {
    return (
      <ProductPageScreen testId="horoscope-sign-page" title="Знак зодиака не найден" contentClassName={pl.content}>
        <DsButton href="/horoscope/today" variant="secondary">
          Вернуться к выбору знака
        </DsButton>
      </ProductPageScreen>
    );
  }

  if (loading) {
    return (
      <ProductPageScreen
        testId="horoscope-sign-page"
        title={`Гороскоп для ${sign.name}`}
        loading
        loadingLabel="Загрузка гороскопа…"
      />
    );
  }

  if (error || !horoscope) {
    return (
      <ProductPageScreen testId="horoscope-sign-page" title={error || "Ошибка загрузки"} contentClassName={pl.content}>
        <DsButton href="/horoscope/today" variant="secondary">
          Вернуться к выбору знака
        </DsButton>
      </ProductPageScreen>
    );
  }

  const dateLabel = new Date(horoscope.date).toLocaleDateString("ru-RU", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <ProductPageScreen
      testId="horoscope-sign-page"
      title={`Гороскоп на сегодня для ${sign.name}`}
      subtitle={dateLabel}
      contentClassName={pl.content}
    >
      <Link href="/horoscope/today" className={pl.textLink}>
        ← Все знаки
      </Link>

      <section className={pl.panel}>
        <DsBody>{horoscope.summary}</DsBody>
      </section>

      {horoscope.sections ? (
        <div className={pl.formStack}>
          {horoscope.sections.love ? (
            <section className={pl.panel}>
              <h3 className={v2.sectionTitle}>Любовь</h3>
              <DsBody size="sm" muted className={pl.bodyMtSm}>
                {horoscope.sections.love}
              </DsBody>
            </section>
          ) : null}
          {horoscope.sections.career ? (
            <section className={pl.panel}>
              <h3 className={v2.sectionTitle}>Карьера</h3>
              <DsBody size="sm" muted className={pl.bodyMtSm}>
                {horoscope.sections.career}
              </DsBody>
            </section>
          ) : null}
          {horoscope.sections.health ? (
            <section className={pl.panel}>
              <h3 className={v2.sectionTitle}>Здоровье</h3>
              <DsBody size="sm" muted className={pl.bodyMtSm}>
                {horoscope.sections.health}
              </DsBody>
            </section>
          ) : null}
          {horoscope.sections.money ? (
            <section className={pl.panel}>
              <h3 className={v2.sectionTitle}>Финансы</h3>
              <DsBody size="sm" muted className={pl.bodyMtSm}>
                {horoscope.sections.money}
              </DsBody>
            </section>
          ) : null}
        </div>
      ) : null}

      <section className={pl.panel}>
        <DsBody className={pl.bodyMbMd}>
          Хочешь персональный прогноз на основе твоей даты рождения?
        </DsBody>
        <DsButton href="/onboarding/core">Открыть персональный прогноз</DsButton>
      </section>

      <section>
        <h2 className={v2.sectionTitle}>Также интересно</h2>
        <div className={pl.gridHub} style={{ marginTop: "0.75rem" }}>
          <Link href="/compatibility/signs" className={pl.hubCard}>
            <DsBody size="sm">Совместимость</DsBody>
          </Link>
          <Link href="/lunar/today" className={pl.hubCard}>
            <DsBody size="sm">Луна сегодня</DsBody>
          </Link>
          <Link href="/today" className={pl.hubCard}>
            <DsBody size="sm">Карта таро дня</DsBody>
          </Link>
        </div>
      </section>
    </ProductPageScreen>
  );
}
