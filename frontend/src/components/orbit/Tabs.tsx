"use client";

import { useState, createContext, useContext } from "react";

interface TabsContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

interface TabsProps {
  children: React.ReactNode;
  defaultTab?: string;
  onTabChange?: (tabId: string) => void;
}

export function Tabs({ children, defaultTab, onTabChange }: TabsProps) {
  const [activeTab, setActiveTab] = useState<string>(defaultTab || "");

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (onTabChange) {
      onTabChange(tabId);
    }
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab: handleTabChange }}>
      <div>{children}</div>
    </TabsContext.Provider>
  );
}

interface TabListProps {
  children: React.ReactNode;
}

export function TabList({ children }: TabListProps) {
  return (
    <div style={{
      display: "flex",
      borderBottom: "2px solid var(--orbit-color-border)",
      marginBottom: "var(--orbit-space-lg)",
      gap: "var(--orbit-space-sm)"
    }}>
      {children}
    </div>
  );
}

interface TabProps {
  id: string;
  label: string;
}

export function Tab({ id, label }: TabProps) {
  const context = useContext(TabsContext);
  if (!context) throw new Error("Tab must be used within Tabs");

  const { activeTab, setActiveTab } = context;
  const isActive = activeTab === id;

  return (
    <button
      onClick={() => setActiveTab(id)}
      style={{
        padding: "var(--orbit-space-md) var(--orbit-space-lg)",
        background: "transparent",
        border: "none",
        borderBottom: isActive ? "2px solid var(--orbit-color-primary)" : "2px solid transparent",
        cursor: "pointer",
        fontSize: "var(--orbit-font-size-base)",
        fontWeight: isActive ? 600 : 400,
        color: isActive ? "var(--orbit-color-primary)" : "var(--orbit-color-text-secondary)",
        marginBottom: "-2px",
        transition: "all 0.2s"
      }}
    >
      {label}
    </button>
  );
}

interface TabPanelsProps {
  children: React.ReactNode;
}

export function TabPanels({ children }: TabPanelsProps) {
  return <div>{children}</div>;
}

interface TabPanelProps {
  id: string;
  children: React.ReactNode;
}

export function TabPanel({ id, children }: TabPanelProps) {
  const context = useContext(TabsContext);
  if (!context) throw new Error("TabPanel must be used within Tabs");

  const { activeTab } = context;
  if (activeTab !== id) return null;

  return (
    <div style={{
      padding: "var(--orbit-space-lg) 0"
    }}>
      {children}
    </div>
  );
}
