"use client";

import Link from "next/link";
import { useCallback, useRef, useState } from "react";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { ProfileLivingMapsSection } from "@/components/profile/ProfileLivingMapsSection";
import { ProfilePortraitSection } from "@/components/profile/ProfilePortraitSection";
import type { ProfileV0ViewModel } from "@/lib/profilePage/buildProfileV0Data";
import { ProfileV0ActionLayer } from "./ProfileV0ActionLayer";
import { ProfileV0Hero } from "./ProfileV0Hero";
import { ProfileV0LifeLayer } from "./ProfileV0LifeLayer";
import { ProfileV0NumbersMiniHero } from "./ProfileV0NumbersMiniHero";
import { ProfileV0SocialMirrorBlock } from "./ProfileV0SocialMirrorBlock";
import { ProfileV0WhoScene } from "./ProfileV0WhoScene";
import styles from "./profileV0.module.css";

export type ProfileV0ScreenProps = {
  model: ProfileV0ViewModel;
  onOpenBirthData: () => void;
};

export function ProfileV0Screen({ model, onOpenBirthData }: ProfileV0ScreenProps) {
  const { header, who, numbers, socialMirror, love, money, action, deepDiveHref } = model;
  const whyRef = useRef<HTMLDivElement | null>(null);
  const [numbersOpen, setNumbersOpen] = useState(false);
  const shapeAudit = process.env.NEXT_PUBLIC_PROFILE_SHAPE_AUDIT === "1";

  const scrollToWhy = useCallback(() => {
    whyRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  return (
    <div className={`${styles.page} ${shapeAudit ? styles.pageShapeAudit : ""}`}>
      <div className={styles.profileStack}>
        <ProfilePortraitSection variant="v0">
          <ProfileV0Hero header={header} onOpenBirthData={onOpenBirthData} onScrollDeeper={scrollToWhy} />

          {who ? (
            <div ref={whyRef}>
              <ProfileV0WhoScene who={who} />
            </div>
          ) : null}

          {numbers ? (
            <ProfileV0NumbersMiniHero
              numbers={numbers}
              expanded={numbersOpen}
              onExpand={() => setNumbersOpen((v) => !v)}
            />
          ) : null}

          {socialMirror ? <ProfileV0SocialMirrorBlock mirror={socialMirror} /> : null}

          {love || money ? <ProfileV0LifeLayer love={love} money={money} /> : null}

          {action ? <ProfileV0ActionLayer action={action} /> : null}
        </ProfilePortraitSection>

        <ProfileLivingMapsSection variant="editorial" showMyDays />

        <Link href={deepDiveHref} className={styles.profilePortalCard}>
          <div className={styles.profilePortalVisual}>
            <SacredGeometryBackdrop emphasis="strong" preset="portal" tone="dark" />
            <div className={styles.atlasVignette} aria-hidden />
            <div className={styles.atlasPortalSlit} aria-hidden />
          </div>

          <div className={styles.profilePortalContent}>
            <p className={styles.atlasCoverKicker}>Следующий уровень</p>
            <p className={styles.atlasCoverTitle}>Карта личности</p>
            <p className={styles.atlasCoverSub}>Планеты, дома, аспекты — полный разбор натальной карты.</p>
            <span className={styles.profilePortalBtn}>
              Войти
              <span className={styles.profileCardCtaArrow} aria-hidden>
                →
              </span>
            </span>
          </div>
        </Link>
      </div>
    </div>
  );
}
