"use client";

interface AccountHeaderProps {
  todayDate: string;
  timeframe: "today" | "month" | "year";
  onTimeframeChange: (value: "today" | "month" | "year") => void;
  showContent: boolean;
}

export function AccountHeader({
  todayDate,
  timeframe,
  onTimeframeChange,
  showContent,
}: AccountHeaderProps) {
  return (
    <section className="orbit-account-header">
      <div className="orbit-account-header-container">
        <h1 
          className="orbit-account-title"
          style={{
            opacity: showContent ? 1 : 0,
            transform: showContent ? "translateY(0)" : "translateY(20px)",
            transition: "opacity 0.8s ease, transform 0.8s ease"
          }}
        >
          Личный кабинет
        </h1>
        
        <div className="orbit-account-panel">
          <div className="orbit-account-panel-item">
            <div className="orbit-account-panel-label">Овен</div>
            <div className="orbit-account-panel-lines">
              <div className="orbit-account-panel-line" />
              <div className="orbit-account-panel-line" />
              <div className="orbit-account-panel-line" />
            </div>
          </div>
          
          <div className="orbit-account-panel-item">
            <div className="orbit-account-panel-label">Дракон</div>
            <div className="orbit-account-panel-lines">
              <div className="orbit-account-panel-line" />
              <div className="orbit-account-panel-line" />
            </div>
          </div>
          
          <div className="orbit-account-panel-item">
            <div className="orbit-account-panel-label">Число 9</div>
            <div className="orbit-account-panel-lines">
              <div className="orbit-account-panel-line" />
              <div className="orbit-account-panel-line" />
              <div className="orbit-account-panel-line" />
            </div>
          </div>
          
          <div className="orbit-account-panel-item orbit-account-panel-item-date">
            <div className="orbit-account-panel-label">Сегодня</div>
            <div className="orbit-account-panel-date">{todayDate}</div>
            <div className="orbit-account-panel-subitems">
              <div className="orbit-account-panel-subitem">
                <span className="orbit-body-sm">Общее предупреждение</span>
              </div>
              <div className="orbit-account-panel-subitem">
                <span className="orbit-body-sm">Аффирмация персонализированная</span>
              </div>
            </div>
          </div>
          
          <div className="orbit-account-panel-item orbit-account-panel-item-switch">
            <div className="orbit-account-panel-label">Период</div>
            <div className="orbit-account-panel-switch">
              <button
                type="button"
                className={`orbit-button orbit-button-xs ${timeframe === "today" ? "orbit-button-primary" : "orbit-button-secondary"}`}
                onClick={() => onTimeframeChange("today")}
              >
                День
              </button>
              <button
                type="button"
                className={`orbit-button orbit-button-xs ${timeframe === "month" ? "orbit-button-primary" : "orbit-button-secondary"}`}
                onClick={() => onTimeframeChange("month")}
              >
                Месяц
              </button>
              <button
                type="button"
                className={`orbit-button orbit-button-xs ${timeframe === "year" ? "orbit-button-primary" : "orbit-button-secondary"}`}
                onClick={() => onTimeframeChange("year")}
              >
                Год
              </button>
            </div>
            <div className="orbit-account-panel-subitem" style={{ marginTop: "var(--orbit-space-sm)" }}>
              <span className="orbit-body-sm">Упражнение/совет</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

