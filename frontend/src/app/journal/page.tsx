"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson } from "@/lib/api";
import { useDashboardData } from "@/hooks/useDashboardData";
import { t } from "@/lib/i18n";
import { useToast } from "@/components/ToastProvider";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";

type JournalEntry = {
  id: number;
  type: "observation" | "gratitude" | "insight";
  content: string;
  practice_id?: string | null;
  tarot_card_id?: string | null;
  pattern_axis_id?: string | null;
  day?: string | null;
  created_at: string;
};

type JournalRepetitions = {
  tension_mentions?: number | null;
  insight_after_practice?: number | null;
  most_active_pattern?: string | null;
};

// Используем функцию для получения переводов
const getEntryTypes = (t: (key: string, fallback: string) => string) => ({
  observation: {
    label: t("journal.types.observation.label", "Наблюдение"),
    question: t("journal.types.observation.question", "Что из сегодняшнего дня откликнулось сильнее всего?"),
    icon: "👁️",
  },
  gratitude: {
    label: t("journal.types.gratitude.label", "Благодарность"),
    question: t("journal.types.gratitude.question", "За что ты благодарен сегодня?"),
    icon: "🙏",
  },
  insight: {
    label: t("journal.types.insight.label", "Инсайт"),
    question: t("journal.types.insight.question", "Что ты понял о себе в этот момент?"),
    icon: "💡",
  },
});

const MAX_CHARS = 500;
const GUEST_DEMO_LIMIT = 1;

