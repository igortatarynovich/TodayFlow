"use client";

import { useState } from "react";

interface AccordionItemProps {
  title: string | React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export function AccordionItem({ title, children, defaultOpen = false }: AccordionItemProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div style={{
      border: "1px solid var(--orbit-color-border)",
      borderRadius: "var(--orbit-border-radius-md)",
      marginBottom: "var(--orbit-space-md)",
      overflow: "hidden"
    }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: "100%",
          padding: "var(--orbit-space-md) var(--orbit-space-lg)",
          background: isOpen ? "var(--orbit-color-surface-subtle)" : "var(--orbit-color-surface)",
          border: "none",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "var(--orbit-font-size-base)",
          fontWeight: 600,
          textAlign: "left",
          transition: "background 0.2s"
        }}
      >
        {title}
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          style={{
            transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.2s",
            flexShrink: 0,
            marginLeft: "var(--orbit-space-md)"
          }}
        >
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>
      {isOpen && (
        <div style={{
          padding: "var(--orbit-space-lg)",
          background: "var(--orbit-color-surface)",
          borderTop: "1px solid var(--orbit-color-border)"
        }}>
          {children}
        </div>
      )}
    </div>
  );
}

interface AccordionProps {
  children: React.ReactNode;
}

export function Accordion({ children }: AccordionProps) {
  return <div>{children}</div>;
}

