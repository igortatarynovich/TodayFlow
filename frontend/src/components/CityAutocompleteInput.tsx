"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { getJson } from "@/lib/api";
import type { GeocodeResult } from "@/lib/types";

type CityAutocompleteInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSelect: (item: GeocodeResult) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
};

export function CityAutocompleteInput({
  value,
  onChange,
  onSelect,
  placeholder,
  disabled,
  required,
}: CityAutocompleteInputProps) {
  const [suggestions, setSuggestions] = useState<GeocodeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (disabled) {
      setSuggestions([]);
      setOpen(false);
      return;
    }
    const query = value.trim();
    if (query.length < 2) {
      setSuggestions([]);
      setOpen(false);
      return;
    }

    const timeout = window.setTimeout(async () => {
      try {
        setLoading(true);
        setFetchError(null);
        const items = await getJson<GeocodeResult[]>(`/astro/geocode/suggest?q=${encodeURIComponent(query)}&limit=8`);
        setSuggestions(Array.isArray(items) ? items : []);
        setOpen(true);
      } catch {
        setSuggestions([]);
        setFetchError("Не удалось найти города. Проверь, что сервер запущен, и попробуй ещё раз.");
        setOpen(true);
      } finally {
        setLoading(false);
      }
    }, 220);

    return () => window.clearTimeout(timeout);
  }, [value, disabled]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const visibleSuggestions = useMemo(() => suggestions.slice(0, 8), [suggestions]);

  return (
    <div ref={rootRef} style={{ position: "relative" }}>
      <input
        type="text"
        value={value}
        onChange={(event) => {
          onChange(event.target.value);
          setFetchError(null);
          setOpen(true);
        }}
        onFocus={() => {
          if (visibleSuggestions.length > 0) {
            setOpen(true);
          }
        }}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
      />
      <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#64748b" }}>
        Можно вводить на русском или English.
      </p>
      {fetchError ? (
        <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#b45309" }}>
          {fetchError}
        </p>
      ) : null}
      {open && (visibleSuggestions.length > 0 || loading || fetchError) ? (
        <div
          style={{
            position: "absolute",
            zIndex: 30,
            top: "calc(100% + 0.45rem)",
            left: 0,
            right: 0,
            border: "1px solid #e6dccf",
            background: "rgba(255,255,255,0.98)",
            borderRadius: "18px",
            boxShadow: "0 18px 40px rgba(15, 23, 42, 0.08)",
            overflow: "hidden",
            backdropFilter: "blur(18px)",
          }}
        >
          {loading ? (
            <div style={{ padding: "0.85rem 0.9rem", color: "#64748b", fontSize: "0.9rem" }}>Ищу города…</div>
          ) : fetchError ? (
            <div style={{ padding: "0.85rem 0.9rem", color: "#b45309", fontSize: "0.9rem" }}>{fetchError}</div>
          ) : (
            visibleSuggestions.map((item) => (
              <button
                key={`${item.name}-${item.country}`}
                type="button"
                onClick={() => {
                  onChange(item.display_name || item.local_name || item.name);
                  onSelect(item);
                  setOpen(false);
                }}
                style={{
                  width: "100%",
                  textAlign: "left",
                  border: "none",
                  background: "transparent",
                  padding: "0.8rem 0.9rem",
                  cursor: "pointer",
                  borderBottom: "1px solid rgba(230, 220, 207, 0.65)",
                }}
              >
                <div style={{ fontWeight: 600, color: "#1f2937" }}>
                  {item.local_name && item.local_name !== item.name ? `${item.local_name} / ${item.name}` : item.name}
                </div>
                <div style={{ marginTop: "0.15rem", fontSize: "0.84rem", color: "#64748b" }}>{item.country}</div>
              </button>
            ))
          )}
        </div>
      ) : null}
    </div>
  );
}
