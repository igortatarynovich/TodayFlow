const FIRST_TODAY_STORAGE_KEY = "todayflow_first_today_v1";

export type FirstTodayState = {
  completed_at?: string;
  day_key?: string;
  profile_depth_unlocked?: boolean;
};

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function readFirstTodayState(): FirstTodayState {
  if (!isBrowser()) return {};
  try {
    const raw = localStorage.getItem(FIRST_TODAY_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as FirstTodayState;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function writeFirstTodayState(next: FirstTodayState): void {
  if (!isBrowser()) return;
  localStorage.setItem(FIRST_TODAY_STORAGE_KEY, JSON.stringify(next));
}

export function markFirstTodayCompleted(dayKey?: string): FirstTodayState {
  const next: FirstTodayState = {
    ...readFirstTodayState(),
    completed_at: new Date().toISOString(),
    day_key: dayKey,
  };
  writeFirstTodayState(next);
  return next;
}

export function markProfileDepthUnlocked(): FirstTodayState {
  const next: FirstTodayState = {
    ...readFirstTodayState(),
    profile_depth_unlocked: true,
  };
  writeFirstTodayState(next);
  return next;
}

export function hasCompletedFirstToday(state = readFirstTodayState()): boolean {
  return Boolean(state.completed_at?.trim());
}

export function hasProfileDepthUnlocked(state = readFirstTodayState()): boolean {
  return Boolean(state.profile_depth_unlocked);
}

export function shouldShowProfileTeaser(state = readFirstTodayState()): boolean {
  return hasCompletedFirstToday(state) && !hasProfileDepthUnlocked(state);
}

export const FIRST_TODAY_PATH = "/today?first=1";
