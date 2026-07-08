"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getJson, postJson, putJson, deleteJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { buildAuthHref } from "@/lib/authRedirect";
import { LoadingSpinner } from "@/components/orbit";

type LexiconPhrase = {
  id: string;
  text: string;
  context: string;
  trigger: string;
  emotion: string;
  reaction: string;
  tone: string;
};

type Lexicon = {
  meta: { version: string; description: string };
  banned_words: string[];
  tags_allow_list: string[];
  phrases: LexiconPhrase[];
};

export default function AdminLexiconPage() {
  const router = useRouter();
  const { isAuthenticated, profile, isLoading: authLoading } = useAuth();
  const [lexicon, setLexicon] = useState<Lexicon | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<LexiconPhrase | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [filterContext, setFilterContext] = useState<string>("");

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !profile)) {
      router.replace(buildAuthHref("login", "/admin/lexicon"));
      return;
    }
    if (isAuthenticated) {
      loadLexicon();
    }
  }, [isAuthenticated, authLoading, router, profile]);

  const loadLexicon = async () => {
    try {
      setLoading(true);
      const data = await getJson<Lexicon>("/admin/lexicon");
      setLexicon(data);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditing({
      id: "",
      text: "",
      context: "body",
      trigger: "overload",
      emotion: "tension",
      reaction: "withdraw",
      tone: "neutral",
    });
  };

  const handleEdit = (p: LexiconPhrase) => {
    setEditing({ ...p });
  };

  const handleSave = async () => {
    if (!editing || !lexicon) return;
    try {
      setMessage(null);
      if (editing.id && lexicon.phrases.some((p) => p.id === editing.id)) {
        await putJson(`/admin/lexicon/phrases/${editing.id}`, editing);
      } else {
        await postJson("/admin/lexicon/phrases", editing);
      }
      setEditing(null);
      await loadLexicon();
      setMessage("Сохранено");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка сохранения");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Удалить фразу?")) return;
    try {
      await deleteJson(`/admin/lexicon/phrases/${id}`);
      await loadLexicon();
      setMessage("Удалено");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка удаления");
    }
  };

  const handleUpdateBannedWords = async (words: string[]) => {
    if (!lexicon) return;
    try {
      await putJson("/admin/lexicon", { ...lexicon, banned_words: words });
      await loadLexicon();
      setMessage("Сохранено");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка");
    }
  };

  const handleUpdateTags = async (tags: string[]) => {
    if (!lexicon) return;
    try {
      await putJson("/admin/lexicon", { ...lexicon, tags_allow_list: tags });
      await loadLexicon();
      setMessage("Сохранено");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка");
    }
  };

  if (authLoading || loading) {
    return (
      <main className="orbit-page" style={{ minHeight: "50vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <LoadingSpinner size="lg" />
      </main>
    );
  }

  if (!lexicon) return null;

  const filteredPhrases = filterContext ? lexicon.phrases.filter((p) => p.context === filterContext) : lexicon.phrases;

  return (
    <main className="orbit-page" style={{ background: "var(--orbit-color-surface-subtle, #faf9f7)" }}>
      <section style={{ padding: "var(--orbit-space-3xl) var(--orbit-space-xl)" }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--orbit-space-xl)" }}>
            <div>
              <h1 className="orbit-display">Админка: Lexicon</h1>
              <p className="orbit-body-sm orbit-text-muted">CRUD фраз лексикона с метаданными (Web Canon v1)</p>
            </div>
            <div style={{ display: "flex", gap: "var(--orbit-space-md)" }}>
              <select value={filterContext} onChange={(e) => setFilterContext(e.target.value)} className="orbit-form" style={{ padding: "var(--orbit-space-sm)" }}>
                <option value="">Все контексты</option>
                <option value="body">Body</option>
                <option value="work">Work</option>
                <option value="relationship">Relationship</option>
                <option value="money">Money</option>
              </select>
              <button className="orbit-button orbit-button-primary" onClick={handleCreate}>
                Создать фразу
              </button>
              <Link href="/admin" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                К админке
              </Link>
            </div>
          </div>

          {message && (
            <div className="orbit-card" style={{ marginBottom: "var(--orbit-space-lg)", padding: "var(--orbit-space-md)" }}>
              <p className="orbit-body-sm">{message}</p>
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: editing ? "1fr 1fr" : "1fr", gap: "var(--orbit-space-xl)" }}>
            <div>
              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)", marginBottom: "var(--orbit-space-lg)" }}>
                <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>Banned Words</h2>
                <textarea
                  value={lexicon.banned_words.join("\n")}
                  onChange={(e) => handleUpdateBannedWords(e.target.value.split("\n").filter((x) => x.trim()))}
                  className="orbit-form orbit-form-textarea"
                  style={{ width: "100%", minHeight: "100px" }}
                  placeholder="Одно слово на строку"
                />
              </div>

              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)", marginBottom: "var(--orbit-space-lg)" }}>
                <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>Tags Allow List</h2>
                <textarea
                  value={lexicon.tags_allow_list.join("\n")}
                  onChange={(e) => handleUpdateTags(e.target.value.split("\n").filter((x) => x.trim()))}
                  className="orbit-form orbit-form-textarea"
                  style={{ width: "100%", minHeight: "100px" }}
                  placeholder="Один тег на строку"
                />
              </div>

              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
                <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
                  Фразы ({filteredPhrases.length} / {lexicon.phrases.length})
                </h2>
                <div style={{ maxHeight: "600px", overflowY: "auto" }}>
                  {filteredPhrases.map((p) => (
                    <div
                      key={p.id}
                      className="orbit-card"
                      style={{
                        padding: "var(--orbit-space-md)",
                        marginBottom: "var(--orbit-space-sm)",
                        border: "1px solid var(--orbit-color-border)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: "flex", gap: "var(--orbit-space-xs)", alignItems: "center", marginBottom: "var(--orbit-space-xs)" }}>
                            <strong className="orbit-body-sm">{p.id}</strong>
                            <span className="orbit-badge-xs">{p.context}</span>
                            <span className="orbit-badge-xs">{p.tone}</span>
                          </div>
                          <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                            {p.text}
                          </p>
                          <div className="orbit-body-xs orbit-text-muted">
                            trigger: {p.trigger} · emotion: {p.emotion} · reaction: {p.reaction}
                          </div>
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-xs)", marginLeft: "var(--orbit-space-md)" }}>
                          <button className="orbit-button orbit-button-xs orbit-button-secondary" onClick={() => handleEdit(p)}>
                            Редактировать
                          </button>
                          <button className="orbit-button orbit-button-xs" style={{ background: "#ef4444", color: "#fff" }} onClick={() => handleDelete(p.id)}>
                            Удалить
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {editing && (
              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
                <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>{editing.id ? "Редактировать" : "Создать"} фразу</h2>
                <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>ID (авто)</label>
                    <input type="text" value={editing.id || "auto"} disabled className="orbit-form" style={{ width: "100%" }} />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Text</label>
                    <textarea
                      value={editing.text}
                      onChange={(e) => setEditing({ ...editing, text: e.target.value })}
                      className="orbit-form orbit-form-textarea"
                      style={{ width: "100%", minHeight: "100px" }}
                    />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Context</label>
                    <select value={editing.context} onChange={(e) => setEditing({ ...editing, context: e.target.value })} className="orbit-form" style={{ width: "100%" }}>
                      <option value="body">body</option>
                      <option value="work">work</option>
                      <option value="relationship">relationship</option>
                      <option value="money">money</option>
                    </select>
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Trigger</label>
                    <input
                      type="text"
                      value={editing.trigger}
                      onChange={(e) => setEditing({ ...editing, trigger: e.target.value })}
                      className="orbit-form"
                      style={{ width: "100%" }}
                      placeholder="overload, uncertainty, conflict, deadline..."
                    />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Emotion</label>
                    <input
                      type="text"
                      value={editing.emotion}
                      onChange={(e) => setEditing({ ...editing, emotion: e.target.value })}
                      className="orbit-form"
                      style={{ width: "100%" }}
                      placeholder="tension, irritability, numbness, hope..."
                    />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Reaction</label>
                    <input
                      type="text"
                      value={editing.reaction}
                      onChange={(e) => setEditing({ ...editing, reaction: e.target.value })}
                      className="orbit-form"
                      style={{ width: "100%" }}
                      placeholder="rush, freeze, overthink, withdraw, please..."
                    />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Tone</label>
                    <select value={editing.tone} onChange={(e) => setEditing({ ...editing, tone: e.target.value })} className="orbit-form" style={{ width: "100%" }}>
                      <option value="neutral">neutral</option>
                      <option value="warm">warm</option>
                      <option value="calm">calm</option>
                    </select>
                  </div>
                  <div style={{ display: "flex", gap: "var(--orbit-space-md)" }}>
                    <button className="orbit-button orbit-button-primary" onClick={handleSave}>
                      Сохранить
                    </button>
                    <button className="orbit-button orbit-button-secondary" onClick={() => setEditing(null)}>
                      Отмена
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
