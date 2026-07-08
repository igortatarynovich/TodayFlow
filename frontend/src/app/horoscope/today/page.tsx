"use client";

import Link from "next/link";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { DsBody, DsButton } from "@/design-system";

const ZODIAC_SIGNS = [
  { id: "aries", name: "Овен", nameEn: "Aries" },
  { id: "taurus", name: "Телец", nameEn: "Taurus" },
  { id: "gemini", name: "Близнецы", nameEn: "Gemini" },
  { id: "cancer", name: "Рак", nameEn: "Cancer" },
  { id: "leo", name: "Лев", nameEn: "Leo" },
  { id: "virgo", name: "Дева", nameEn: "Virgo" },
  { id: "libra", name: "Весы", nameEn: "Libra" },
  { id: "scorpio", name: "Скорпион", nameEn: "Scorpio" },
  { id: "sagittarius", name: "Стрелец", nameEn: "Sagittarius" },
  { id: "capricorn", name: "Козерог", nameEn: "Capricorn" },
  { id: "aquarius", name: "Водолей", nameEn: "Aquarius" },
  { id: "pisces", name: "Рыбы", nameEn: "Pisces" },
];

const POPULAR_SIGNS = ["leo", "scorpio", "aries", "libra"];

export default function HoroscopeTodayPage() {
  return (
    <ProductPageScreen
      testId="horoscope-today-page"
      title="Гороскоп на сегодня"
      subtitle="Выбери свой знак зодиака, чтобы узнать, что тебя ждёт сегодня"
      contentClassName={pl.content}
    >
      <section>
        <h2 className={v2.sectionTitle}>Популярные сегодня</h2>
        <div className={pl.gridHub} style={{ marginTop: "0.75rem", maxWidth: "36rem" }}>
          {POPULAR_SIGNS.map((signId) => {
            const sign = ZODIAC_SIGNS.find((s) => s.id === signId);
            if (!sign) return null;
            return (
              <Link key={signId} href={`/horoscope/today/${signId}`} className={pl.hubCard}>
                <DsBody>{sign.name}</DsBody>
              </Link>
            );
          })}
        </div>
      </section>

      <section>
        <h2 className={v2.sectionTitle}>Все знаки зодиака</h2>
        <div className={pl.gridHub} style={{ marginTop: "0.75rem" }}>
          {ZODIAC_SIGNS.map((sign) => (
            <Link key={sign.id} href={`/horoscope/today/${sign.id}`} className={pl.hubCard}>
              <DsBody>{sign.name}</DsBody>
            </Link>
          ))}
        </div>
      </section>

      <section className={pl.panel}>
        <DsBody className={pl.bodyMbMd}>
          Хочешь персональный прогноз на основе твоей даты рождения?
        </DsBody>
        <DsButton href="/onboarding/core">Открыть в приложении</DsButton>
      </section>
    </ProductPageScreen>
  );
}
