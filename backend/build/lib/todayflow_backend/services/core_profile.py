"""Core profile assembler for unified personalization context."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from hashlib import sha1
import time as time_module
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core.profile_interpreter import generate_profile_interpretation
from todayflow_backend.data.astrology import sign_for_date
from todayflow_backend.db import models as db_models


@dataclass
class CoreProfileService:
    """Builds stable profile context from natal + numerology data."""

    profile_version: str = "core-v2"
    cache_ttl_seconds: int = 900

    def __post_init__(self) -> None:
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def _attach_natal_summary(
        self,
        db: Session,
        payload: dict[str, Any],
        astro_profile: db_models.AstroProfile | None,
        settings: db_models.UserSettings | None,
    ) -> dict[str, Any]:
        """Подмешивает сжатое астро-резюме при отдаче (не кладём в снапшот — карта может появиться позже)."""
        from todayflow_backend.services.natal_chart_summary import build_natal_chart_summary_for_core

        locale = (settings.locale if settings else None) or "ru"
        aid = astro_profile.id if astro_profile else None
        payload["natal_summary"] = build_natal_chart_summary_for_core(
            db, astro_profile_id=aid, locale=locale
        )
        return payload

    def build(self, db: Session, user: db_models.User, astro_profile_id: int | None = None) -> dict[str, Any]:
        # Явная загрузка настроек: при переиспользовании одной DB-сессии (pytest / TestClient)
        # связь user.settings может не отражать только что закоммиченный PUT /account/profile.
        settings = (
            db.query(db_models.UserSettings).filter(db_models.UserSettings.user_id == user.id).first()
        )
        astro_profile = self._resolve_astro_profile(db, user.id, astro_profile_id)
        numerology_profile = self._resolve_numerology_profile(db, user.id, settings, astro_profile)
        profiles_context = self._build_profiles_context(db, user.id, astro_profile.id if astro_profile else None)
        living_context, living_cache_marker = self._build_living_context(db, user.id)
        cache_key = self._cache_key(user.id, settings, astro_profile, numerology_profile, profiles_context, living_cache_marker)
        now = time_module.time()
        cached = self._cache.get(cache_key)
        if cached and cached[0] > now:
            return self._attach_natal_summary(db, deepcopy(cached[1]), astro_profile, settings)

        astro_context = self._build_astro_context(astro_profile)
        numerology_context = self._build_numerology_context(numerology_profile)
        profile_hash = self._build_profile_hash(settings, astro_context, numerology_context)
        snapshot = self._load_snapshot(db, user.id, profile_hash)
        if snapshot is not None:
            cached_payload = self._normalize_payload_contract(deepcopy(snapshot))
            cached_payload["astro"]["relation"] = astro_context.get("relation")
            cached_payload["profiles"] = profiles_context
            cached_payload["living"] = living_context
            self._cache[cache_key] = (now + self.cache_ttl_seconds, deepcopy(cached_payload))
            self._prune_cache(now)
            return self._attach_natal_summary(db, cached_payload, astro_profile, settings)

        baseline = self._build_baseline(astro_context, numerology_context)
        missing_fields = self._build_missing_fields(settings, astro_context, numerology_context)
        is_ready = len(missing_fields) == 0

        first_name = settings.first_name if settings else None
        display_name = first_name or (settings.greeting if settings else None) or user.email.split("@")[0]

        interpretation_payload = generate_profile_interpretation(db, user, {
            "profile_version": self.profile_version,
            "generated_at": datetime.utcnow().isoformat(),
            "is_ready": is_ready,
            "missing_fields": missing_fields,
            "profile_hash": profile_hash,
            "person": {
                "first_name": first_name,
                "display_name": display_name,
                "locale": settings.locale if settings else None,
            },
            "astro": astro_context,
            "numerology": numerology_context,
            "baseline": baseline,
            "profiles": profiles_context,
        })
        profile_payload = {
            "profile_version": self.profile_version,
            "generated_at": datetime.utcnow().isoformat(),
            "is_ready": is_ready,
            "missing_fields": missing_fields,
            "profile_hash": profile_hash,
            "person": {
                "first_name": first_name,
                "display_name": display_name,
                "locale": settings.locale if settings else None,
            },
            "astro": astro_context,
            "numerology": numerology_context,
            "baseline": baseline,
            "profiles": profiles_context,
            "interpretation": interpretation_payload.get("interpretation"),
            "daily_interpretation": interpretation_payload.get("daily_interpretation"),
            "living": living_context,
        }
        self._save_snapshot(
            db=db,
            user_id=user.id,
            profile_hash=profile_hash,
            payload=profile_payload,
        )
        self._cache[cache_key] = (now + self.cache_ttl_seconds, deepcopy(profile_payload))
        self._prune_cache(now)
        return self._attach_natal_summary(db, deepcopy(profile_payload), astro_profile, settings)

    def _cache_key(
        self,
        user_id: int,
        settings: db_models.UserSettings | None,
        astro_profile: db_models.AstroProfile | None,
        numerology_profile: db_models.NumerologyProfileRecord | None,
        profiles_context: dict[str, Any],
        living_cache_marker: str,
    ) -> str:
        return "|".join(
            [
                str(user_id),
                str(settings.updated_at.isoformat() if settings and settings.updated_at else ""),
                str(settings.first_name if settings else ""),
                str(settings.last_name if settings else ""),
                str(astro_profile.id if astro_profile else ""),
                str(astro_profile.updated_at.isoformat() if astro_profile and astro_profile.updated_at else ""),
                str(astro_profile.birth_date.isoformat() if astro_profile and astro_profile.birth_date else ""),
                str(profiles_context.get("profiles_hash") or ""),
                str(numerology_profile.id if numerology_profile else ""),
                str(numerology_profile.created_at.isoformat() if numerology_profile and numerology_profile.created_at else ""),
                living_cache_marker,
            ]
        )

    def _prune_cache(self, now: float) -> None:
        if len(self._cache) <= 256:
            return
        expired_keys = [key for key, (expires_at, _) in self._cache.items() if expires_at <= now]
        for key in expired_keys:
            self._cache.pop(key, None)
        if len(self._cache) > 256:
            # Fallback trim by arbitrary oldest insertion order.
            for key in list(self._cache.keys())[: len(self._cache) - 256]:
                self._cache.pop(key, None)

    def _resolve_astro_profile(
        self,
        db: Session,
        user_id: int,
        astro_profile_id: int | None,
    ) -> db_models.AstroProfile | None:
        query = db.query(db_models.AstroProfile).filter(db_models.AstroProfile.user_id == user_id)
        if astro_profile_id is not None:
            return query.filter(db_models.AstroProfile.id == astro_profile_id).first()

        primary = query.filter(db_models.AstroProfile.is_primary.is_(True)).first()
        if primary:
            return primary

        return query.order_by(db_models.AstroProfile.created_at.desc()).first()

    def _resolve_numerology_profile(
        self,
        db: Session,
        user_id: int,
        settings: db_models.UserSettings | None,
        astro_profile: db_models.AstroProfile | None,
    ) -> db_models.NumerologyProfileRecord | None:
        query = db.query(db_models.NumerologyProfileRecord).filter(
            db_models.NumerologyProfileRecord.user_id == user_id
        )
        if astro_profile:
            by_birth_date = query.filter(
                db_models.NumerologyProfileRecord.birth_date == astro_profile.birth_date
            ).order_by(db_models.NumerologyProfileRecord.created_at.desc()).first()
            if by_birth_date:
                return by_birth_date

        if settings and settings.first_name and settings.last_name:
            full_name = f"{settings.first_name} {settings.last_name}".strip()
            by_name = query.filter(
                db_models.NumerologyProfileRecord.full_name == full_name
            ).order_by(db_models.NumerologyProfileRecord.created_at.desc()).first()
            if by_name:
                return by_name

        return query.order_by(db_models.NumerologyProfileRecord.created_at.desc()).first()

    def _build_astro_context(self, astro_profile: db_models.AstroProfile | None) -> dict[str, Any]:
        if astro_profile is None:
            return {
                "profile_id": None,
                "label": None,
                "relation": None,
                "birth_date": None,
                "birth_time": None,
                "time_unknown": None,
                "location_name": None,
                "sun_sign": None,
                "sun_element": None,
                "sun_modality": None,
            }

        sign = sign_for_date(astro_profile.birth_date)
        return {
            "profile_id": astro_profile.id,
            "label": astro_profile.label,
            "relation": self._relation_for_profile(astro_profile),
            "birth_date": astro_profile.birth_date.isoformat(),
            "birth_time": astro_profile.birth_time.isoformat() if astro_profile.birth_time else None,
            "time_unknown": astro_profile.time_unknown,
            "location_name": astro_profile.location_name,
            "sun_sign": sign.get("name") if sign else None,
            "sun_element": sign.get("element") if sign else None,
            "sun_modality": sign.get("modality") if sign else None,
        }

    def _build_numerology_context(
        self,
        numerology_profile: db_models.NumerologyProfileRecord | None,
    ) -> dict[str, Any]:
        if numerology_profile is None:
            return {
                "full_name": None,
                "birth_date": None,
                "life_path": None,
                "expression": None,
                "soul_urge": None,
                "personality": None,
                "is_master_life_path": False,
            }

        payload = numerology_profile.data or {}
        life_path = self._extract_reduced_value(payload.get("life_path"))
        expression = self._extract_reduced_value(payload.get("expression"))
        soul_urge = self._extract_reduced_value(payload.get("soul_urge"))
        personality = self._extract_reduced_value(payload.get("personality"))

        return {
            "full_name": numerology_profile.full_name,
            "birth_date": numerology_profile.birth_date.isoformat(),
            "life_path": life_path,
            "expression": expression,
            "soul_urge": soul_urge,
            "personality": personality,
            "is_master_life_path": life_path in {11, 22, 33},
        }

    def _build_baseline(self, astro_context: dict[str, Any], numerology_context: dict[str, Any]) -> dict[str, Any]:
        element = astro_context.get("sun_element")
        modality = astro_context.get("sun_modality")
        life_path = numerology_context.get("life_path")

        element_focus = {
            "fire": "Инициатива и действие",
            "earth": "Структура и устойчивость",
            "air": "Смысл и коммуникация",
            "water": "Эмпатия и внутренняя глубина",
        }.get((element or "").lower(), "Баланс и адаптация")

        rhythm_style = {
            "cardinal": "Ясный старт и первый шаг",
            "fixed": "Устойчивость через понятный ритм",
            "mutable": "Гибкость и мягкая перенастройка",
        }.get((modality or "").lower(), "Ритм через базовые микро-шаги")

        archetype = "Observer"
        if life_path in {1, 8, 22}:
            archetype = "Architect"
        elif life_path in {2, 6, 11}:
            archetype = "Harmonizer"
        elif life_path in {3, 5, 21}:
            archetype = "Explorer"
        elif life_path in {4, 7, 9, 33}:
            archetype = "Sage"

        return {
            "archetype_seed": archetype,
            "element_focus": element_focus,
            "rhythm_style": rhythm_style,
        }

    def _build_profiles_context(
        self,
        db: Session,
        user_id: int,
        selected_profile_id: int | None,
    ) -> dict[str, Any]:
        profiles = (
            db.query(db_models.AstroProfile)
            .filter(db_models.AstroProfile.user_id == user_id)
            .order_by(db_models.AstroProfile.is_primary.desc(), db_models.AstroProfile.created_at.asc())
            .all()
        )
        items: list[dict[str, Any]] = []
        hash_parts: list[str] = []
        primary_profile_id: int | None = None
        for profile in profiles:
            relation = self._relation_for_profile(profile)
            if profile.is_primary and primary_profile_id is None:
                primary_profile_id = profile.id
            sign = sign_for_date(profile.birth_date)
            item = {
                "id": profile.id,
                "label": profile.label,
                "relation": relation,
                "is_primary": profile.is_primary,
                "is_selected": profile.id == selected_profile_id,
                "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
                "birth_time": profile.birth_time.isoformat() if profile.birth_time else None,
                "time_unknown": profile.time_unknown,
                "location_name": profile.location_name,
                "sun_sign": sign.get("name") if sign else None,
            }
            items.append(item)
            hash_parts.append(
                "|".join(
                    [
                        str(profile.id),
                        relation,
                        str(profile.label or ""),
                        str(profile.is_primary),
                        str(profile.updated_at.isoformat() if profile.updated_at else ""),
                    ]
                )
            )
        return {
            "selected_profile_id": selected_profile_id,
            "primary_profile_id": primary_profile_id,
            "has_multiple_profiles": len(items) > 1,
            "items": items,
            "profiles_hash": sha1("||".join(hash_parts).encode("utf-8")).hexdigest() if hash_parts else None,
        }

    def _build_living_context(self, db: Session, user_id: int) -> tuple[dict[str, Any], str]:
        from todayflow_backend.services.learning import get_learning_service

        today = date.today()
        recent_signals = (
            db.query(db_models.DayConnection)
            .filter(
                db_models.DayConnection.user_id == user_id,
                db_models.DayConnection.date >= today - timedelta(days=13),
                db_models.DayConnection.date <= today,
            )
            .order_by(db_models.DayConnection.date.desc(), db_models.DayConnection.updated_at.desc())
            .all()
        )
        recent_insights = (
            db.query(db_models.AutoInsight)
            .filter(db_models.AutoInsight.user_id == user_id)
            .order_by(db_models.AutoInsight.date.desc(), db_models.AutoInsight.created_at.desc())
            .limit(3)
            .all()
        )
        latest_weekly = (
            db.query(db_models.WeeklyIntegration)
            .filter(
                db_models.WeeklyIntegration.user_id == user_id,
                db_models.WeeklyIntegration.week_end >= today - timedelta(days=14),
            )
            .order_by(db_models.WeeklyIntegration.week_start.desc(), db_models.WeeklyIntegration.created_at.desc())
            .first()
        )

        signal_summary = self._summarize_recent_signals(recent_signals)
        weekly_state = None
        if latest_weekly:
            weekly_state = {
                "week_start": latest_weekly.week_start.isoformat(),
                "week_end": latest_weekly.week_end.isoformat(),
                "integration_text": latest_weekly.integration_text,
                "signals_days": int((latest_weekly.data_points or {}).get("signals_days") or 0),
                "ritual_feedback_yes_days": int((latest_weekly.data_points or {}).get("ritual_feedback_yes_days") or 0),
                "ritual_feedback_no_days": int((latest_weekly.data_points or {}).get("ritual_feedback_no_days") or 0),
                "unclear_decision_days": int((latest_weekly.data_points or {}).get("unclear_decision_days") or 0),
                "dominant_question_focus": (latest_weekly.data_points or {}).get("dominant_question_focus"),
            }

        insights_payload = [
            {
                "id": insight.id,
                "date": insight.date.isoformat(),
                "type": insight.type,
                "text": insight.insight_text,
                "confidence": (insight.data_points or {}).get("confidence", "medium") if isinstance(insight.data_points, dict) else "medium",
            }
            for insight in recent_insights
        ]
        learning_context = get_learning_service().build_user_learning_context(
            db,
            user_id=user_id,
            target_date=today,
        )
        living = {
            "summary": self._compose_living_summary(signal_summary, weekly_state, insights_payload),
            "signal_profile": signal_summary,
            "weekly_state": weekly_state,
            "recent_insights": insights_payload,
            "learning_context": learning_context,
        }
        marker_parts = [
            recent_signals[0].updated_at.isoformat() if recent_signals and recent_signals[0].updated_at else "",
            recent_insights[0].created_at.isoformat() if recent_insights and recent_insights[0].created_at else "",
            latest_weekly.created_at.isoformat() if latest_weekly and latest_weekly.created_at else "",
            str(signal_summary.get("signals_days") or 0),
            str((learning_context.get("summary") or "")),
        ]
        return living, "|".join(marker_parts)

    def _summarize_recent_signals(self, signals: list[db_models.DayConnection]) -> dict[str, Any]:
        relevant = [
            item for item in signals
            if item.ritual_feedback or item.quick_decision_answer or item.question_of_day_answer
        ]
        if not relevant:
            return {
                "signals_days": 0,
                "closure_state": "unknown",
                "clarity_state": "unknown",
                "dominant_focus": None,
                "ritual_feedback_yes_days": 0,
                "ritual_feedback_no_days": 0,
                "unclear_decision_days": 0,
            }

        yes_days = sum(1 for item in relevant if item.ritual_feedback == "yes")
        no_days = sum(1 for item in relevant if item.ritual_feedback == "no")
        unclear_days = sum(1 for item in relevant if item.quick_decision_answer == "unclear")
        answer_counts: dict[str, int] = {}
        for item in relevant:
            answer = (item.question_of_day_answer or "").strip()
            if not answer:
                continue
            answer_counts[answer] = answer_counts.get(answer, 0) + 1
        dominant_focus = max(answer_counts.items(), key=lambda item: item[1])[0] if answer_counts else None

        closure_state = "mixed"
        if yes_days >= 4 and yes_days > no_days:
            closure_state = "stable"
        elif no_days >= 3 and no_days >= yes_days:
            closure_state = "fragile"
        elif yes_days > 0 or no_days > 0:
            closure_state = "building"

        clarity_state = "mixed"
        clear_days = sum(1 for item in relevant if item.quick_decision_answer == "yes")
        if unclear_days >= 3:
            clarity_state = "unclear"
        elif clear_days >= 3 and clear_days > unclear_days:
            clarity_state = "growing"
        elif clear_days == 0 and unclear_days == 0:
            clarity_state = "unknown"

        return {
            "signals_days": len(relevant),
            "closure_state": closure_state,
            "clarity_state": clarity_state,
            "dominant_focus": dominant_focus,
            "ritual_feedback_yes_days": yes_days,
            "ritual_feedback_no_days": no_days,
            "unclear_decision_days": unclear_days,
        }

    def _compose_living_summary(
        self,
        signal_summary: dict[str, Any],
        weekly_state: dict[str, Any] | None,
        recent_insights: list[dict[str, Any]],
    ) -> str:
        if signal_summary.get("signals_days", 0) == 0:
            return "Пока профиль в основном опирается на базовые данные. Когда ты чаще отвечаешь дню, карта начнет показывать и живой паттерн проживания."

        closure_map = {
            "stable": "Ты всё чаще собираешь день до ощущения завершенности.",
            "fragile": "Сейчас профиль видит, что дню часто не хватает спокойного закрытия.",
            "building": "Собранность уже появляется, но пока держится не каждый день.",
            "mixed": "Ритм дня пока живет неровно: часть дней собирается, часть распадается.",
            "unknown": "Собранность дня пока ещё не читается устойчиво.",
        }
        clarity_map = {
            "growing": "Ясность решений растет.",
            "unclear": "Неясность решений повторяется чаще, чем хотелось бы.",
            "mixed": "С решениями есть и ясные, и зависающие дни.",
            "unknown": "Слой быстрых решений пока собран слабо.",
        }
        focus = signal_summary.get("dominant_focus")
        focus_line = f" Чаще всего сейчас всплывает тема `{focus}`." if focus else ""
        weekly_line = f" Недельный слой тоже это подтверждает: {weekly_state.get('integration_text')}" if weekly_state and weekly_state.get("integration_text") else ""
        insight_line = f" Последний инсайт: {recent_insights[0]['text']}" if recent_insights else ""
        return f"{closure_map.get(signal_summary.get('closure_state'), '')} {clarity_map.get(signal_summary.get('clarity_state'), '')}{focus_line}{weekly_line}{insight_line}".strip()

    def _relation_for_profile(self, astro_profile: db_models.AstroProfile) -> str:
        relation = (astro_profile.relation or "").strip().lower()
        if astro_profile.is_primary:
            return "self"
        if relation in {"partner", "child", "close_person"}:
            return relation
        return "close_person"

    def _build_missing_fields(
        self,
        settings: db_models.UserSettings | None,
        astro_context: dict[str, Any],
        numerology_context: dict[str, Any],
    ) -> list[str]:
        missing: list[str] = []
        if not settings or not settings.first_name:
            missing.append("first_name")
        if not astro_context.get("birth_date"):
            missing.append("astro_birth_date")
        if not astro_context.get("location_name"):
            missing.append("astro_location_name")
        if numerology_context.get("life_path") is None:
            missing.append("numerology_life_path")
        return missing

    def _build_profile_hash(
        self,
        settings: db_models.UserSettings | None,
        astro_context: dict[str, Any],
        numerology_context: dict[str, Any],
    ) -> str:
        raw = "|".join(
            [
                str(settings.first_name if settings else ""),
                str(settings.last_name if settings else ""),
                str(astro_context.get("birth_date") or ""),
                str(astro_context.get("birth_time") or ""),
                str(astro_context.get("location_name") or ""),
                str(astro_context.get("sun_sign") or ""),
                str(numerology_context.get("life_path") or ""),
                str(numerology_context.get("expression") or ""),
            ]
        )
        return sha1(raw.encode("utf-8")).hexdigest()

    def _load_snapshot(self, db: Session, user_id: int, profile_hash: str) -> dict[str, Any] | None:
        record = (
            db.query(db_models.CoreProfileSnapshot)
            .filter(
                db_models.CoreProfileSnapshot.user_id == user_id,
                db_models.CoreProfileSnapshot.profile_hash == profile_hash,
            )
            .first()
        )
        if record is None or not isinstance(record.payload, dict):
            return None
        payload = deepcopy(record.payload)
        # Keep generated_at stable from persisted record.
        if record.updated_at:
            payload["generated_at"] = record.updated_at.isoformat()
        if "profile_version" not in payload:
            payload["profile_version"] = record.profile_version or self.profile_version
        return self._normalize_payload_contract(payload)

    def _save_snapshot(
        self,
        *,
        db: Session,
        user_id: int,
        profile_hash: str,
        payload: dict[str, Any],
    ) -> None:
        existing = (
            db.query(db_models.CoreProfileSnapshot)
            .filter(
                db_models.CoreProfileSnapshot.user_id == user_id,
                db_models.CoreProfileSnapshot.profile_hash == profile_hash,
            )
            .first()
        )
        if existing is not None:
            existing.profile_version = self.profile_version
            existing.payload = deepcopy(payload)
            db.add(existing)
            db.commit()
            return

        snapshot = db_models.CoreProfileSnapshot(
            user_id=user_id,
            profile_hash=profile_hash,
            profile_version=self.profile_version,
            payload=deepcopy(payload),
        )
        db.add(snapshot)
        db.commit()

    @staticmethod
    def _extract_reduced_value(item: Any) -> int | None:
        if not isinstance(item, dict):
            return None
        if isinstance(item.get("reduced_value"), int):
            return int(item["reduced_value"])
        if isinstance(item.get("value"), int):
            return int(item["value"])
        return None

    def _normalize_payload_contract(self, payload: dict[str, Any]) -> dict[str, Any]:
        interpretation = payload.get("interpretation")
        daily_interpretation = payload.get("daily_interpretation")
        if isinstance(interpretation, dict):
            legacy_daily_lenses = interpretation.pop("daily_lenses", None)
            if not isinstance(daily_interpretation, dict):
                daily_interpretation = {}
            if isinstance(legacy_daily_lenses, dict) and "daily_lenses" not in daily_interpretation:
                daily_interpretation["daily_lenses"] = legacy_daily_lenses
        else:
            payload["interpretation"] = None

        if not isinstance(daily_interpretation, dict):
            daily_interpretation = {}
        payload["daily_interpretation"] = daily_interpretation
        if not isinstance(payload.get("living"), dict):
            payload["living"] = None
        return payload


_CORE_PROFILE_SERVICE = CoreProfileService()


def get_core_profile_service() -> CoreProfileService:
    return _CORE_PROFILE_SERVICE
