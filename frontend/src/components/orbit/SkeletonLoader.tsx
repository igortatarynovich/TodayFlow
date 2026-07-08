"use client";

import styles from "./SkeletonLoader.module.css";

interface SkeletonLoaderProps {
  width?: string;
  height?: string;
  className?: string;
  lines?: number;
}

export function SkeletonLoader({ width, height, lines = 1, className = "" }: SkeletonLoaderProps) {
  if (lines > 1) {
    return (
      <div className={`${styles.skeletonContainer} ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={styles.skeleton}
            aria-label="Loading content"
            style={{
              width: width || "100%",
              height: height || "1rem",
              marginBottom: i < lines - 1 ? "0.5rem" : "0",
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={`${styles.skeleton} ${className}`}
      style={{
        width: width || "100%",
        height: height || "1rem",
      }}
      aria-label="Loading content"
    />
  );
}

