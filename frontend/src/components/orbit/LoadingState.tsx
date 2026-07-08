import React from "react";
import { LoadingSpinner } from "./LoadingSpinner";

interface LoadingStateProps {
  text?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function LoadingState({
  text,
  size = "md",
  className = "",
}: LoadingStateProps) {
  return (
    <div className={`orbit-loading-state ${className}`}>
      <div className="orbit-loading-state__spinner">
        <LoadingSpinner size={size} />
      </div>
      {text && (
        <p className="orbit-loading-state__text">{text}</p>
      )}
    </div>
  );
}

