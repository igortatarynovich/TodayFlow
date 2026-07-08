"use client";

import Link from "next/link";
import { t } from "@/lib/i18n";

interface DemoPatternBlockProps {
  title: string;
  items: string[];
  examples?: string[];
  className?: string;
}

export function DemoPatternBlock({ title, items, examples, className = "" }: DemoPatternBlockProps) {
  return (
    <div 
      className={`orbit-card ${className}`}
      style={{ 
        padding: "var(--orbit-space-lg)",
        position: "relative",
        filter: "blur(2px)",
        opacity: 0.7,
        transition: "all 0.3s ease",
        cursor: "not-allowed",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.filter = "blur(1px)";
        e.currentTarget.style.opacity = "0.8";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.filter = "blur(2px)";
        e.currentTarget.style.opacity = "0.7";
      }}
    >
      {/* Иконка замка */}
      <div style={{
        position: "absolute",
        top: "var(--orbit-space-md)",
        right: "var(--orbit-space-md)",
        fontSize: "1.25rem",
        opacity: 0.6,
      }}>
        🔒
      </div>

      <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)", paddingRight: "2rem" }}>
        {title}
      </h3>
      
      <ul style={{ listStyle: "none", padding: 0, margin: "var(--orbit-space-sm) 0 0 0" }}>
        {items.map((item, idx) => (
          <li 
            key={idx}
            style={{ 
              marginBottom: "var(--orbit-space-xs)", 
              fontSize: "0.875rem", 
              color: "var(--orbit-color-slate)",
              position: "relative",
              paddingLeft: "1rem",
            }}
          >
            <span style={{ position: "absolute", left: 0 }}>•</span>
            {item}
          </li>
        ))}
      </ul>

      {/* Примеры текста (если есть) */}
      {examples && examples.length > 0 && (
        <div style={{
          marginTop: "var(--orbit-space-md)",
          padding: "var(--orbit-space-sm)",
          background: "rgba(0, 0, 0, 0.02)",
          borderRadius: "var(--orbit-radius-sm)",
          border: "1px dashed var(--orbit-color-border)",
        }}>
          <p style={{
            fontSize: "0.75rem",
            color: "var(--orbit-color-slate)",
            opacity: 0.6,
            fontStyle: "italic",
            lineHeight: 1.4,
          }}>
            {examples[0]}
          </p>
        </div>
      )}

      {/* Подсказка при hover */}
      <div style={{
        position: "absolute",
        bottom: "var(--orbit-space-sm)",
        left: "var(--orbit-space-md)",
        right: "var(--orbit-space-md)",
        fontSize: "0.7rem",
        color: "var(--orbit-color-coral)",
        textAlign: "center",
        opacity: 0.7,
        fontWeight: 500,
      }}>
        {t("profile.registerToSee", "Зарегистрируйся, чтобы увидеть")}
      </div>
    </div>
  );
}

