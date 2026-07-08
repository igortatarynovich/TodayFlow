"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getJson, postJson, deleteJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { buildAuthHref } from "@/lib/authRedirect";
import { LoadingSpinner } from "@/components/orbit";

type Forecast = {
  id: string;
  date: string;
  locale: string;
  published: boolean;
  tags: string[];
  blocks: {
    theme: string;
    notice: string[];
    scene: string[];
    micro_action: string;
  };
  markers: {
    body: string[];
    social: string[];
    domestic: string[];
    micro_action: string[];
  };
  _quality_gate_errors?: string[];
};

export default function AdminForecastsPage() {
  const router = useRouter();
  const { isAuthenticated, profile, isLoading: authLoading } = useAuth();
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Forecast | null>(null);
  const [editing, setEditing] = useState<Forecast | null>(null);
  const [localeFilter, setLocaleFilter] = useState<string>("");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !profile || !profile.is_admin)) {
      router.replace(buildAuthHref("login", "/admin/forecasts"));
      return;
    }
    if (isAuthenticated && profile?.is_admin) {
      loadForecasts();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, authLoading, router, profile]);

  const loadForecasts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (localeFilter) params.set("locale", localeFilter);
      params.set("include_unpublished", "true");
      const data = await getJson<Forecast[]>(`/admin/forecasts?${params}`);
      setForecasts(Array.isArray(data) ? data : []);
      if (!Array.isArray(data)) {
        setMessage("Некорректный формат ответа от сервера.");
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка загрузки");
      setForecasts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    const newForecast: Forecast = {
      id: "",
      date: new Date().toISOString().split("T")[0],
      locale: "ru",
      published: false,
      tags: [],
      blocks: { theme: "", notice: [""], scene: [""], micro_action: "" },
      markers: { body: [], social: [], domestic: [], micro_action: [] },
    };
    setEditing(newForecast);
    setSelected(null);
  };

  const handleEdit = (f: Forecast) => {
    setEditing({ ...f });
    setSelected(null);
  };

  const handleSave = async () => {
    if (!editing) return;
    try {
      setMessage(null);
      if (editing.id) {
        await postJson(`/admin/forecasts/${editing.id}`, editing);
      } else {
        await postJson("/admin/forecasts", editing);
      }
      setEditing(null);
      await loadForecasts();
      setMessage("Сохранено");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка сохранения");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Удалить прогноз?")) return;
    try {
      await deleteJson(`/admin/forecasts/${id}`);
      await loadForecasts();
      setMessage("Удалено");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка удаления");
    }
  };

  const handlePublish = async (id: string) => {
    try {
      await postJson(`/admin/forecasts/${id}/publish`, {});
      await loadForecasts();
      setMessage("Статус обновлён");
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

  return (
    <main className="orbit-page" style={{ background: "var(--orbit-color-surface-subtle, #faf9f7)" }}>
      <section style={{ padding: "var(--orbit-space-3xl) var(--orbit-space-xl)" }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--orbit-space-xl)" }}>
            <div>
              <h1 className="orbit-display">Админка: Прогнозы</h1>
              <p className="orbit-body-sm orbit-text-muted">CRUD Daily Forecast (Web Canon v1)</p>
            </div>
            <div style={{ display: "flex", gap: "var(--orbit-space-md)" }}>
              <select value={localeFilter} onChange={(e) => setLocaleFilter(e.target.value)} className="orbit-form" style={{ padding: "var(--orbit-space-sm)" }}>
                <option value="">Все языки</option>
                <option value="ru">RU</option>
                <option value="en">EN</option>
              </select>
              <button className="orbit-button orbit-button-primary" onClick={handleCreate}>
                Создать
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
            <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
              <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>Список ({forecasts.length})</h2>
              <div style={{ maxHeight: "600px", overflowY: "auto" }}>
                {forecasts.map((f) => (
                  <div
                    key={f.id}
                    className="orbit-card"
                    style={{
                      padding: "var(--orbit-space-md)",
                      marginBottom: "var(--orbit-space-sm)",
                      border: selected?.id === f.id ? "2px solid var(--orbit-color-primary)" : "1px solid var(--orbit-color-border)",
                      background: selected?.id === f.id ? "var(--orbit-color-mist)" : "var(--orbit-color-surface)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", gap: "var(--orbit-space-sm)", alignItems: "center", marginBottom: "var(--orbit-space-xs)" }}>
                          <strong className="orbit-body-sm">{f.date}</strong>
                          <span className="orbit-body-xs">{f.locale}</span>
                          {f.published ? (
                            <span className="orbit-badge-xs" style={{ background: "var(--orbit-color-highlight)" }}>Опубликован</span>
                          ) : (
                            <span className="orbit-badge-xs orbit-badge-xs--muted">Черновик</span>
                          )}
                          {f._quality_gate_errors && f._quality_gate_errors.length > 0 && (
                            <span className="orbit-badge-xs" style={{ background: "#ef4444", color: "#fff" }}>
                              {f._quality_gate_errors.length} ошибок
                            </span>
                          )}
                        </div>
                        <p className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                          {f.blocks.theme?.substring(0, 100)}...
                        </p>
                        <div className="orbit-body-xs" style={{ color: "var(--orbit-color-slate)" }}>
                          Теги: {f.tags.join(", ") || "—"}
                        </div>
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-xs)", marginLeft: "var(--orbit-space-md)" }}>
                        <button className="orbit-button orbit-button-xs orbit-button-secondary" onClick={() => setSelected(f)}>
                          Просмотр
                        </button>
                        <button className="orbit-button orbit-button-xs orbit-button-secondary" onClick={() => handleEdit(f)}>
                          Редактировать
                        </button>
                        <button className="orbit-button orbit-button-xs orbit-button-secondary" onClick={() => handlePublish(f.id)}>
                          {f.published ? "Снять" : "Опубликовать"}
                        </button>
                        <button className="orbit-button orbit-button-xs" style={{ background: "#ef4444", color: "#fff" }} onClick={() => handleDelete(f.id)}>
                          Удалить
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {editing && (
              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
                <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>{editing.id ? "Редактировать" : "Создать"}</h2>
                <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>ID (авто)</label>
                    <input
                      type="text"
                      value={editing.id || `forecast-${editing.date}-${editing.locale}`}
                      disabled
                      className="orbit-form"
                      style={{ width: "100%" }}
                    />
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--orbit-space-md)" }}>
                    <div>
                      <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Дата</label>
                      <input
                        type="date"
                        value={editing.date}
                        onChange={(e) => setEditing({ ...editing, date: e.target.value, id: editing.id || `forecast-${e.target.value}-${editing.locale}` })}
                        className="orbit-form"
                        style={{ width: "100%" }}
                      />
                    </div>
                    <div>
                      <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Язык</label>
                      <select
                        value={editing.locale}
                        onChange={(e) => setEditing({ ...editing, locale: e.target.value, id: editing.id || `forecast-${editing.date}-${e.target.value}` })}
                        className="orbit-form"
                        style={{ width: "100%" }}
                      >
                        <option value="ru">RU</option>
                        <option value="en">EN</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>
                      <input type="checkbox" checked={editing.published} onChange={(e) => setEditing({ ...editing, published: e.target.checked })} /> Опубликован
                    </label>
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Theme</label>
                    <textarea
                      value={editing.blocks.theme}
                      onChange={(e) => setEditing({ ...editing, blocks: { ...editing.blocks, theme: e.target.value } })}
                      className="orbit-form orbit-form-textarea"
                      style={{ width: "100%", minHeight: "80px" }}
                    />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Notice (по одному на строку)</label>
                    <textarea
                      value={editing.blocks.notice.join("\n")}
                      onChange={(e) =>
                        setEditing({
                          ...editing,
                          blocks: { ...editing.blocks, notice: e.target.value.split("\n").filter((x) => x.trim()) },
                        })
                      }
                      className="orbit-form orbit-form-textarea"
                      style={{ width: "100%", minHeight: "100px" }}
                    />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Scene (по одному на строку)</label>
                    <textarea
                      value={editing.blocks.scene.join("\n")}
                      onChange={(e) =>
                        setEditing({
                          ...editing,
                          blocks: { ...editing.blocks, scene: e.target.value.split("\n").filter((x) => x.trim()) },
                        })
                      }
                      className="orbit-form orbit-form-textarea"
                      style={{ width: "100%", minHeight: "100px" }}
                    />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Micro Action</label>
                    <textarea
                      value={editing.blocks.micro_action}
                      onChange={(e) => setEditing({ ...editing, blocks: { ...editing.blocks, micro_action: e.target.value } })}
                      className="orbit-form orbit-form-textarea"
                      style={{ width: "100%", minHeight: "60px" }}
                    />
                  </div>
                  <div>
                    <label className="orbit-body-sm" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>Теги (через запятую)</label>
                    <input
                      type="text"
                      value={editing.tags.join(", ")}
                      onChange={(e) => setEditing({ ...editing, tags: e.target.value.split(",").map((x) => x.trim()).filter((x) => x) })}
                      className="orbit-form"
                      style={{ width: "100%" }}
                    />
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

            {selected && !editing && (
              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
                <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>Просмотр</h2>
                <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                  <div>
                    <strong className="orbit-body-sm">{selected.date}</strong> <span className="orbit-body-xs">{selected.locale}</span>
                    {selected.published ? <span className="orbit-badge-xs">Опубликован</span> : <span className="orbit-badge-xs orbit-badge-xs--muted">Черновик</span>}
                  </div>
                  {selected._quality_gate_errors && selected._quality_gate_errors.length > 0 && (
                    <div style={{ padding: "var(--orbit-space-md)", background: "#fee2e2", borderRadius: "var(--orbit-radius-md)" }}>
                      <strong className="orbit-body-sm">Ошибки Quality Gate:</strong>
                      <ul style={{ marginTop: "var(--orbit-space-xs)" }}>
                        {selected._quality_gate_errors.map((err, i) => (
                          <li key={i} className="orbit-body-xs">{err}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div>
                    <strong className="orbit-body-sm">Theme:</strong>
                    <p className="orbit-body">{selected.blocks.theme}</p>
                  </div>
                  <div>
                    <strong className="orbit-body-sm">Notice:</strong>
                    <ul>
                      {selected.blocks.notice.map((n, i) => (
                        <li key={i} className="orbit-body">{n}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <strong className="orbit-body-sm">Scene:</strong>
                    <ul>
                      {selected.blocks.scene.map((s, i) => (
                        <li key={i} className="orbit-body">{s}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <strong className="orbit-body-sm">Micro Action:</strong>
                    <p className="orbit-body">{selected.blocks.micro_action}</p>
                  </div>
                  <div>
                    <strong className="orbit-body-sm">Маркеры:</strong>
                    <div className="orbit-body-xs">
                      Body: {selected.markers.body.join(", ") || "—"}
                      <br />
                      Social: {selected.markers.social.join(", ") || "—"}
                      <br />
                      Domestic: {selected.markers.domestic.join(", ") || "—"}
                      <br />
                      Micro Action: {selected.markers.micro_action.join(", ") || "—"}
                    </div>
                  </div>
                  <div>
                    <strong className="orbit-body-sm">Теги:</strong>
                    <p className="orbit-body">{selected.tags.join(", ") || "—"}</p>
                  </div>
                  <div style={{ display: "flex", gap: "var(--orbit-space-md)" }}>
                    <button className="orbit-button orbit-button-secondary" onClick={() => handleEdit(selected)}>
                      Редактировать
                    </button>
                    <button className="orbit-button orbit-button-secondary" onClick={() => setSelected(null)}>
                      Закрыть
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
