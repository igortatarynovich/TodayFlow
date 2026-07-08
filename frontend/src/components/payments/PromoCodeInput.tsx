"use client";

import { useState } from "react";
import { postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { LoadingSpinner } from "@/components/orbit";

interface PromoCodeInputProps {
  onValidated?: (code: string, discount: { discount_amount: number; final_amount: number }) => void;
  onRemoved?: () => void;
  productType?: "subscription" | "report";
  amount?: number; // Amount in cents
}

export function PromoCodeInput({ onValidated, onRemoved, productType, amount }: PromoCodeInputProps) {
  const toast = useToast();
  const [code, setCode] = useState("");
  const [validating, setValidating] = useState(false);
  const [validatedCode, setValidatedCode] = useState<string | null>(null);
  const [discount, setDiscount] = useState<{ discount_amount: number; final_amount: number } | null>(null);

  const handleValidate = async () => {
    if (!code.trim()) {
      toast.error("Введите промокод");
      return;
    }

    setValidating(true);
    try {
      const response = await postJson<{
        code: string;
        discount_type: string;
        discount_value: number;
        discount_amount: number;
        final_amount: number;
        description?: string;
      }>("/promo-codes/validate", {
        code: code.trim(),
        product_type: productType,
        amount: amount,
      });

      setValidatedCode(response.code);
      setDiscount({
        discount_amount: response.discount_amount,
        final_amount: response.final_amount,
      });
      onValidated?.(response.code, {
        discount_amount: response.discount_amount,
        final_amount: response.final_amount,
      });
      toast.success(
        `Промокод применен! Скидка: ${(response.discount_amount / 100).toFixed(2)} ₽`
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Промокод недействителен";
      toast.error(errorMessage);
    } finally {
      setValidating(false);
    }
  };

  const handleRemove = () => {
    setCode("");
    setValidatedCode(null);
    setDiscount(null);
    onRemoved?.();
  };

  if (validatedCode && discount) {
    return (
      <div style={{ 
        padding: "var(--orbit-space-md)",
        background: "var(--orbit-color-mist)",
        borderRadius: "var(--orbit-radius-sm)",
        border: "1px solid var(--orbit-color-primary)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--orbit-space-xs)" }}>
          <div>
            <p className="orbit-body-sm" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)" }}>
              Промокод: {validatedCode}
            </p>
            <p className="orbit-body-xs orbit-text-muted">
              Скидка: <strong>{(discount.discount_amount / 100).toFixed(2)} ₽</strong>
            </p>
          </div>
          <button
            onClick={handleRemove}
            className="orbit-button orbit-button-secondary orbit-button-xs"
          >
            Удалить
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", gap: "var(--orbit-space-sm)" }}>
      <input
        type="text"
        value={code}
        onChange={(e) => setCode(e.target.value.toUpperCase())}
        placeholder="Введите промокод"
        className="orbit-input"
        style={{ flex: 1 }}
        onKeyPress={(e) => {
          if (e.key === "Enter") {
            handleValidate();
          }
        }}
        disabled={validating}
      />
      <button
        onClick={handleValidate}
        disabled={validating || !code.trim()}
        className="orbit-button orbit-button-secondary"
      >
        {validating ? (
          <>
            <LoadingSpinner size="sm" />
            <span style={{ marginLeft: "var(--orbit-space-xs)" }}>Проверка...</span>
          </>
        ) : (
          "Применить"
        )}
      </button>
    </div>
  );
}

