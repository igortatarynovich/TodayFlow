"""Tarot Flow service: deterministic daily draws + ritual/mantra recommendations."""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta, timezone
from random import Random
from typing import Any, Dict, List
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError

from todayflow_backend.core import models as api_models
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.data import content_system
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import utc_naive_now
from todayflow_backend.db.session import SessionLocal
from todayflow_backend.i18n import localize_mantra, localize_ritual, localize_spread_meta, translate

DEFAULT_REMINDER_TZ = "UTC"
DEFAULT_REMINDER_HOUR = 9
DEFAULT_REMINDER_MINUTE = 0


class TarotService:
    def __init__(self) -> None:
        self.cards = astrology_ref.tarot_major_arcana()
        self.card_map = {str(card["id"]): card for card in self.cards}
        spreads = astrology_ref.tarot_spreads()
        self.spreads = {spread["id"]: spread for spread in spreads}
        self.default_spread_id = spreads[0]["id"] if spreads else None
        self.mantras = astrology_ref.mantras()
        self.rituals = astrology_ref.rituals()

    def not_selected_daily_draw(self, *, draw_date: date | None = None) -> api_models.TarotDailyDraw:
        """Gate payload: no card name/id/image-identifying fields before user action."""
        target = draw_date or date.today()
        return api_models.TarotDailyDraw(
            date=target.isoformat(),
            selection_status="not_selected",
            card=None,
            orientation=None,
            mantra=None,
            ritual=None,
        )

    def get_daily_draw(
        self,
        user: db_models.User,
        *,
        locale: str | None = None,
        assign_if_missing: bool = True,
    ) -> api_models.TarotDailyDraw:
        """Internal / Today morning path may assign.

        Tarot module public GET must use ``assign_if_missing=False`` so identity
        is not created or returned before an explicit reveal/select.
        """
        # Public guest: never return identity from module endpoints.
        if user.id == 0:
            if assign_if_missing:
                # Legacy callers that still want a deterministic public draw
                # (e.g. morning-adjacent tooling). Prefer not_selected for modules.
                return self._generate_public_daily_draw(date.today(), locale=locale)
            return self.not_selected_daily_draw()
        if assign_if_missing:
            draw = self._ensure_draw_for_date(user, date.today())
            return self._to_model(draw, locale=locale)
        session = SessionLocal()
        try:
            draw = (
                session.query(db_models.TarotDraw)
                .filter_by(user_id=user.id, draw_date=date.today())
                .order_by(db_models.TarotDraw.created_at.desc())
                .first()
            )
        finally:
            session.close()
        if not draw:
            return self.not_selected_daily_draw()
        return self._to_model(draw, locale=locale)

    def reveal_daily_draw(self, user: db_models.User, *, locale: str | None = None) -> api_models.TarotDailyDraw:
        """Explicit user action: assign (if needed) and return selected card identity."""
        if user.id == 0:
            # Guests cannot persist; still do not expose via public GET — use Today ritual.
            return self.not_selected_daily_draw()
        draw = self._ensure_draw_for_date(user, date.today())
        model = self._to_model(draw, locale=locale)
        model.selection_status = "selected"
        return model

    def get_card_by_id(self, card_id: int, *, locale: str | None = None) -> api_models.TarotCard | None:
        """Return a single major arcana card from reference data (for library / SEO pages)."""
        _ = locale  # reserved for future localized decks
        card_data = self.card_map.get(str(card_id))
        if not card_data:
            return None
        return api_models.TarotCard(
            id=card_data["id"],
            name=card_data["name"],
            keywords=list(card_data.get("keywords") or []),
            upright=str(card_data.get("upright") or ""),
            reversed=str(card_data.get("reversed") or ""),
            correspondences=dict(card_data.get("correspondences") or {}),
        )

    def get_history(
        self, user: db_models.User, limit: int = 30, *, locale: str | None = None
    ) -> api_models.TarotHistoryResponse:
        # Do not auto-create today's draw — that would spoil card-of-day before select.
        today = self.get_daily_draw(user, locale=locale, assign_if_missing=False)
        session = SessionLocal()
        try:
            draws = (
                session.query(db_models.TarotDraw)
                .filter_by(user_id=user.id)
                .order_by(db_models.TarotDraw.draw_date.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()

        streak = self._calculate_streak(draws, date.today())
        history_models = [self._to_model(draw, locale=locale) for draw in draws]
        return api_models.TarotHistoryResponse(
            today=today, history=history_models, streak_days=streak
        )

    def generate_spread(
        self,
        spread_id: str | None,
        user: db_models.User,
        *,
        locale: str | None = None,
        selected_cards: List[api_models.TarotSelectedCard] | None = None,
    ) -> api_models.TarotSpreadResult:
        draw_date = date.today()
        result = self._build_spread_result(spread_id, user, draw_date, locale=locale, selected_cards=selected_cards)
        self._record_spread_draw(user.id, result.spread_id, draw_date)
        return result

    def get_spread_history(
        self, user: db_models.User, limit: int = 5, *, locale: str | None = None
    ) -> api_models.TarotSpreadHistoryResponse:
        session = SessionLocal()
        try:
            rows = (
                session.query(db_models.TarotSpreadDraw)
                .filter_by(user_id=user.id)
                .order_by(db_models.TarotSpreadDraw.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()
        history: List[api_models.TarotSpreadRecord] = []
        for row in rows:
            spread_result = self._build_spread_result(row.spread_id, user, row.draw_date, locale=locale)
            history.append(
                api_models.TarotSpreadRecord(
                    draw_date=row.draw_date.isoformat(),
                    created_at=row.created_at.isoformat() if row.created_at else None,
                    spread=spread_result,
                )
            )
        return api_models.TarotSpreadHistoryResponse(history=history)

    def get_reminder_setting(self, user: db_models.User) -> api_models.TarotReminderSettings:
        session = SessionLocal()
        try:
            setting = (
                session.query(db_models.TarotReminderSetting)
                .filter_by(user_id=user.id)
                .first()
            )
        finally:
            session.close()
        if not setting:
            return api_models.TarotReminderSettings(
                enabled=False,
                timezone=DEFAULT_REMINDER_TZ,
                hour=DEFAULT_REMINDER_HOUR,
                minute=DEFAULT_REMINDER_MINUTE,
            )
        return api_models.TarotReminderSettings(
            enabled=setting.enabled,
            timezone=setting.timezone,
            hour=setting.hour,
            minute=setting.minute,
            next_run_at=setting.next_run_at.isoformat() if setting.next_run_at else None,
            last_sent_at=setting.last_sent_at.isoformat() if setting.last_sent_at else None,
        )

    def update_reminder_setting(
        self, user: db_models.User, payload: api_models.TarotReminderUpdate
    ) -> api_models.TarotReminderSettings:
        timezone_name = payload.timezone or DEFAULT_REMINDER_TZ
        tz = self._safe_timezone(timezone_name)
        next_run = self._compute_next_run(tz, payload.hour, payload.minute)
        session = SessionLocal()
        try:
            setting = (
                session.query(db_models.TarotReminderSetting)
                .filter_by(user_id=user.id)
                .first()
            )
            if setting:
                setting.enabled = payload.enabled
                setting.timezone = timezone_name
                setting.hour = payload.hour
                setting.minute = payload.minute
                setting.next_run_at = next_run
            else:
                setting = db_models.TarotReminderSetting(
                    user_id=user.id,
                    enabled=payload.enabled,
                    timezone=timezone_name,
                    hour=payload.hour,
                    minute=payload.minute,
                    next_run_at=next_run,
                )
            session.add(setting)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        return api_models.TarotReminderSettings(
            enabled=setting.enabled,
            timezone=setting.timezone,
            hour=setting.hour,
            minute=setting.minute,
            next_run_at=setting.next_run_at.isoformat() if setting.next_run_at else None,
            last_sent_at=setting.last_sent_at.isoformat() if setting.last_sent_at else None,
        )

    def record_reminder_sent(self, user_id: int) -> None:
        session = SessionLocal()
        try:
            setting = (
                session.query(db_models.TarotReminderSetting)
                .filter_by(user_id=user_id)
                .first()
            )
            if not setting:
                return
            setting.last_sent_at = datetime.now(timezone.utc)
            setting.next_run_at = self._compute_next_run(
                self._safe_timezone(setting.timezone),
                setting.hour,
                setting.minute,
            )
            session.add(setting)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_due_reminders(self, *, limit: int = 50, now: datetime | None = None) -> List[db_models.TarotReminderSetting]:
        reference = now or datetime.now(timezone.utc)
        session = SessionLocal()
        try:
            rows = (
                session.query(db_models.TarotReminderSetting)
                .filter(
                    db_models.TarotReminderSetting.enabled.is_(True),
                    db_models.TarotReminderSetting.next_run_at <= reference,
                )
                .order_by(db_models.TarotReminderSetting.next_run_at.asc())
                .limit(limit)
                .all()
            )
            return rows
        finally:
            session.close()

    def get_favorites(self, user: db_models.User) -> List[int]:
        """Get list of favorite card IDs for user."""
        session = SessionLocal()
        try:
            favorites = session.query(db_models.TarotFavorite).filter_by(user_id=user.id).all()
            return [fav.card_id for fav in favorites]
        finally:
            session.close()

    def toggle_favorite(self, user: db_models.User, card_id: int) -> bool:
        """Toggle favorite status for a card. Returns True if added, False if removed."""
        session = SessionLocal()
        try:
            existing = (
                session.query(db_models.TarotFavorite)
                .filter_by(user_id=user.id, card_id=card_id)
                .first()
            )
            if existing:
                session.delete(existing)
                session.commit()
                return False
            else:
                favorite = db_models.TarotFavorite(user_id=user.id, card_id=card_id)
                session.add(favorite)
                session.commit()
                return True
        except IntegrityError:
            session.rollback()
            return False
        finally:
            session.close()

    def generate_reminder_ics(
        self, user: db_models.User, *, locale: str | None = None, occurrences: int = 14
    ) -> str:
        session = SessionLocal()
        try:
            setting = (
                session.query(db_models.TarotReminderSetting)
                .filter_by(user_id=user.id)
                .first()
            )
        finally:
            session.close()
        if not setting or not setting.enabled:
            raise ValueError("Reminders are not enabled.")
        tz = self._safe_timezone(setting.timezone)
        summary = translate("tarot.reminder.ics.summary", locale=locale, default="Tarot Flow reminder")
        description = translate(
            "tarot.reminder.ics.description",
            locale=locale,
            default="Open your TodayFlow dashboard to pull today's Tarot Flow spread.",
        )
        starts = self._upcoming_occurrences(tz, setting.hour, setting.minute, occurrences)
        now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        events = []
        for start in starts:
            dtstart = start.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            dtend = (start + timedelta(minutes=15)).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            uid = f"{uuid4()}@todayflow"
            events.append(
                "\n".join(
                    [
                        "BEGIN:VEVENT",
                        f"UID:{uid}",
                        f"DTSTAMP:{now_stamp}",
                        f"SUMMARY:{summary}",
                        f"DESCRIPTION:{description}",
                        f"DTSTART:{dtstart}",
                        f"DTEND:{dtend}",
                        "END:VEVENT",
                    ]
                )
            )
        return "\n".join(
            [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//TodayFlow//TarotReminder//EN",
                *events,
                "END:VCALENDAR",
            ]
        )

    def _ensure_draw_for_date(self, user: db_models.User, target_date: date) -> db_models.TarotDraw:
        session = SessionLocal()
        try:
            draw = (
                session.query(db_models.TarotDraw)
                .filter_by(user_id=user.id, draw_date=target_date)
                .order_by(db_models.TarotDraw.created_at.desc())
                .first()
            )
            if not draw:
                draw = self._create_draw(session, user, target_date)
            return draw
        finally:
            session.close()

    def _create_draw(self, session, user: db_models.User, draw_date: date) -> db_models.TarotDraw:
        # For public user (id=0), use date-based seed instead of user.id
        user_seed = 0 if user.id == 0 else user.id
        seed = self._stable_seed(user_seed, draw_date.isoformat())
        card = self.cards[seed % len(self.cards)]
        orientation = "reversed" if self._stable_seed(user_seed, draw_date.isoformat(), "orientation") % 2 else "upright"
        axes = card.get("correspondences", {}).get("axes", [])
        mantra = self._pick_item(self.mantras, axes, user_seed, draw_date, "mantra")
        ritual = self._pick_item(self.rituals, axes, user_seed, draw_date, "ritual")

        db_draw = db_models.TarotDraw(
            user_id=user.id,
            card_id=str(card["id"]),
            orientation=orientation,
            mantra_id=mantra["id"] if mantra else None,
            ritual_id=ritual["id"] if ritual else None,
            draw_date=draw_date,
        )
        session.add(db_draw)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            db_draw = (
                session.query(db_models.TarotDraw)
                .filter_by(user_id=user.id, draw_date=draw_date)
                .order_by(db_models.TarotDraw.created_at.desc())
                .first()
            )
        return db_draw

    def _pick_item(
        self,
        collection: List[Dict[str, Any]],
        axes: List[str],
        user_id: int,
        draw_date: date,
        salt: str,
    ) -> Dict[str, Any] | None:
        if not collection:
            return None
        axis_set = set(axes)
        candidates = [item for item in collection if axis_set.intersection(item.get("axes", []))]
        pool = candidates if candidates else collection
        index = self._stable_seed(user_id, draw_date.isoformat(), salt) % len(pool)
        return pool[index]

    def _deal_cards(self, count: int, user_id: int, token: str) -> List[Dict[str, Any]]:
        rng = Random(self._stable_seed(user_id, token, "deck"))
        deck = list(self.cards)
        rng.shuffle(deck)
        return deck[:count]

    @staticmethod
    def _safe_timezone(name: str) -> ZoneInfo:
        try:
            return ZoneInfo(name)
        except Exception:
            return ZoneInfo(DEFAULT_REMINDER_TZ)

    @staticmethod
    def _compute_next_run(tz: ZoneInfo, hour: int, minute: int) -> datetime:
        now = datetime.now(tz)
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate = candidate + timedelta(days=1)
        return candidate.astimezone(timezone.utc)

    @staticmethod
    def _upcoming_occurrences(tz: ZoneInfo, hour: int, minute: int, count: int) -> List[datetime]:
        start = datetime.now(tz)
        first = start.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if first <= start:
            first += timedelta(days=1)
        occurrences = []
        current = first
        for _ in range(max(count, 1)):
            occurrences.append(current)
            current = current + timedelta(days=1)
        return occurrences

    @staticmethod
    def _calculate_streak(draws: List[db_models.TarotDraw], reference_date: date) -> int:
        streak = 0
        expected = reference_date
        for draw in sorted(draws, key=lambda d: d.draw_date, reverse=True):
            if draw.draw_date == expected:
                streak += 1
                expected = expected - timedelta(days=1)
            elif draw.draw_date > expected:
                continue
            else:
                break
        return streak

    @staticmethod
    def _stable_seed(user_id: int, token: str, salt: str | None = None) -> int:
        payload = f"{user_id}:{token}"
        if salt:
            payload = f"{payload}:{salt}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return int(digest[:12], 16)

    def _generate_public_daily_draw(self, draw_date: date, *, locale: str | None = None) -> api_models.TarotDailyDraw:
        """Generate daily draw for public access (not saved to DB)."""
        seed = self._stable_seed(0, draw_date.isoformat())
        card = self.cards[seed % len(self.cards)]
        orientation = "reversed" if self._stable_seed(0, draw_date.isoformat(), "orientation") % 2 else "upright"
        axes = card.get("correspondences", {}).get("axes", [])
        mantra_data = self._pick_item(self.mantras, axes, 0, draw_date, "mantra")
        ritual_data = self._pick_item(self.rituals, axes, 0, draw_date, "ritual")
        
        card_model = api_models.TarotCard(
            id=card["id"],
            name=card["name"],
            keywords=card.get("keywords", []),
            upright=card.get("upright", ""),
            reversed=card.get("reversed", ""),
            correspondences=card.get("correspondences", {}),
        )
        
        # Localize and add human_text (same approach as _to_model)
        mantra_dict = localize_mantra(mantra_data, locale=locale) if mantra_data else None
        ritual_dict = localize_ritual(ritual_data, locale=locale) if ritual_data else None
        
        if mantra_dict:
            mantra_id = mantra_dict.get("id")
            if mantra_id:
                try:
                    content_mantra = content_system.get_mantra_by_id(mantra_id)
                    if content_mantra and content_mantra.get("human_text"):
                        mantra_dict["human_text"] = content_mantra["human_text"]
                except Exception:
                    pass
        
        if ritual_dict:
            ritual_id = ritual_dict.get("id")
            if ritual_id:
                try:
                    content_ritual = content_system.get_ritual_by_id(ritual_id)
                    if content_ritual and content_ritual.get("human_text"):
                        ritual_dict["human_text"] = content_ritual["human_text"]
                except Exception:
                    pass
        
        return api_models.TarotDailyDraw(
            date=draw_date.isoformat(),
            selection_status="selected",
            card=card_model,
            orientation=orientation,
            mantra=api_models.Mantra(**mantra_dict) if mantra_dict else None,
            ritual=api_models.Ritual(**ritual_dict) if ritual_dict else None,
        )

    def _to_model(self, draw: db_models.TarotDraw, locale: str | None = None) -> api_models.TarotDailyDraw:
        card_data = self.card_map.get(draw.card_id)
        if not card_data:
            raise ValueError(f"Unknown tarot card id {draw.card_id}")
        mantra_data = next((m for m in self.mantras if m["id"] == draw.mantra_id), None)
        ritual_data = next((r for r in self.rituals if r["id"] == draw.ritual_id), None)
        
        # Localize mantra and ritual, then add human_text from Content System
        mantra_dict = localize_mantra(mantra_data, locale=locale) if mantra_data else None
        ritual_dict = localize_ritual(ritual_data, locale=locale) if ritual_data else None
        
        # Add human_text from Content System
        if mantra_dict:
            mantra_id = mantra_dict.get("id") or (mantra_data.get("id") if mantra_data else None)
            if mantra_id:
                try:
                    content_mantra = content_system.get_mantra_by_id(mantra_id)
                    if content_mantra and content_mantra.get("human_text"):
                        mantra_dict["human_text"] = content_mantra["human_text"]
                except Exception:
                    pass  # Fallback to existing data
        
        if ritual_dict:
            ritual_id = ritual_dict.get("id") or (ritual_data.get("id") if ritual_data else None)
            if ritual_id:
                try:
                    content_ritual = content_system.get_ritual_by_id(ritual_id)
                    if content_ritual and content_ritual.get("human_text"):
                        ritual_dict["human_text"] = content_ritual["human_text"]
                except Exception:
                    pass  # Fallback to existing data
        
        return api_models.TarotDailyDraw(
            date=draw.draw_date.isoformat(),
            selection_status="selected",
            card=api_models.TarotCard(**card_data),
            orientation=draw.orientation,
            mantra=api_models.Mantra(**mantra_dict) if mantra_dict else None,
            ritual=api_models.Ritual(**ritual_dict) if ritual_dict else None,
        )

    def _record_spread_draw(self, user_id: int, spread_id: str, draw_date: date) -> None:
        session = SessionLocal()
        try:
            existing = (
                session.query(db_models.TarotSpreadDraw)
                .filter_by(user_id=user_id, spread_id=spread_id, draw_date=draw_date)
                .first()
            )
            if existing:
                existing.created_at = utc_naive_now()
                session.add(existing)
            else:
                session.add(
                    db_models.TarotSpreadDraw(user_id=user_id, spread_id=spread_id, draw_date=draw_date)
                )
            session.commit()
        except IntegrityError:
            session.rollback()
        finally:
            session.close()

    def _build_spread_result(
        self,
        spread_id: str | None,
        user: db_models.User,
        draw_date: date,
        *,
        locale: str | None = None,
        selected_cards: List[api_models.TarotSelectedCard] | None = None,
    ) -> api_models.TarotSpreadResult:
        if not self.spreads:
            raise ValueError("Tarot spreads are not configured.")
        target_id = spread_id or self.default_spread_id
        spread_meta = self.spreads.get(target_id)
        if not spread_meta:
            spread_meta = next(iter(self.spreads.values()))
            target_id = spread_meta["id"]
        localized_spread = localize_spread_meta(spread_meta, locale=locale)
        positions = localized_spread.get("positions", [])
        if not positions:
            raise ValueError(f"Spread {target_id} has no positions defined.")

        token = f"{target_id}:{draw_date.isoformat()}"
        if selected_cards and len(selected_cards) >= len(positions):
            deck = []
            for item in selected_cards[: len(positions)]:
                card_data = self.card_map.get(str(item.card_id))
                if not card_data:
                    continue
                deck.append(card_data)
            if len(deck) < len(positions):
                deck = self._deal_cards(len(positions), user.id, token)
        else:
            deck = self._deal_cards(len(positions), user.id, token)

        cards: List[api_models.TarotSpreadCard] = []
        for idx, position in enumerate(positions):
            card_data = deck[idx]
            card_model = api_models.TarotCard(**card_data)
            selected_orientation = None
            if selected_cards and idx < len(selected_cards):
                selected_orientation = str(selected_cards[idx].orientation or "").strip().lower()
            orientation = (
                selected_orientation
                if selected_orientation in {"upright", "reversed"}
                else ("reversed" if self._stable_seed(user.id, f"{token}:{position['id']}", "spread") % 2 else "upright")
            )
            meaning = card_data["reversed"] if orientation == "reversed" else card_data["upright"]

            axes = list(
                set(position.get("axes", []))
                .union(card_data.get("correspondences", {}).get("axes", []) or [])
            )
            mantra_data = self._pick_item(self.mantras, axes, user.id, draw_date, f"{target_id}:{position['id']}:mantra")
            ritual_data = self._pick_item(self.rituals, axes, user.id, draw_date, f"{target_id}:{position['id']}:ritual")

            # Localize and add human_text (same approach as _to_model)
            mantra_dict = localize_mantra(mantra_data, locale=locale) if mantra_data else None
            ritual_dict = localize_ritual(ritual_data, locale=locale) if ritual_data else None
            
            if mantra_dict:
                mantra_id = mantra_dict.get("id")
                if mantra_id:
                    try:
                        content_mantra = content_system.get_mantra_by_id(mantra_id)
                        if content_mantra and content_mantra.get("human_text"):
                            mantra_dict["human_text"] = content_mantra["human_text"]
                    except Exception:
                        pass
            
            if ritual_dict:
                ritual_id = ritual_dict.get("id")
                if ritual_id:
                    try:
                        content_ritual = content_system.get_ritual_by_id(ritual_id)
                        if content_ritual and content_ritual.get("human_text"):
                            ritual_dict["human_text"] = content_ritual["human_text"]
                    except Exception:
                        pass

            cards.append(
                api_models.TarotSpreadCard(
                    position=api_models.TarotSpreadPosition(
                        id=position["id"],
                        title=position["title"],
                        prompt=position.get("prompt"),
                    ),
                    card=card_model,
                    orientation=orientation,
                    meaning=meaning,
                    mantra=api_models.Mantra(**mantra_dict) if mantra_dict else None,
                    ritual=api_models.Ritual(**ritual_dict) if ritual_dict else None,
                )
            )

        # Try to get human_text from Content System
        human_text = None
        try:
            content_spread = content_system.get_tarot_spread_by_id(target_id)
            if content_spread and content_spread.get("human_text"):
                human_text = content_spread["human_text"]
        except Exception:
            pass  # Fallback to existing data
        
        return api_models.TarotSpreadResult(
            spread_id=target_id,
            title=localized_spread.get("title", target_id),
            description=localized_spread.get("description"),
            cards=cards,
            human_text=human_text,
        )

    def draw_cards_from_deck(
        self, user: db_models.User, count: int = 10, *, locale: str | None = None
    ) -> List[api_models.TarotCard]:
        """Draw cards from deck for interactive selection."""
        from datetime import date
        token = f"{user.id}:{date.today().isoformat()}:deck"
        deck = self._deal_cards(count, user.id, token)
        
        cards: List[api_models.TarotCard] = []
        for card_data in deck:
            # Карты уже локализованы в данных, используем напрямую
            cards.append(
                api_models.TarotCard(
                    id=card_data["id"],
                    name=card_data["name"],
                    keywords=card_data.get("keywords", []),
                    upright=card_data.get("upright", ""),
                    reversed=card_data.get("reversed", ""),
                    correspondences=card_data.get("correspondences", {}),
                )
            )
        return cards


async def get_tarot_service() -> TarotService:
    return TarotService()
