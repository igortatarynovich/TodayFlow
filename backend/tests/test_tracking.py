"""Tests for tracking API endpoints - контур влияния."""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User
from todayflow_backend.services.auth import hash_password


@pytest.fixture
def test_tracking_user(db_session: Session) -> User:
    """Создаёт тестового пользователя для трекинга."""
    user = User(
        email="test_tracking@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token_tracking(client, test_tracking_user):
    """Получает токен авторизации для тестового пользователя."""
    # Создаём пользователя через signup
    signup_data = {
        "email": test_tracking_user.email,
        "password": "testpassword123"
    }
    client.post("/auth/signup", json=signup_data)
    
    # Логинимся и получаем токен
    response = client.post("/auth/login", json=signup_data)
    if response.status_code == 200:
        return response.json().get("token")
    return None


@pytest.fixture
def auth_headers(auth_token_tracking):
    """Возвращает заголовки авторизации."""
    if auth_token_tracking:
        return {"Authorization": f"Bearer {auth_token_tracking}"}
    return {}


class TestProgressTracker:
    """Тесты для прогресс-трекера."""
    
    def test_create_progress_entry(self, client, test_tracking_user, auth_headers, db_session):
        """Тест создания записи в прогресс-трекере."""
        entry_data = {
            "date": "2026-01-25",
            "asceticism_id": "asceticism.001",
            "affirmation_id": "practice.101",
            "completed": True,
            "state": "calm",
            "state_scale": 4,
            "note": "Тестовая запись"
        }
        
        response = client.post(
            "/tracking/progress",
            json=entry_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["date"] == entry_data["date"]
        assert data["completed"] == entry_data["completed"]
        assert data["state"] == entry_data["state"]
        assert data["state_scale"] == entry_data["state_scale"]
    
    def test_get_progress_entries(self, client, test_tracking_user, auth_headers, db_session):
        """Тест получения записей прогресс-трекера."""
        # Создаём несколько записей
        for i in range(3):
            entry_data = {
                "date": (date.today() - timedelta(days=i)).isoformat(),
                "affirmation_id": f"practice.{100+i}",
                "completed": True,
                "state": "calm"
            }
            client.post("/tracking/progress", json=entry_data, headers=auth_headers)
        
        # Получаем записи
        response = client.get(
            "/tracking/progress",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3


class TestObservationDiary:
    """Тесты для дневника наблюдений."""
    
    def test_create_diary_entry(self, client, test_tracking_user, auth_headers, db_session):
        """Тест создания записи в дневнике наблюдений."""
        entry_data = {
            "date": "2026-01-25",
            "noticed": "Заметил, что утром хочется сразу проверить сообщения.",
            "hardest": "Сложнее всего было не переключаться между задачами.",
            "easier_than_expected": "Оказалось легче, чем ожидал — просто остановиться на 30 секунд."
        }
        
        response = client.post(
            "/tracking/diary",
            json=entry_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["date"] == entry_data["date"]
        assert data["noticed"] == entry_data["noticed"]
        assert data["hardest"] == entry_data["hardest"]
        assert data["easier_than_expected"] == entry_data["easier_than_expected"]
    
    def test_get_diary_entries(self, client, test_tracking_user, auth_headers, db_session):
        """Тест получения записей дневника."""
        # Создаём запись
        entry_data = {
            "date": "2026-01-25",
            "noticed": "Тест",
            "hardest": "Тест",
            "easier_than_expected": "Тест"
        }
        client.post("/tracking/diary", json=entry_data, headers=auth_headers)
        
        # Получаем записи
        response = client.get(
            "/tracking/diary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


class TestDayRitual:
    """Тесты для ритуала закрытия дня."""
    
    def test_create_day_ritual(self, client, test_tracking_user, auth_headers, db_session):
        """Тест создания ритуала закрытия дня."""
        ritual_data = {
            "date": "2026-01-25",
            "completed": True,
            "closing_phrase_id": "lex.001",
            "sufficiency_confirmed": True
        }
        
        response = client.post(
            "/tracking/ritual",
            json=ritual_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["date"] == ritual_data["date"]
        assert data["completed"] == ritual_data["completed"]
        assert data["sufficiency_confirmed"] == ritual_data["sufficiency_confirmed"]
        # Проверяем, что текст фразы загружен из Lexicon
        if ritual_data["closing_phrase_id"]:
            assert data["closing_phrase_text"] is not None
    
    def test_get_day_ritual(self, client, test_tracking_user, auth_headers, db_session):
        """Тест получения ритуала по дате."""
        # Создаём ритуал
        ritual_data = {
            "date": "2026-01-25",
            "completed": True,
            "sufficiency_confirmed": True
        }
        client.post("/tracking/ritual", json=ritual_data, headers=auth_headers)
        
        # Получаем ритуал
        response = client.get(
            "/tracking/ritual/2026-01-25",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == ritual_data["date"]


class TestAutoInsights:
    """Тесты для автоматических инсайтов."""
    
    def test_generate_insight(self, client, test_tracking_user, auth_headers, db_session):
        """Тест генерации инсайта."""
        # Создаём несколько записей трекера для генерации инсайта
        for i in range(3):
            entry_data = {
                "date": (date.today() - timedelta(days=i)).isoformat(),
                "affirmation_id": "practice.001",
                "completed": True,
                "state_scale": 4
            }
            client.post("/tracking/progress", json=entry_data, headers=auth_headers)
        
        # Генерируем инсайт
        response = client.post(
            "/tracking/insights/generate",
            params={"target_date": date.today().isoformat()},
            headers=auth_headers
        )
        
        # Может вернуть 404, если недостаточно данных, или 200 с инсайтом
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "insight_text" in data
            assert "type" in data
    
    def test_get_insights(self, client, test_tracking_user, auth_headers, db_session):
        """Тест получения инсайтов."""
        response = client.get(
            "/tracking/insights",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestWeeklyIntegration:
    """Тесты для недельной интеграции."""
    
    def test_generate_weekly_integration(self, client, test_tracking_user, auth_headers, db_session):
        """Тест генерации недельной интеграции."""
        # Создаём записи трекера за неделю
        week_start = date.today() - timedelta(days=7)
        for i in range(5):
            entry_data = {
                "date": (week_start + timedelta(days=i)).isoformat(),
                "affirmation_id": "practice.001",
                "completed": True,
                "state": "calm"
            }
            client.post("/tracking/progress", json=entry_data, headers=auth_headers)
        
        # Генерируем недельную интеграцию
        response = client.post(
            "/tracking/weekly/generate",
            params={
                "week_start": week_start.isoformat(),
                "week_end": (week_start + timedelta(days=6)).isoformat()
            },
            headers=auth_headers
        )
        
        # Может вернуть 404, если недостаточно данных, или 200 с интеграцией
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "integration_text" in data

    def test_get_weekly_integration(self, client, test_tracking_user, auth_headers, db_session):
        """Тест получения недельной интеграции."""
        week_start = date.today() - timedelta(days=7)
        week_end = week_start + timedelta(days=6)
        
        response = client.get(
            f"/tracking/weekly/{week_start.isoformat()}",
            params={"week_end": week_end.isoformat()},
            headers=auth_headers
        )
        
        # Может вернуть 200 с данными или 404, если нет интеграции
        assert response.status_code in [200, 404]


class TestAsceticContractsAndFusion:
    """Тесты для контрактов аскез и fusion-индекса."""

    def test_create_contract_and_checkin(self, client, test_tracking_user, auth_headers):
        create_resp = client.post(
            "/tracking/ascetic-contracts",
            json={
                "title": "Сахарный детокс",
                "asceticism_id": "asceticism.sugar_free",
                "intention": "Стабилизировать энергию",
                "start_date": "2026-02-10",
                "end_date": "2026-03-02",
            },
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        contract_id = create_resp.json()["id"]

        checkin_resp = client.post(
            f"/tracking/ascetic-contracts/{contract_id}/checkin",
            json={
                "date": "2026-02-10",
                "completed": True,
                "state_scale": 4,
                "note": "День 1 пройден",
            },
            headers=auth_headers,
        )
        assert checkin_resp.status_code == 200
        payload = checkin_resp.json()
        assert payload["streak_days"] >= 1
        assert payload["status"] in ["active", "completed"]

    def test_daily_fusion_index(self, client, test_tracking_user, auth_headers):
        target_date = "2026-02-10"
        client.post(
            "/tracking/progress",
            json={
                "date": target_date,
                "affirmation_id": "practice.001",
                "completed": True,
                "state_scale": 4,
            },
            headers=auth_headers,
        )
        client.post(
            "/tracking/ritual",
            json={
                "date": target_date,
                "completed": True,
                "sufficiency_confirmed": True,
            },
            headers=auth_headers,
        )

        fusion_resp = client.get(f"/tracking/fusion/{target_date}", headers=auth_headers)
        assert fusion_resp.status_code == 200
        fusion = fusion_resp.json()
        assert fusion["date"] == target_date
        assert "scores" in fusion
        assert "energy" in fusion["scores"]
        assert "emotional_balance" in fusion["scores"]
        assert "focus" in fusion["scores"]
        assert "rhythm_context" in fusion
        rc = fusion["rhythm_context"]
        assert isinstance(rc.get("goals"), list)
        assert isinstance(rc.get("habits"), list)
        assert isinstance(rc.get("ascetics"), list)
        assert isinstance(rc.get("diary"), dict)
        assert "has_entry_today" in rc["diary"]
        assert "entries_last_7_days" in rc["diary"]
        assert fusion["activity_context"].get("guide_action_options_selected_today", -1) == 0
        dh = fusion.get("day_history")
        assert dh is not None
        assert dh.get("contract_version") == "day_history_v0"
        assert "yesterday" in dh
        assert "fusion_score_delta_vs_yesterday" in dh
        assert "fusion_score_delta_trustworthy" in dh
        assert "yesterday_fusion_has_flow_markers" in dh
        assert "trailing_7d_summary_trustworthy" in dh
        assert "trailing_7d_flow_days" in dh

    def test_fusion_activity_context_includes_day_flow_closure_flags(self, client, test_tracking_user, auth_headers):
        """DE-7: флаги DayConnection в fusion для narrative / DayContext."""
        target_date = "2026-02-16"
        dc = client.post(
            f"/day-connection/{target_date}",
            json={
                "morning_completed": True,
                "day_completed": True,
                "evening_completed": False,
            },
            headers=auth_headers,
        )
        assert dc.status_code == 200
        fusion_resp = client.get(f"/tracking/fusion/{target_date}", headers=auth_headers)
        assert fusion_resp.status_code == 200
        ac = fusion_resp.json()["activity_context"]
        assert ac["morning_completed"] is True
        assert ac["day_completed"] is True
        assert ac["evening_completed"] is False
        assert ac.get("guide_action_options_selected_today", 0) == 0
        gmc = ac["guide_meaning_completions_today"]
        assert gmc == {
            "habit_completed": 0,
            "practice_completed": 0,
            "focus_completed": 0,
            "affirmation_done": 0,
            "ascetic_step_done": 0,
        }

    def test_fusion_counts_action_option_selected_meaning_events(self, client, test_tracking_user, auth_headers):
        target_date = "2026-02-18"
        ev = client.post(
            "/meaning/events",
            json={
                "events": [
                    {
                        "event_type": "action_option_selected",
                        "event_source": "today",
                        "local_date": target_date,
                        "payload": {"action_option_index": 0, "action_option_title": "Шаг один"},
                        "idempotency_key": "pytest-fusion-ao-0",
                    },
                    {
                        "event_type": "action_option_selected",
                        "event_source": "today",
                        "local_date": target_date,
                        "payload": {"action_option_index": 2, "action_option_title": "Шаг три"},
                        "idempotency_key": "pytest-fusion-ao-2",
                    },
                ]
            },
            headers=auth_headers,
        )
        assert ev.status_code == 200
        fusion_resp = client.get(f"/tracking/fusion/{target_date}", headers=auth_headers)
        assert fusion_resp.status_code == 200
        assert fusion_resp.json()["activity_context"]["guide_action_options_selected_today"] == 2

    def test_fusion_guide_meaning_completions_today_from_meaning_events(
        self, client, test_tracking_user, auth_headers
    ):
        """DE-7 v2: счётчики «сделано» из meaning_events в fusion (не доверяем клиенту)."""
        target_date = "2026-02-19"
        ev = client.post(
            "/meaning/events",
            json={
                "events": [
                    {
                        "event_type": "habit_completed",
                        "event_source": "today",
                        "local_date": target_date,
                        "payload": {"habit_id": 1},
                        "idempotency_key": "pytest-fusion-gmc-h1",
                    },
                    {
                        "event_type": "habit_completed",
                        "event_source": "today",
                        "local_date": target_date,
                        "payload": {"habit_id": 2},
                        "idempotency_key": "pytest-fusion-gmc-h2",
                    },
                    {
                        "event_type": "practice_completed",
                        "event_source": "today",
                        "local_date": target_date,
                        "payload": {},
                        "idempotency_key": "pytest-fusion-gmc-p1",
                    },
                    {
                        "event_type": "focus_completed",
                        "event_source": "today",
                        "local_date": target_date,
                        "payload": {},
                        "idempotency_key": "pytest-fusion-gmc-f1",
                    },
                ]
            },
            headers=auth_headers,
        )
        assert ev.status_code == 200
        fusion_resp = client.get(f"/tracking/fusion/{target_date}", headers=auth_headers)
        assert fusion_resp.status_code == 200
        gmc = fusion_resp.json()["activity_context"]["guide_meaning_completions_today"]
        assert gmc["habit_completed"] == 2
        assert gmc["practice_completed"] == 1
        assert gmc["focus_completed"] == 1
        assert gmc["affirmation_done"] == 0
        assert gmc["ascetic_step_done"] == 0


class TestReflections:
    """Тесты для отражений."""
    
    def test_get_daily_reflection(self, client, test_tracking_user, auth_headers, db_session):
        """Тест получения дневного отражения."""
        response = client.get(
            "/tracking/reflection/daily/2026-01-25",
            params={
                "forecast_type": "workday_focus",
                "layers": ["L1", "L2"]
            },
            headers=auth_headers
        )
        
        # Может вернуть 200 с отражением или 404
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "theme" in data
            assert "recommended_practice" in data
    
    def test_get_weekly_reflection(self, client, test_tracking_user, auth_headers, db_session):
        """Тест получения недельного отражения."""
        week_start = date.today() - timedelta(days=7)
        week_end = week_start + timedelta(days=6)
        
        response = client.get(
            f"/tracking/reflection/weekly/{week_start.isoformat()}",
            params={"week_end": week_end.isoformat()},
            headers=auth_headers
        )
        
        # Может вернуть 200 с отражением или 404
        assert response.status_code in [200, 404]
