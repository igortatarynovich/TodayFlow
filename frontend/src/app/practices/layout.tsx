import type { ReactNode } from "react";
import Link from "next/link";
import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";
import { lookupPracticesCatalogServer } from "@/lib/practices/fetchPracticeDetailServer";
import styles from "@/app/practices/PracticesPage.module.css";

export const metadata = metadataForSegment("practices");

function difficultyRu(raw: string | null | undefined): string | null {
  if (!raw) return null;
  if (raw === "beginner") return "начальный";
  if (raw === "intermediate") return "средний";
  if (raw === "advanced") return "продвинутый";
  return raw;
}

export default async function PracticesLayout({ children }: { children: ReactNode }) {
  const catalog = await lookupPracticesCatalogServer();

  return (
    <>
      {catalog.length > 0 ? (
        <nav
          className={styles.ssrCatalog}
          aria-hidden="true"
          data-testid="practices-ssr-catalog"
        >
          <h2 className={styles.ssrCatalogTitle}>Практики</h2>
          <p className={styles.ssrCatalogLead}>
            Короткие шаги для спокойного дня — дыхание, медитация и ритуалы.
          </p>
          <ul className={styles.ssrCatalogList}>
            {catalog.map((item) => (
              <li key={item.id}>
                <Link href={`/practices/${item.id}`} className={styles.ssrCatalogLink}>
                  <span className={styles.ssrCatalogName}>{item.title}</span>
                  <span className={styles.ssrCatalogMeta}>
                    {[
                      item.duration_minutes != null ? `${item.duration_minutes} мин` : null,
                      difficultyRu(item.difficulty),
                    ]
                      .filter(Boolean)
                      .join(" · ")}
                  </span>
                  {item.description ? (
                    <span className={styles.ssrCatalogDesc}>{item.description}</span>
                  ) : null}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      ) : null}
      {children}
    </>
  );
}
