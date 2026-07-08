"use client";

import styles from "./LoadingSpinner.module.css";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function LoadingSpinner({ size = "md", className = "" }: LoadingSpinnerProps) {
  return (
    <div className={`${styles.spinner} ${styles[`spinner--${size}`]} ${className}`} aria-label="Loading">
      <div className={styles.spinner__circle}></div>
    </div>
  );
}

