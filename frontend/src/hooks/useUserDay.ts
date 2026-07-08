import { useState, useEffect } from "react";

export function useUserDay(userId?: number) {
  const [userDay, setUserDay] = useState<number | null>(null);
  const [currentTimeMarker, setCurrentTimeMarker] = useState<string>("");

  useEffect(() => {
    if (!userId) return;

    // Вычисляем день пользователя (отсчет от регистрации)
    const firstVisitKey = `todayflow_first_visit_${userId}`;
    let firstVisitDate = localStorage.getItem(firstVisitKey);
    
    if (!firstVisitDate) {
      // Первый визит - сохраняем дату
      firstVisitDate = new Date().toISOString();
      localStorage.setItem(firstVisitKey, firstVisitDate);
      setUserDay(1);
    } else {
      // Вычисляем день от первого визита
      const registrationDate = new Date(firstVisitDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      registrationDate.setHours(0, 0, 0, 0);
      const diffTime = today.getTime() - registrationDate.getTime();
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1; // +1 потому что день 1 - это день регистрации
      const day = Math.min(Math.max(diffDays, 1), 7); // Ограничиваем 1-7 днями
      setUserDay(day);
    }
    
    // Устанавливаем маркер времени (сегодня, в течение дня, к вечеру)
    const hour = new Date().getHours();
    if (hour < 12) {
      setCurrentTimeMarker("Сегодня");
    } else if (hour < 18) {
      setCurrentTimeMarker("В течение дня");
    } else {
      setCurrentTimeMarker("К вечеру");
    }
  }, [userId]);

  return { userDay, currentTimeMarker };
}

