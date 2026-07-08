/**
 * Утилиты для определения состояния Dashboard (STATE MACHINE)
 * Используется для адаптации Dashboard под ритуал дня
 * 
 * Приоритеты определения состояния:
 * 1. Ручной override (редко, опционально)
 * 2. Последнее действие пользователя сегодня
 * 3. Время суток
 * 
 * Поведение пользователя важнее времени!
 */

export type TimeOfDay = "morning" | "day" | "evening";

/**
 * Состояние дня пользователя
 */
export interface DayState {
  date: string; // YYYY-MM-DD
  morning_opened: boolean;
  morning_action_done: boolean;
  day_action_done: boolean;
  evening_reflection_done: boolean;
  current_state: TimeOfDay;
}

/**
 * Определяет время суток по текущему времени (технические границы)
 * 
 * Утро: 05:00-11:00
 * День: 11:00-18:00
 * Вечер: после 18:00 или до 05:00
 */
export function getTimeOfDayByHour(): TimeOfDay {
  const hour = new Date().getHours();
  
  if (hour >= 5 && hour < 11) {
    return "morning";
  }
  
  if (hour >= 11 && hour < 18) {
    return "day";
  }
  
  return "evening";
}

/**
 * Получает состояние дня пользователя из localStorage
 * 
 * @param userId - ID пользователя
 * @returns состояние дня или null, если нет данных
 */
export function getDayState(userId: string | number | null | undefined): DayState | null {
  if (!userId) return null;
  
  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const key = `day_state_${userId}_${today}`;
  const stored = localStorage.getItem(key);
  
  if (!stored) return null;
  
  try {
    return JSON.parse(stored) as DayState;
  } catch {
    return null;
  }
}

/**
 * Сохраняет состояние дня пользователя в localStorage
 * 
 * @param userId - ID пользователя
 * @param state - состояние дня
 */
export function saveDayState(userId: string | number | null | undefined, state: DayState): void {
  if (!userId) return;
  
  const key = `day_state_${userId}_${state.date}`;
  localStorage.setItem(key, JSON.stringify(state));
}

/**
 * Инициализирует новое состояние дня
 * 
 * @param userId - ID пользователя
 * @returns новое состояние дня
 */
export function initDayState(userId: string | number | null | undefined): DayState {
  const today = new Date().toISOString().split('T')[0];
  const timeOfDay = getTimeOfDayByHour();
  
  return {
    date: today,
    morning_opened: true,
    morning_action_done: false,
    day_action_done: false,
    evening_reflection_done: false,
    current_state: "morning", // Первый заход всегда MORNING
  };
}

/**
 * Определяет текущее состояние Dashboard на основе логики state machine
 * 
 * Приоритеты:
 * 1. Если вечерняя фиксация сделана → EVENING (read-only)
 * 2. Если утреннее действие сделано → DAY (или EVENING если время >= 18:00)
 * 3. Если это первый заход сегодня → MORNING
 * 4. Если утро уже было → DAY (или EVENING если время >= 18:00)
 * 5. По времени суток
 * 
 * @param userId - ID пользователя
 * @returns текущее состояние Dashboard
 */