function JournalPageContent() {
  const ENTRY_TYPES = getEntryTypes(t);
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const { trackMeaningEvent } = useMeaningRuntime();
  const { data: dashboardData } = useDashboardData();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [repetitions, setRepetitions] = useState<JournalRepetitions | null>(null);
  const [showQuickEntry, setShowQuickEntry] = useState<string | null>(null);
  const [quickEntryText, setQuickEntryText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [justSaved, setJustSaved] = useState<{ entry: JournalEntry; patternAxisId?: string } | null>(null);
  const [guestEntriesCount, setGuestEntriesCount] = useState(0);

  // Определяем контекст из URL или dashboard
  const practiceId = searchParams.get("practice_id");
  const tarotCardId = searchParams.get("tarot_card_id");
  const patternAxisId = searchParams.get("pattern_axis_id") || dashboardData?.liteReport?.internal_model?.axes?.[0]?.axis_id;

  useEffect(() => {
    const loadData = async () => {
      if (!isAuthenticated) {
        // Для guest проверяем localStorage
        const guestCount = localStorage.getItem("guest_journal_entries_count");
        setGuestEntriesCount(guestCount ? parseInt(guestCount, 10) : 0);
        setLoading(false);
        return;
      }

      try {
        // Загружаем последние 7 записей
        const entriesData = await getJson<JournalEntry[]>("/journal/entries?limit=7").catch(() => []);
        setEntries(entriesData);

        // Загружаем повторы и акценты
        const reps = await getJson<JournalRepetitions>("/journal/repetitions").catch(() => null);
        setRepetitions(reps);
      } catch (err) {
        console.error("Error loading journal:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isAuthenticated]);

  const handleQuickEntrySubmit = async (type: string) => {
    if (!quickEntryText.trim()) return;

    if (!isAuthenticated) {
      // Guest может сделать только 1 демо-запись
      if (guestEntriesCount >= GUEST_DEMO_LIMIT) {
        toast.info(t("journal.guest.createProfile", "Чтобы сохранить и видеть повторы — создай профиль."));
        return;
      }
      
      // Сохраняем в localStorage для guest
      const demoEntry: JournalEntry = {
        id: Date.now(),
        type: type as "observation" | "gratitude" | "insight",
        content: quickEntryText.trim(),
        created_at: new Date().toISOString(),
      };
      
      localStorage.setItem("guest_journal_entries_count", String(guestEntriesCount + 1));
      setGuestEntriesCount(guestEntriesCount + 1);
      setShowQuickEntry(null);
      setQuickEntryText("");
      toast.success(t("journal.guest.demoSaved", "Демо-запись сохранена. Чтобы сохранять историю — создай профиль."));
      return;
    }

    setIsSubmitting(true);
    try {
      // Определяем день (сегодня)
      const today = new Date().toISOString().split("T")[0];

      const newEntry = await postJson<JournalEntry>("/journal/entries", {
        type,
        content: quickEntryText.trim(),
        practice_id: practiceId || null,
        tarot_card_id: tarotCardId || null,
        pattern_axis_id: patternAxisId || null,
        day: today,
      });

      setEntries([newEntry, ...entries]);
      trackMeaningEvent({
        event_type: "diary_entry",
        event_source: "today",
        payload: {
          entry_id: newEntry.id,
          entry_type: newEntry.type,
          has_pattern_axis: Boolean(newEntry.pattern_axis_id),
        },
      });
      setShowQuickEntry(null);
      setQuickEntryText("");
      
      // Показываем экран подтверждения
      setJustSaved({ entry: newEntry, patternAxisId: newEntry.pattern_axis_id || patternAxisId });
    } catch (err) {
      console.error("Error saving entry:", err);
      toast.error(t("journal.errors.saveFailed", "Ошибка при сохранении записи"));
    } finally {
      setIsSubmitting(false);
    }
  };

  const getAxisName = (axisId?: string | null): string => {
    if (!axisId) return "";
    const axisNames: Record<string, string> = {
      "A1": t("patterns.axis.A1", "Ориентация идентичности"),
      "A2": t("patterns.axis.A2", "Эмоциональная обработка"),
      "A3": t("patterns.axis.A3", "Принятие решений"),
      "A4": t("patterns.axis.A4", "Стабильность и изменения"),
      "A5": t("patterns.axis.A5", "Ориентация контроля"),
      "A6": t("patterns.axis.A6", "Реляционная ориентация"),
      "A7": t("patterns.axis.A7", "Управление энергией"),
    };
    return axisNames[axisId] || axisId;
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="journal-page"
        title={t("journal.title", "Зафиксировать день")}
        loading
        loadingLabel={t("journal.loading", "Загрузка…")}
      />
    );
  }

  if (justSaved) {
    return (
      <ProductPageScreen
        testId="journal-page"
        title={t("journal.saved.title", "Запись сохранена")}
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <DsBody>
            {t("journal.saved.body", "Запись сохранена.")}
            {justSaved.patternAxisId && (
              <>
                {" "}
                {t("journal.saved.patternPrefix", "Сегодня это было связано с паттерном")}{" "}
                <Link href={`/discover/pattern/${justSaved.patternAxisId}`} className={pl.textLink}>
                  {getAxisName(justSaved.patternAxisId)}
                </Link>
                .
              </>
            )}
          </DsBody>
          <div className={pl.formStack} style={{ marginTop: "1.25rem" }}>
            {justSaved.patternAxisId && (
              <DsButton href={`/discover/pattern/${justSaved.patternAxisId}`}>
                {t("journal.saved.viewPattern", "Посмотреть в моей карте →")}
              </DsButton>
            )}
            <DsButton href="/today" variant="secondary">
              {t("journal.saved.backToToday", "Вернуться к дню →")}
            </DsButton>
          </div>
        </section>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="journal-page"
      title={t("journal.title", "Зафиксировать день")}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
          {!showQuickEntry ? (
            <div style={{ display: "grid", gap: "var(--orbit-space-md)" }}>
              {(Object.keys(ENTRY_TYPES) as Array<keyof typeof ENTRY_TYPES>).map((type) => (
                <button
                  key={type}
                  onClick={() => setShowQuickEntry(type)}
                  className="orbit-button orbit-button-secondary"
                  style={{ 
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "var(--orbit-space-sm)",
                    padding: "var(--orbit-space-lg)"
                  }}
                >
                  <span style={{ fontSize: "1.5rem" }}>{ENTRY_TYPES[type].icon}</span>
                  <span>{ENTRY_TYPES[type].label}</span>
                </button>
              ))}
            </div>
          ) : (
            <div className="orbit-card" style={{ padding: "var(--orbit-space-xl)" }}>
              <h2 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
                {ENTRY_TYPES[showQuickEntry as keyof typeof ENTRY_TYPES].question}
              </h2>

              <textarea
                value={quickEntryText}
                onChange={(e) => {
                  if (e.target.value.length <= MAX_CHARS) {
                    setQuickEntryText(e.target.value);
                  }
                }}
                placeholder="..."
                className="orbit-form-input"
                style={{
                  minHeight: "120px",
                  resize: "vertical",
                  fontFamily: "var(--orbit-font-body)",
                  fontSize: "var(--orbit-text-body-sm)",
                  lineHeight: 1.6,
                  marginBottom: "var(--orbit-space-sm)",
                }}
                autoFocus
                disabled={isSubmitting}
              />

              <div style={{ 
                display: "flex", 
                justifyContent: "space-between", 
                alignItems: "center",
                marginBottom: "var(--orbit-space-md)"
              }}>
                <span className="orbit-body-xs orbit-text-muted">
                  {quickEntryText.length} / {MAX_CHARS}
                </span>
                <button
                  onClick={() => {
                    setShowQuickEntry(null);
                    setQuickEntryText("");
                  }}
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                >
                  Отмена
                </button>
              </div>

              <button
                onClick={() => handleQuickEntrySubmit(showQuickEntry)}
                className="orbit-button orbit-button-primary"
                style={{ width: "100%" }}
                disabled={!quickEntryText.trim() || isSubmitting}
              >
                {isSubmitting ? "Сохранение..." : "Сохранить"}
              </button>

              {!isAuthenticated && guestEntriesCount >= GUEST_DEMO_LIMIT && (
                <p className="orbit-body-sm orbit-text-muted" style={{ 
                  marginTop: "var(--orbit-space-md)",
                  textAlign: "center"
                }}>
                  Чтобы сохранить и видеть повторы — создай профиль.
                </p>
              )}
            </div>
          )}

          {!isAuthenticated && guestEntriesCount < GUEST_DEMO_LIMIT && (
            <p className="orbit-body-sm orbit-text-muted" style={{ 
              marginTop: "var(--orbit-space-md)",
              textAlign: "center"
            }}>
              Демо-режим: можно сделать {GUEST_DEMO_LIMIT - guestEntriesCount} запись
            </p>
          )}

          {!isAuthenticated && guestEntriesCount >= GUEST_DEMO_LIMIT && (
            <div className="orbit-card" style={{ 
              marginTop: "var(--orbit-space-lg)",
              padding: "var(--orbit-space-lg)",
              background: "var(--orbit-color-mist)"
            }}>
              <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-md)", textAlign: "center" }}>
                Чтобы сохранить и видеть повторы — создай профиль.
              </p>
              <Link href="/onboarding/welcome?fresh=1" className="orbit-button orbit-button-primary" style={{ width: "100%" }}>
                Создать профиль →
              </Link>
            </div>
          )}

      {isAuthenticated && entries.length > 0 && (
        <section className={pl.panel}>
          <div className={pl.toolbar}>
            <h2 className={v2.sectionTitle}>Последние записи</h2>
              <div style={{ display: "flex", gap: "var(--orbit-space-xs)" }}>
                <button
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                  onClick={async () => {
                    const token = localStorage.getItem("todayflow_token");
                    if (!token) return;
                    try {
                      const response = await fetch("/journal/export/csv", {
                        headers: {
                          "Authorization": `Bearer ${token}`,
                        },
                      });
                      if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `journal_entries_${new Date().toISOString().split("T")[0]}.csv`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                      }
                    } catch (err) {
                      console.error("Export failed", err);
                    }
                  }}
                >
                  CSV
                </button>
                <button
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                  onClick={async () => {
                    const token = localStorage.getItem("todayflow_token");
                    if (!token) return;
                    try {
                      const response = await fetch("/journal/export/json", {
                        headers: {
                          "Authorization": `Bearer ${token}`,
                        },
                      });
                      if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `journal_entries_${new Date().toISOString().split("T")[0]}.json`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                      }
                    } catch (err) {
                      console.error("Export failed", err);
                    }
                  }}
                >
                  JSON
                </button>
              </div>
            </div>

            <div style={{ display: "grid", gap: "var(--orbit-space-md)", marginBottom: "var(--orbit-space-lg)" }}>
              {entries.slice(0, 7).map((entry) => (
                <div key={entry.id} className="orbit-card" style={{ padding: "var(--orbit-space-md)" }}>
                  <div style={{ display: "flex", gap: "var(--orbit-space-sm)", marginBottom: "var(--orbit-space-xs)" }}>
                    <span>{ENTRY_TYPES[entry.type].icon}</span>
                    <span className="orbit-body-xs orbit-text-muted">
                      {ENTRY_TYPES[entry.type].label}
                    </span>
                    <span className="orbit-body-xs orbit-text-muted">•</span>
                    <span className="orbit-body-xs orbit-text-muted">
                      {new Date(entry.created_at).toLocaleDateString("ru-RU", {
                        day: "numeric",
                        month: "long",
                      })}
                    </span>
                  </div>
                  <p className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
                    {entry.content.length > 150 ? `${entry.content.substring(0, 150)}...` : entry.content}
                  </p>
                </div>
              ))}
            </div>

            {entries.length > 7 && (
              <DsButton href="/journal/all" variant="secondary">
                Смотреть все записи →
              </DsButton>
            )}
        </section>
      )}

      {isAuthenticated && repetitions && (
        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>Повторы и акценты</h2>

              <div style={{ display: "grid", gap: "var(--orbit-space-sm)", marginBottom: "var(--orbit-space-lg)" }}>
                {repetitions.tension_mentions && repetitions.tension_mentions > 0 && (
                  <p className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
                    За последние 7 дней ты {repetitions.tension_mentions} {repetitions.tension_mentions === 1 ? "раз" : "раза"} писал про напряжение
                  </p>
                )}

                {repetitions.insight_after_practice && repetitions.insight_after_practice > 0 && (
                  <p className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
                    Чаще всего ты фиксируешь инсайты после практик
                  </p>
                )}

                {repetitions.most_active_pattern && (
                  <p className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
                    В последних записях чаще всего упоминается паттерн{" "}
                    <Link 
                      href={`/discover/pattern/${repetitions.most_active_pattern}`}
                      className="orbit-link"
                    >
                      {getAxisName(repetitions.most_active_pattern)}
                    </Link>
                  </p>
                )}

                {!repetitions.tension_mentions && !repetitions.insight_after_practice && !repetitions.most_active_pattern && (
                  <p className="orbit-body-sm orbit-text-muted" style={{ lineHeight: 1.6 }}>
                    Продолжай фиксировать, чтобы увидеть закономерности
                  </p>
                )}
              </div>

              <DsButton href="/discover" variant="secondary">
                Посмотреть, как это связано с тобой →
              </DsButton>
        </section>
      )}
    </ProductPageScreen>
  );
}

export default function JournalPage() {
  return (
    <Suspense
      fallback={
        <ProductPageScreen
          testId="journal-page"
          title={t("journal.title", "Зафиксировать день")}
          loading
          loadingLabel="…"
        />
      }
    >
      <JournalPageContent />
    </Suspense>
  );
}
