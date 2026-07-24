"use client";

import Link from "next/link";
import { HeroLarge, heroLargeStyles } from "@/components/foundation/HeroLarge";
import type { ProfileV0ViewModel } from "@/lib/profilePage/buildProfileV0Data";
import { WEB_LAUNCH_MIN_PROFILE } from "@/lib/webLaunchFlags";
import { ProfileEditorialNumbers } from "./ProfileEditorialNumbers";
import { ProfileEditorialSocialMirror } from "./ProfileEditorialSocialMirror";
import { ProfilePortraitSection } from "@/components/profile/ProfilePortraitSection";
import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "./profileEditorial.module.css";

export type ProfileEditorialScreenProps = {
  model: ProfileV0ViewModel;
  onOpenBirthData: () => void;
};

export function ProfileEditorialScreen({ model, onOpenBirthData }: ProfileEditorialScreenProps) {
  const { header, who, numbers, socialMirror, love, money, action, deepDiveHref } = model;

  const metaParts = [
    header.sunSignDisplay,
    header.lifePath != null ? `Число пути ${header.lifePath}` : null,
  ].filter(Boolean);

  return (
    <div className={styles.shell}>
      <div className={styles.stack}>
        <ProfilePortraitSection variant="editorial">
        <HeroLarge
          symbolSeed={header.archetypeLabel}
          kicker="Профиль"
          title={header.archetypeLabel}
          poeticCaption={header.poeticCaption}
          metaLine={metaParts.length ? metaParts.join(" · ") : null}
          digest={header.intro}
          traits={header.qualities}
          topAction={
            <button type="button" className={heroLargeStyles.topAction} onClick={onOpenBirthData}>
              Данные рождения
            </button>
          }
          ariaLabel="Кто ты"
        />

        {who ? (
          <blockquote className={styles.statement}>
            <p className={styles.statementTitle}>Почему именно {who.archetypeLabel}</p>
            {who.whyManifest ? <p className={styles.statementLead}>{who.whyManifest}</p> : null}
            <p className={styles.statementNote}>{who.layerHint}</p>
          </blockquote>
        ) : null}

        {numbers ? <ProfileEditorialNumbers numbers={numbers} /> : null}

        {socialMirror ? <ProfileEditorialSocialMirror mirror={socialMirror} /> : null}

        {love || money ? (
          <div className={styles.lifeGrid}>
            {love ? (
              <section className={`${styles.section} ${styles.tintLove}`} aria-labelledby="profile-love">
                <p id="profile-love" className={styles.sectionLabel}>
                  Любовь
                </p>
                <h2 className={styles.sectionTitle}>Как ты строишь близость</h2>
                <p className={styles.sectionLead}>{love.style}</p>
                <div className={styles.signals}>
                  {love.whatMatters ? (
                    <p className={styles.signal}>
                      <strong>Важно</strong>
                      {love.whatMatters}
                    </p>
                  ) : null}
                  {love.watchout ? (
                    <p className={styles.signal}>
                      <strong>Мешает</strong>
                      {love.watchout}
                    </p>
                  ) : null}
                </div>
              </section>
            ) : null}

            {money ? (
              <section className={`${styles.section} ${styles.tintMoney}`} aria-labelledby="profile-money">
                <p id="profile-money" className={styles.sectionLabel}>
                  Деньги
                </p>
                <h2 className={styles.sectionTitle}>Как ты реализуешь себя</h2>
                <p className={styles.sectionLead}>{money.approach}</p>
                <div className={styles.signals}>
                  {money.helps ? (
                    <p className={styles.signal}>
                      <strong>Усиливает</strong>
                      {money.helps}
                    </p>
                  ) : null}
                  {money.blocks ? (
                    <p className={styles.signal}>
                      <strong>Тормозит</strong>
                      {money.blocks}
                    </p>
                  ) : null}
                </div>
              </section>
            ) : null}
          </div>
        ) : null}

        {action ? (
          <section className={`${styles.section} ${styles.compass}`} aria-labelledby="profile-compass">
            <p id="profile-compass" className={styles.sectionLabel}>
              Как двигаться
            </p>
            <h2 className={styles.sectionTitle}>{action.title}</h2>
            {action.mainText ? <p className={styles.sectionLead}>{action.mainText}</p> : null}

            {action.rules.length ? (
              <ol className={styles.steps}>
                {action.rules.map((rule, index) => (
                  <li key={rule} className={styles.step}>
                    <span className={styles.stepNum}>{index + 1}</span>
                    <span>{rule}</span>
                  </li>
                ))}
              </ol>
            ) : null}

            {action.recommendation ? (
              <div className={styles.today}>
                <p className={styles.todayLabel}>Сегодня</p>
                <p className={styles.todayText}>{action.recommendation}</p>
              </div>
            ) : null}
          </section>
        ) : null}

        </ProfilePortraitSection>

        {/* PR-4: Maps home is /maps/* — thin CTA only. */}
        <p className={styles.mapsCta} data-testid="profile-maps-thin-cta">
          {PROFILE_V2_COPY.mapsCtaHint}{" "}
          <Link href="/maps/mood">{PROFILE_V2_COPY.mapsCta}</Link>
        </p>

        {!WEB_LAUNCH_MIN_PROFILE ? (
        <Link href={deepDiveHref} className={styles.portal}>
          <p className={styles.portalKicker}>Следующий уровень</p>
          <p className={styles.portalTitle}>Карта личности</p>
          <p className={styles.portalSub}>Планеты, дома, аспекты — полный разбор натальной карты.</p>
          <span className={styles.portalCta}>Войти в карту →</span>
        </Link>
        ) : null}
      </div>
    </div>
  );
}