export function getDashboardState(userId: string | number | null | undefined): TimeOfDay {
  if (!userId) {
    // Для гостей используем только время суток
    return getTimeOfDayByHour();
  }
  
  const today = new Date().toISOString().split('T')[0];
  let state = getDayState(userId);
  
  // Если нет состояния или это новый день → инициализируем
  if (!state || state.date !== today) {
    state = initDayState(userId);
    saveDayState(userId, state);
  }
  
  // 1. Если вечерняя фиксация сделана → EVENING (read-only)
  if (state.evening_reflection_done) {
    return "evening";
  }
  
  // 2. Если утреннее действие сделано → переходим в DAY или EVENING
  if (state.morning_action_done) {
    const timeOfDay = getTimeOfDayByHour();
    // Если время >= 18:00, переходим в EVENING
    if (timeOfDay === "evening") {
      // Обновляем состояние, но не помечаем как завершённое
      if (state.current_state !== "evening") {
        state.current_state = "evening";
        saveDayState(userId, state);
      }
      return "evening";
    }
    // Иначе остаёмся в DAY
    if (state.current_state !== "day") {
      state.current_state = "day";
      saveDayState(userId, state);
    }
    return "day";
  }
  
  // 3. Если это первый заход сегодня → MORNING (независимо от времени)
  if (!state.morning_opened) {
    state.morning_opened = true;
    state.current_state = "morning";
    saveDayState(userId, state);
    return "morning";
  }
  
  // 4. Если утро уже было, но действие не сделано → DAY (или EVENING если время >= 18:00)
  if (state.morning_opened && !state.morning_action_done) {
    const timeOfDay = getTimeOfDayByHour();
    if (timeOfDay === "evening") {
      if (state.current_state !== "evening") {
        state.current_state = "evening";
        saveDayState(userId, state);
      }
      return "evening";
    }
    // Мягкий переход в DAY, даже если утреннее действие не сделано
    if (state.current_state !== "day") {
      state.current_state = "day";
      saveDayState(userId, state);
    }
    return "day";
  }
  
  // 5. По времени суток (fallback)
  const timeOfDay = getTimeOfDayByHour();
  if (state.current_state !== timeOfDay) {
    state.current_state = timeOfDay;
    saveDayState(userId, state);
  }
  return timeOfDay;
}

/**
 * Отмечает утреннее действие как выполненное
 * 
 * @param userId - ID пользователя
 */
export function markMorningActionDone(userId: string | number | null | undefined): void {
  if (!userId) return;
  
  const state = getDayState(userId);
  if (!state) return;
  
  const today = new Date().toISOString().split('T')[0];
  if (state.date !== today) {
    // Новый день, инициализируем
    const newState = initDayState(userId);
    newState.morning_action_done = true;
    newState.current_state = "day";
    saveDayState(userId, newState);
    return;
  }
  
  state.morning_action_done = true;
  state.current_state = "day";
  saveDayState(userId, state);
}

/**
 * Отмечает вечернюю фиксацию как выполненную
 * 
 * @param userId - ID пользователя
 */
export function markEveningReflectionDone(userId: string | number | null | undefined): void {
  if (!userId) return;
  
  const state = getDayState(userId);
  if (!state) return;
  
  const today = new Date().toISOString().split('T')[0];
  if (state.date !== today) {
    // Новый день, инициализируем
    const newState = initDayState(userId);
    newState.evening_reflection_done = true;
    newState.current_state = "evening";
    saveDayState(userId, newState);
    return;
  }
  
  state.evening_reflection_done = true;
  state.current_state = "evening";
  saveDayState(userId, state);
}

/**
 * Проверяет, завершён ли день (вечерняя фиксация сделана)
 * 
 * @param userId - ID пользователя
 * @returns true, если день завершён
 */
export function isDayCompleted(userId: string | number | null | undefined): boolean {
  if (!userId) return false;
  
  const state = getDayState(userId);
  if (!state) return false;
  
  const today = new Date().toISOString().split('T')[0];
  if (state.date !== today) return false;
  
  return state.evening_reflection_done;
}

// DEPRECATED: Используйте getDashboardState вместо этих функций
// Оставлены для обратной совместимости

/**
 * @deprecated Используйте getDashboardState
 */
export function getTimeOfDay(): TimeOfDay {
  return getTimeOfDayByHour();
}

/**
 * @deprecated Используйте getDashboardState
 */
export function isFirstVisitToday(userId: string | number | null | undefined): boolean {
  if (!userId) return false;
  
  const state = getDayState(userId);
  if (!state) return true; // Нет состояния = первый заход
  
  const today = new Date().toISOString().split('T')[0];
  return state.date !== today || !state.morning_opened;
}

/**
 * @deprecated Используйте getDashboardState
 */
export function getTimeContext(userId: string | number | null | undefined): {
  timeOfDay: TimeOfDay;
  isFirstVisit: boolean;
} {
  return {
    timeOfDay: getDashboardState(userId),
    isFirstVisit: isFirstVisitToday(userId),
  };
}

/**
 * @deprecated Используйте getDashboardState
 */
export function shouldShowMorningMode(userId: string | number | null | undefined): boolean {
  return getDashboardState(userId) === "morning";
}

