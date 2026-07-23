"use client";

import { CityAutocompleteInput } from "@/components/CityAutocompleteInput";

export type BirthProfileIntakeValues = {
  label: string;
  birth_date: string;
  birth_time: string;
  time_unknown: boolean;
  location_name: string;
  latitude: number | null;
  longitude: number | null;
};

type Props = {
  title?: string;
  values: BirthProfileIntakeValues;
  onChange: (next: BirthProfileIntakeValues) => void;
  /** Show label/name field */
  showLabel?: boolean;
  labelPlaceholder?: string;
  disabled?: boolean;
  className?: string;
};

/** Shared intake fields for 1A/1B/Scenario-2 — date required; time/place optional but paired. */
export function BirthProfileIntakeFields({
  title,
  values,
  onChange,
  showLabel = true,
  labelPlaceholder = "Имя или подпись",
  disabled = false,
  className,
}: Props) {
  const patch = (partial: Partial<BirthProfileIntakeValues>) => onChange({ ...values, ...partial });

  return (
    <section className={className} style={{ display: "grid", gap: "0.85rem" }}>
      {title ? (
        <p
          className="orbit-body-xs"
          style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}
        >
          {title}
        </p>
      ) : null}

      {showLabel ? (
        <label style={{ display: "grid", gap: "0.35rem" }}>
          <span className="orbit-body-sm">Имя или подпись</span>
          <input
            type="text"
            value={values.label}
            onChange={(e) => patch({ label: e.target.value })}
            placeholder={labelPlaceholder}
            disabled={disabled}
            className="orbit-input"
          />
        </label>
      ) : null}

      <label style={{ display: "grid", gap: "0.35rem" }}>
        <span className="orbit-body-sm">Дата рождения</span>
        <input
          type="date"
          value={values.birth_date}
          onChange={(e) => patch({ birth_date: e.target.value })}
          required
          disabled={disabled}
          className="orbit-input"
        />
      </label>

      <div style={{ display: "grid", gap: "0.6rem" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "0.55rem" }}>
          <input
            type="checkbox"
            checked={!values.time_unknown}
            onChange={(e) =>
              patch({
                time_unknown: !e.target.checked,
                birth_time: e.target.checked ? values.birth_time : "",
              })
            }
            disabled={disabled}
          />
          <span className="orbit-body-sm">Знаю время рождения</span>
        </label>
        {!values.time_unknown ? (
          <label style={{ display: "grid", gap: "0.35rem" }}>
            <span className="orbit-body-sm">Время рождения</span>
            <input
              type="time"
              value={values.birth_time}
              onChange={(e) => patch({ birth_time: e.target.value })}
              disabled={disabled}
              className="orbit-input"
            />
          </label>
        ) : null}
      </div>

      <label style={{ display: "grid", gap: "0.35rem" }}>
        <span className="orbit-body-sm">
          Место рождения{!values.time_unknown ? " (нужно для Асцендента и домов)" : " (опционально)"}
        </span>
        <CityAutocompleteInput
          value={values.location_name}
          onChange={(value) => patch({ location_name: value, latitude: null, longitude: null })}
          onSelect={(item) =>
            patch({
              location_name: (item.local_name || item.name || "").trim(),
              latitude: item.latitude,
              longitude: item.longitude,
            })
          }
          placeholder="Город, страна"
          disabled={disabled}
        />
      </label>
    </section>
  );
}
