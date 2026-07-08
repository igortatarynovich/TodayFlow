"use client";

import type { ReactNode } from "react";
import styles from "./conversation.module.css";

type Props = {
  children: ReactNode;
  className?: string;
  testId?: string;
};

export function ConversationThread({ children, className = "", testId = "conversation-thread" }: Props) {
  return (
    <div className={`${styles.thread} ${className}`.trim()} data-testid={testId}>
      {children}
    </div>
  );
}
