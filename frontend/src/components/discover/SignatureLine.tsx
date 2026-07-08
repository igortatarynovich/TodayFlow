"use client";

interface SignatureLineProps {
  signature?: string;
  isGuest?: boolean;
  axes?: Array<{ axis_id: string; value: number }>;
  sun?: string;
  moon?: string;
  rising?: string;
}

/**
 * Генерирует Signature строку из Core Trio и осей
 * Если signature не предоставлена, генерирует из данных
 */
export function SignatureLine({ signature, isGuest = false, axes, sun, moon, rising }: SignatureLineProps) {
  // Если есть готовая signature, используем её
  if (signature) {
    return (
      <div
        style={{
          marginBottom: "var(--orbit-space-xl)",
          padding: "var(--orbit-space-lg)",
          textAlign: "center",
        }}
      >
        <p
          className="orbit-body"
          style={{
            fontSize: "1.25rem",
            lineHeight: 1.6,
            color: "#0f172a",
            fontStyle: "italic",
            opacity: isGuest ? 0.6 : 1,
            maxWidth: "800px",
            margin: "0 auto",
          }}
        >
          {signature}
        </p>
      </div>
    );
  }

  // Генерируем простую signature из доступных данных
  const parts: string[] = [];

  if (sun) {
    parts.push(`Солнце в ${sun}`);
  }
  if (moon) {
    parts.push(`Луна в ${moon}`);
  }
  if (rising) {
    parts.push(`Асцендент в ${rising}`);
  }

  // Добавляем информацию об осях, если есть
  if (axes && axes.length > 0) {
    const topAxis = axes
      .map((a) => ({ ...a, absValue: Math.abs(a.value) }))
      .sort((a, b) => b.absValue - a.absValue)[0];

    if (topAxis) {
      const axisNames: Record<string, string> = {
        A1: "ориентация",
        A2: "эмоции",
        A3: "решения",
        A4: "изменения",
        A5: "контроль",
        A6: "отношения",
        A7: "энергия",
      };
      parts.push(axisNames[topAxis.axis_id] || topAxis.axis_id);
    }
  }

  const generatedSignature = parts.length > 0
    ? `Твоя личность формируется через ${parts.slice(0, 3).join(", ")}.`
    : "Твоя уникальная карта личности";

  return (
    <div
      style={{
        marginBottom: "var(--orbit-space-xl)",
        padding: "var(--orbit-space-lg)",
        textAlign: "center",
      }}
    >
      <p
        className="orbit-body"
        style={{
          fontSize: "1.25rem",
          lineHeight: 1.6,
          color: "#0f172a",
          fontStyle: "italic",
          opacity: isGuest ? 0.6 : 1,
          maxWidth: "800px",
          margin: "0 auto",
        }}
      >
        {generatedSignature}
      </p>
    </div>
  );
}

