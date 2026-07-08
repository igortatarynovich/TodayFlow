"use client";

import { Modality, modalityNames, getModality } from "@/lib/zodiac-utils";

interface ModalityBalanceProps {
  signs: string[];
  isGuest?: boolean;
}

export function ModalityBalance({ signs, isGuest = false }: ModalityBalanceProps) {
  const modalities: Modality[] = ["Cardinal", "Fixed", "Mutable"];

  // Вычисляем реальный баланс модальностей из знаков пользователя
  // Логика: считаем, сколько знаков каждой модальности в Core Trio (Солнце, Луна, Асцендент)
  const totalSigns = signs.length || 1;
  const modalityCounts = modalities.reduce((acc, modality) => {
    acc[modality] = signs.filter(sign => {
      const signModality = getModality(sign);
      return signModality === modality;
    }).length;
    return acc;
  }, {} as Record<Modality, number>);

  return (
    <div
      style={{
        marginBottom: "var(--orbit-space-xl)",
      }}
    >
      <h3
        className="orbit-body"
        style={{
          marginBottom: "var(--orbit-space-md)",
          color: "#0f172a",
          fontWeight: 500,
        }}
      >
        Стиль движения
      </h3>
      <div
        style={{
          display: "flex",
          gap: "var(--orbit-space-md)",
          alignItems: "flex-end",
          height: "80px",
        }}
      >
        {modalities.map((modality) => {
          const count = modalityCounts[modality];
          const percentage = (count / totalSigns) * 100;
          const height = Math.max(15, percentage); // Минимум 15% для видимости

          return (
            <div
              key={modality}
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "var(--orbit-space-xs)",
              }}
              title={`${modalityNames[modality]}: ${count} из ${totalSigns} (${Math.round(percentage)}%)`}
            >
              <div
                style={{
                  width: "100%",
                  height: `${height}%`,
                  backgroundColor: isGuest ? "#e5e0d8" : "#6b7280",
                  borderRadius: "4px 4px 0 0",
                  transition: "all 0.3s ease",
                  opacity: isGuest ? 0.5 : 1,
                  minHeight: "15px",
                  display: "flex",
                  alignItems: "flex-end",
                  justifyContent: "center",
                  paddingBottom: "4px",
                }}
              >
                {!isGuest && count > 0 && (
                  <span
                    className="orbit-body-xs"
                    style={{
                      color: "#ffffff",
                      fontWeight: 600,
                    }}
                  >
                    {count}
                  </span>
                )}
              </div>
              <span
                className="orbit-body-sm"
                style={{
                  color: "#334155",
                  opacity: isGuest ? 0.6 : 1,
                  fontWeight: count > 0 ? 500 : 400,
                  textAlign: "center",
                }}
              >
                {modalityNames[modality]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

