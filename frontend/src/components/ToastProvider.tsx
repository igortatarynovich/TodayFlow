"use client";

import { createContext, useContext, ReactNode } from "react";
import { ToastContainer, useToast as useToastHook, type Toast } from "@/components/orbit";

const ToastContext = createContext<ReturnType<typeof useToastHook> | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const toast = useToastHook();

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastContainer toasts={toast.toasts} onClose={toast.removeToast} />
    </ToastContext.Provider>
  );
}

export function useToastContext() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToastContext must be used within ToastProvider");
  }
  return context;
}

// Alias for convenience
export const useToast = useToastContext;

