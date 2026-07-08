export default function PrivacyPage() {
  return (
    <main className="orbit-page todayflow-serene" style={{ maxWidth: "920px", margin: "0 auto", padding: "2rem 1rem 3rem" }}>
      <h1 className="orbit-display-sm" style={{ margin: 0 }}>Политика конфиденциальности</h1>
      <p className="orbit-body" style={{ marginTop: "0.8rem", color: "#475569", lineHeight: 1.7 }}>
        TodayFlow хранит учетные и профильные данные пользователя для персонализации рекомендаций.
        Данные не передаются третьим лицам за пределами необходимых сервисов инфраструктуры и обработки запросов.
      </p>
      <p className="orbit-body" style={{ marginTop: "0.6rem", color: "#475569", lineHeight: 1.7 }}>
        Пользователь может обновить или удалить часть данных через настройки аккаунта. При использовании
        расширенных функций TodayFlow отдельные запросы могут обрабатываться внешними провайдерами в рамках
        политики безопасности сервиса.
      </p>
    </main>
  );
}
