"Database models for TodayFlow backend."

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Date, ForeignKey, Integer, String, JSON, Boolean, UniqueConstraint, Text, Time, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_naive_now() -> datetime:
    """UTC instant as naive datetime (columns use DateTime without timezone=True)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)
    is_paid = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    # Максимальный достигнутый индекс роста (0–100): кольца не «гаснут» при просадке индекса
    reward_evolution_index_peak = Column(Integer, nullable=False, default=0)
    stripe_customer_id = Column(String, nullable=True)
    subscription_status = Column(String, default="none")  # 'none', 'active', 'past_due', 'canceled', 'trialing'
    created_at = Column(DateTime, default=utc_naive_now)

    profiles = relationship("UserProfile", back_populates="user")
    astro_profiles = relationship("AstroProfile", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    challenge_participants = relationship("ChallengeParticipant", back_populates="user", cascade="all, delete-orphan")
    practice_usages = relationship("PracticeUsage", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    saved_forecasts = relationship("SavedForecast", back_populates="user", cascade="all, delete-orphan")
    saved_calculations = relationship("SavedCalculation", back_populates="user", cascade="all, delete-orphan")
    promo_code_usages = relationship("PromoCodeUsage", back_populates="user", cascade="all, delete-orphan")
    # Контур влияния
    progress_tracker_entries = relationship("ProgressTrackerEntry", back_populates="user", cascade="all, delete-orphan")
    observation_diary_entries = relationship("ObservationDiaryEntry", back_populates="user", cascade="all, delete-orphan")
    day_connections = relationship("DayConnection", back_populates="user", cascade="all, delete-orphan")
    day_rituals = relationship("DayRitual", back_populates="user", cascade="all, delete-orphan")
    auto_insights = relationship("AutoInsight", back_populates="user", cascade="all, delete-orphan")
    weekly_integrations = relationship("WeeklyIntegration", back_populates="user", cascade="all, delete-orphan")
    weekly_goals = relationship("WeeklyGoal", back_populates="user", cascade="all, delete-orphan")
    weekly_goal_steps = relationship("WeeklyGoalStep", back_populates="user", cascade="all, delete-orphan")
    state_check_ins = relationship("StateCheckIn", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    habit_entries = relationship("HabitEntry", back_populates="user", cascade="all, delete-orphan")
    ascetic_contracts = relationship("AsceticContract", back_populates="user", cascade="all, delete-orphan")
    # Календарь-органайзер
    calendar_events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")
    calendar_notes = relationship("CalendarNote", back_populates="user", cascade="all, delete-orphan")
    menstrual_cycles = relationship("MenstrualCycle", back_populates="user", cascade="all, delete-orphan")
    core_profile_snapshots = relationship("CoreProfileSnapshot", back_populates="user", cascade="all, delete-orphan")
    generation_logs = relationship("GenerationLog", back_populates="user", cascade="all, delete-orphan")
    generation_feedback = relationship("GenerationFeedback", back_populates="user", cascade="all, delete-orphan")
    push_devices = relationship("PushDevice", back_populates="user", cascade="all, delete-orphan")
    push_schedule = relationship("UserPushSchedule", back_populates="user", uselist=False, cascade="all, delete-orphan")
    daily_goal_snapshots = relationship("DailyGoalSnapshot", back_populates="user", cascade="all, delete-orphan")
    push_dispatch_logs = relationship("PushDispatchLog", back_populates="user", cascade="all, delete-orphan")
    meaning_events = relationship("MeaningEvent", back_populates="user", cascade="all, delete-orphan")
    active_knowledge_records = relationship(
        "UserActiveKnowledge", back_populates="user", cascade="all, delete-orphan"
    )
    cum_confidence_snapshots = relationship(
        "CumConfidenceSnapshot", back_populates="user", cascade="all, delete-orphan"
    )


class CumConfidenceSnapshot(Base):
    """Daily CUM confidence point for delta_30d (UMTS §3.6 · Learning Output #4)."""

    __tablename__ = "cum_confidence_snapshots"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    overall = Column(Float, nullable=False)
    by_domain = Column(JSON, nullable=False, default=dict)
    meaning_events_28d = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="cum_confidence_snapshots")
    __table_args__ = (
        UniqueConstraint("user_id", "snapshot_date", name="uq_cum_confidence_snapshot_user_date"),
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_version = Column(String, nullable=False)
    axes = Column(JSON, nullable=False)
    modulators = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="profiles")
    reports = relationship("GeneratedReport", back_populates="profile")


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    profile_id = Column(Integer, ForeignKey("user_profiles.id"))
    product_type = Column(String, nullable=False)
    content_version = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="reports")
    profile = relationship("UserProfile", back_populates="reports")


class ParagraphOverride(Base):
    __tablename__ = "paragraph_overrides"

    id = Column(Integer, primary_key=True)
    paragraph_id = Column(String, unique=True, nullable=False)
    lite_enabled = Column(Boolean, default=True)
    full_enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)


class ParagraphTextOverride(Base):
    __tablename__ = "paragraph_text_overrides"

    id = Column(Integer, primary_key=True)
    paragraph_id = Column(String, nullable=False)
    variant_id = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)
    __table_args__ = (UniqueConstraint("paragraph_id", "variant_id", name="uq_paragraph_variant"),)


class ParagraphAudit(Base):
    __tablename__ = "paragraph_audit"

    id = Column(Integer, primary_key=True)
    paragraph_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)


class TarotDraw(Base):
    __tablename__ = "tarot_draws"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(String, nullable=False)
    orientation = Column(String, nullable=False)  # upright / reversed
    mantra_id = Column(String, nullable=True)
    ritual_id = Column(String, nullable=True)
    draw_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    __table_args__ = (UniqueConstraint("user_id", "draw_date", name="uq_user_draw_date"),)


class TarotSpreadDraw(Base):
    __tablename__ = "tarot_spread_draws"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    spread_id = Column(String, nullable=False)
    draw_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    __table_args__ = (UniqueConstraint("user_id", "spread_id", "draw_date", name="uq_spread_user_draw"),)


class TarotReminderSetting(Base):
    __tablename__ = "tarot_reminder_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    timezone = Column(String, nullable=False, default="UTC")
    hour = Column(Integer, nullable=False, default=9)
    minute = Column(Integer, nullable=False, default=0)
    enabled = Column(Boolean, default=True)
    last_sent_at = Column(DateTime, nullable=True)


class TarotFavorite(Base):
    __tablename__ = "tarot_favorites"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)
    
    __table_args__ = (UniqueConstraint("user_id", "card_id", name="uq_user_card"),)


class SavedForecast(Base):
    """My Library — сохранённые DailyForecast (Web Canon v1)."""

    __tablename__ = "saved_forecasts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    forecast_id = Column(String, nullable=False)  # e.g. forecast-2026-01-20-ru
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="saved_forecasts")

    __table_args__ = (UniqueConstraint("user_id", "forecast_id", name="uq_user_forecast"),)


class SavedCalculation(Base):
    """My Library — сохранённые расчёты калькуляторов (Вертикаль 2). payload = { input, output, version }."""

    __tablename__ = "saved_calculations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    calc_type = Column(String, nullable=False)  # life_path | birthday_number | personal_year
    key = Column(String, nullable=False)  # e.g. life_path:1990-01-15
    payload = Column(JSON, nullable=False)  # { input, output, version }
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="saved_calculations")

    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_user_calc_key"),)


class NumerologyProfileRecord(Base):
    __tablename__ = "numerology_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    locale = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    __table_args__ = (UniqueConstraint("user_id", "full_name", "birth_date", name="uq_numerology_profile"),)


class AstroProfile(Base):
    __tablename__ = "astro_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time, nullable=True)
    time_unknown = Column(Boolean, default=False)
    timezone_offset_minutes = Column(Integer, nullable=True)
    timezone_name = Column(String, nullable=True)
    location_name = Column(String, nullable=True)  # Birth location
    latitude = Column(Float, nullable=True)  # Birth location latitude
    longitude = Column(Float, nullable=True)  # Birth location longitude
    current_residence_city = Column(String, nullable=True)  # Current city of residence (for local transits/solar return)
    current_residence_latitude = Column(Float, nullable=True)  # Current residence latitude
    current_residence_longitude = Column(Float, nullable=True)  # Current residence longitude
    relation = Column(String, nullable=True)  # self | partner | child | close_person
    notes = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False)
    birth_facts_correction_count = Column(Integer, default=0, nullable=False)
    birth_facts_last_changed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="astro_profiles")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String, unique=True, nullable=False)
    stripe_price_id = Column(String, nullable=False)
    plan_id = Column(String, nullable=False)  # 'lite_plus', 'full_access', 'tarot_plus', etc.
    status = Column(String, nullable=False)  # 'active', 'past_due', 'canceled', 'trialing'
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="subscriptions")
    history = relationship("SubscriptionHistory", back_populates="subscription", cascade="all, delete-orphan")


class SubscriptionHistory(Base):
    __tablename__ = "subscription_history"

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    stripe_invoice_id = Column(String, nullable=True)
    stripe_payment_intent_id = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)  # in cents
    currency = Column(String, default="usd")
    status = Column(String, nullable=False)  # 'paid', 'pending', 'failed', 'refunded'
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    subscription = relationship("Subscription", back_populates="history")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    greeting = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    country = Column(String, nullable=True)
    language = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    stay_logged_in = Column(Boolean, default=True)
    newsletter_opt_in = Column(Boolean, default=False)
    push_opt_in = Column(Boolean, default=False)
    subscriptions = Column(JSON, nullable=False, default=list)
    astrology_level = Column(String, default="beginner")  # 'beginner', 'intermediate', 'advanced'
    text_preference = Column(String, default="detailed")  # 'brief', 'detailed', 'comprehensive'
    # DE-8: quick | normal | deep — объём одного вызова Today narrative (не тариф insight).
    today_narrative_depth_level = Column(String, default="normal", nullable=False)
    gender = Column(String, nullable=True)  # 'female', 'male', 'unspecified'
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="settings")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # 'observation', 'gratitude', 'insight'
    content = Column(Text, nullable=False)
    # Контекстная подстановка (автоматически привязывается системой)
    practice_id = Column(String, nullable=True)  # ID практики, если запись после практики
    tarot_card_id = Column(String, nullable=True)  # ID карты таро, если запись после таро
    pattern_axis_id = Column(String, nullable=True)  # A1-A7, если связан с паттерном
    day = Column(Date, nullable=True)  # Дата дня, если вечерняя запись
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="journal_entries")


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(String, primary_key=True)  # e.g., "gratitude-21"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    duration = Column(Integer, nullable=False)  # days
    goal = Column(String, nullable=False)
    challenge_type = Column(String, nullable=True, default="goal")  # "tracker", "ascetic", "goal", "habit"
    price = Column(Integer, nullable=True)  # in cents, null = free for Pro
    is_pro_only = Column(Boolean, default=False)
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    participants = relationship("ChallengeParticipant", back_populates="challenge", cascade="all, delete-orphan")
    day_tasks = relationship("ChallengeDayTask", back_populates="challenge", cascade="all, delete-orphan")


class ChallengeParticipant(Base):
    __tablename__ = "challenge_participants"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    started_at = Column(DateTime, default=utc_naive_now)
    completed_at = Column(DateTime, nullable=True)
    current_day = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="challenge_participants")
    challenge = relationship("Challenge", back_populates="participants")
    task_completions = relationship("ChallengeTaskCompletion", back_populates="participant", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge"),)


class ChallengeDayTask(Base):
    __tablename__ = "challenge_day_tasks"

    id = Column(Integer, primary_key=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    day_number = Column(Integer, nullable=False)  # 1, 2, 3, ... duration
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    task_type = Column(String, nullable=False, default="reflection")  # 'reflection', 'action', 'journal', 'meditation'
    order = Column(Integer, nullable=False, default=0)  # для сортировки задач в один день
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    challenge = relationship("Challenge", back_populates="day_tasks")
    completions = relationship("ChallengeTaskCompletion", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("challenge_id", "day_number", "order", name="uq_challenge_day_order"),)


class ChallengeTaskCompletion(Base):
    __tablename__ = "challenge_task_completions"

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey("challenge_participants.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("challenge_day_tasks.id"), nullable=False)
    completed_at = Column(DateTime, default=utc_naive_now)
    notes = Column(Text, nullable=True)  # опциональные заметки пользователя

    participant = relationship("ChallengeParticipant", back_populates="task_completions")
    task = relationship("ChallengeDayTask", back_populates="completions")

    __table_args__ = (UniqueConstraint("participant_id", "task_id", name="uq_participant_task"),)


class PracticeUsage(Base):
    """Отслеживание использования персонализированных практик для контроля лимитов по подпискам."""
    __tablename__ = "practice_usages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    practice_id = Column(String, nullable=False)  # ID практики из PRACTICES
    completed_at = Column(DateTime, default=utc_naive_now)
    week_start = Column(Date, nullable=False)  # Начало недели (понедельник) для подсчета лимитов
    is_personalized = Column(Boolean, default=True)  # Была ли практика персонализированной
    sequence_id = Column(String, nullable=True)  # Если это часть guided sequence
    step_number = Column(Integer, nullable=True)  # Номер шага в серии
    
    user = relationship("User", back_populates="practice_usages")

    __table_args__ = (
        # Индекс для быстрого подсчета лимитов по неделе
        # UniqueConstraint не нужен - пользователь может выполнять одну практику несколько раз
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="password_reset_tokens")

    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token for password reset."""
        import secrets
        return secrets.token_urlsafe(32)

    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)."""
        return self.expires_at > utc_naive_now() and self.used_at is None


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    discount_type = Column(String, nullable=False)  # 'percentage' or 'fixed_amount'
    discount_value = Column(Float, nullable=False)  # percentage (0-100) or amount in cents
    min_amount = Column(Integer, nullable=True)  # Minimum purchase amount in cents
    max_discount = Column(Integer, nullable=True)  # Maximum discount in cents (for percentage)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)  # None = unlimited
    current_uses = Column(Integer, default=0)
    applicable_to = Column(String, nullable=False)  # 'subscriptions', 'reports', 'all'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_naive_now)

    usages = relationship("PromoCodeUsage", back_populates="promo_code", cascade="all, delete-orphan")

    def is_valid(self, user_id: int | None = None, amount: int | None = None) -> tuple[bool, str]:
        """Check if promo code is valid. Returns (is_valid, error_message)."""
        if not self.is_active:
            return False, "Промокод неактивен"
        
        if utc_naive_now() < self.valid_from:
            return False, "Промокод еще не действителен"
        
        if self.valid_until and utc_naive_now() > self.valid_until:
            return False, "Промокод истек"
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return False, "Промокод исчерпан"
        
        if amount and self.min_amount and amount < self.min_amount:
            return False, f"Минимальная сумма для применения: {self.min_amount / 100:.2f}"
        
        # Check if user already used this code
        if user_id:
            from todayflow_backend.db.session import SessionLocal
            session = SessionLocal()
            try:
                from todayflow_backend.db.models import PromoCodeUsage
                existing = session.query(PromoCodeUsage).filter_by(
                    promo_code_id=self.id,
                    user_id=user_id
                ).first()
                if existing:
                    return False, "Вы уже использовали этот промокод"
            finally:
                session.close()
        
        return True, ""

    def calculate_discount(self, amount: int) -> int:
        """Calculate discount amount in cents."""
        if self.discount_type == "percentage":
            discount = int(amount * (self.discount_value / 100))
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount
        else:  # fixed_amount
            return min(int(self.discount_value), amount)


class PromoCodeUsage(Base):
    __tablename__ = "promo_code_usages"

    id = Column(Integer, primary_key=True)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(String, nullable=True)  # Stripe order/subscription ID
    discount_amount = Column(Integer, nullable=False)  # Discount in cents
    original_amount = Column(Integer, nullable=False)  # Original amount in cents
    final_amount = Column(Integer, nullable=False)  # Final amount after discount
    used_at = Column(DateTime, default=utc_naive_now)

    promo_code = relationship("PromoCode", back_populates="usages")
    user = relationship("User", back_populates="promo_code_usages")


# ============================================================================
# Контур влияния (Tracking & Influence Loop)
# ============================================================================

class ProgressTrackerEntry(Base):
    """Прогресс-трекер: фиксация выполнения аскез и аффирмаций."""
    __tablename__ = "progress_tracker_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    asceticism_id = Column(String, nullable=True)  # ID аскезы из asceticisms.json
    affirmation_id = Column(String, nullable=True)  # ID аффирмации из practices.json (type=affirmation)
    completed = Column(Boolean, nullable=False, default=False)
    state = Column(String, nullable=True)  # 1-2 слова: "calm", "tension", etc.
    state_scale = Column(Integer, nullable=True)  # 1-5
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="progress_tracker_entries")
    __table_args__ = (UniqueConstraint("user_id", "date", "asceticism_id", "affirmation_id", name="uq_user_date_practice"),)


class Habit(Base):
    """Пользовательская привычка."""
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    target_frequency = Column(String, nullable=False, default="daily")  # daily | weekly
    target_per_period = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="habits")
    entries = relationship("HabitEntry", back_populates="habit", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_habit_name"),)


class HabitEntry(Base):
    """Лог выполнения привычки за день."""
    __tablename__ = "habit_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    intensity = Column(Integer, nullable=True)  # 1-5, опционально
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="habit_entries")
    habit = relationship("Habit", back_populates="entries")
    __table_args__ = (UniqueConstraint("user_id", "habit_id", "date", name="uq_user_habit_entry_date"),)


class AsceticContract(Base):
    """Контракт аскезы с фиксацией прогресса."""
    __tablename__ = "ascetic_contracts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asceticism_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    intention = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="active")  # active | completed | paused
    streak_days = Column(Integer, nullable=False, default=0)
    longest_streak_days = Column(Integer, nullable=False, default=0)
    last_completed_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="ascetic_contracts")


class ObservationDiaryEntry(Base):
    """Дневник наблюдений: простое отражение без анализа."""
    __tablename__ = "observation_diary_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    noticed = Column(Text, nullable=False)  # "Что я заметил" (1-2 предложения)
    hardest = Column(Text, nullable=False)  # "Где было сложнее всего" (1-2 предложения)
    easier_than_expected = Column(Text, nullable=False)  # "Что оказалось легче, чем ожидал" (1-2 предложения)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="observation_diary_entries")
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date_diary"),)


class DayConnection(Base):
    """Связка дня: связь между утренним намерением и вечерним завершением."""
    __tablename__ = "day_connections"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    
    # Утреннее намерение
    morning_intention = Column(Text, nullable=True)  # Что хотел сделать/почувствовать
    morning_focus = Column(String(100), nullable=True)  # Фокус из morning ritual
    
    # Вечернее отражение
    evening_reflection = Column(Text, nullable=True)  # Что получилось, что изменилось
    evening_observations = Column(JSON, nullable=True)  # {noticed: "...", hardest: "...", easier: "..."}
    
    # Связующая нить
    connection_thread = Column(Text, nullable=True)  # Как утро связано с вечером
    ritual_feedback = Column(String(16), nullable=True)  # yes | partial | no
    quick_decision_answer = Column(String(16), nullable=True)  # yes | no | unclear
    question_of_day_answer = Column(String(120), nullable=True)  # selected answer id/label
    
    # Статус
    morning_completed = Column(Boolean, default=False)
    day_completed = Column(Boolean, default=False)
    evening_completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="day_connections")
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date_connection"),)


class DayRitual(Base):
    """Ритуал закрытия дня: 1 экран, 10 секунд."""
    __tablename__ = "day_rituals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    closing_phrase_id = Column(String, nullable=True)  # ID фразы из Lexicon
    closing_phrase_text = Column(Text, nullable=True)  # Текст фразы из Lexicon
    custom_closing_phrase = Column(Text, nullable=True)  # Своя завершающая фраза
    sufficiency_confirmed = Column(Boolean, nullable=False, default=False)
    
    # Расширение для кастомизации
    ritual_type = Column(String(50), default="template")  # "custom" | "template" | "combined"
    custom_elements = Column(JSON, nullable=True)  # [{type: "gratitude", content: "..."}, ...]
    day_connection_id = Column(Integer, ForeignKey("day_connections.id", ondelete="SET NULL"), nullable=True)
    observations = Column(JSON, nullable=True)  # {noticed: "...", hardest: "...", easier: "..."}
    
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="day_rituals")
    day_connection = relationship("DayConnection", foreign_keys=[day_connection_id])
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date_ritual"),)


class AutoInsight(Base):
    """Автоматические инсайты: система говорит пользователю, что происходит."""
    __tablename__ = "auto_insights"

    id = Column(String, primary_key=True)  # "insight.YYYYMMDDHHMMSS"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)  # "streak", "pattern", "shift"
    insight_text = Column(Text, nullable=False)
    data_points = Column(JSON, nullable=False)  # Дополнительные данные для инсайта
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="auto_insights")


class WeeklyIntegration(Base):
    """Недельная интеграция: раз в 7 дней, один абзац."""
    __tablename__ = "weekly_integrations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    integration_text = Column(Text, nullable=False)
    data_points = Column(JSON, nullable=False)  # most_common_state, where_held, where_released, etc.
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="weekly_integrations")
    __table_args__ = (UniqueConstraint("user_id", "week_start", "week_end", name="uq_user_week"),)


class WeeklyGoal(Base):
    """Цель в трекинге: фокус на неделю (week_start = понедельник) или на месяц (week_start = 1-е число)."""
    __tablename__ = "weekly_goals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    progress_days = Column(Integer, nullable=False, default=0)
    last_progress_date = Column(Date, nullable=True)
    scope = Column(String(16), nullable=False, default="week")  # week | month
    period_end = Column(Date, nullable=True)  # для month — последний день месяца
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="weekly_goals")
    steps = relationship("WeeklyGoalStep", back_populates="weekly_goal", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("user_id", "week_start", "title", name="uq_user_week_goal_title"),)


class WeeklyGoalStep(Base):
    """Отметка шага по цели в конкретный день (история для календаря)."""
    __tablename__ = "weekly_goal_steps"

    id = Column(Integer, primary_key=True)
    weekly_goal_id = Column(Integer, ForeignKey("weekly_goals.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    step_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="weekly_goal_steps")
    weekly_goal = relationship("WeeklyGoal", back_populates="steps")
    __table_args__ = (UniqueConstraint("weekly_goal_id", "step_date", name="uq_weekly_goal_step_date"),)


class StateCheckIn(Base):
    """Короткий чек-ин состояния: утро / день / вечер."""
    __tablename__ = "state_check_ins"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    checkin_date = Column(Date, nullable=False)
    phase = Column(String(16), nullable=False)  # morning | day | evening
    mood_scale = Column(Integer, nullable=True)  # 1–5
    energy_scale = Column(Integer, nullable=True)  # 1–5
    stress_scale = Column(Integer, nullable=True)  # 1–5
    note = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="state_check_ins")
    __table_args__ = (UniqueConstraint("user_id", "checkin_date", "phase", name="uq_state_checkin_user_date_phase"),)


class CalendarEvent(Base):
    """Календарное событие: органайзер событий и записей."""
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=True)  # Опционально, если "весь день"
    is_all_day = Column(Boolean, default=False)
    color = Column(String, nullable=True)  # Hex цвет для визуализации
    category = Column(String, nullable=True)  # "meeting", "personal", "practice", "yoga", etc.
    description = Column(Text, nullable=True)  # Описание события
    repeat_type = Column(String, nullable=True)  # "none", "daily", "weekly", "monthly"
    reminder_minutes = Column(Integer, nullable=True)  # За сколько минут напоминать
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="calendar_events")


class CalendarNote(Base):
    """Запись к дню или событию в календаре."""
    __tablename__ = "calendar_notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=True)  # Опционально, если привязана к событию
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="calendar_notes")
    event = relationship("CalendarEvent", foreign_keys=[event_id])
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date_note"),)


class MenstrualCycle(Base):
    """Трекинг менструального цикла (опционально)."""
    __tablename__ = "menstrual_cycles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    cycle_day = Column(Integer, nullable=True)  # День цикла (1-35)
    period_intensity = Column(String, nullable=True)  # "light", "medium", "heavy"
    ovulation = Column(Boolean, default=False)
    fertile_window = Column(Boolean, default=False)
    symptoms = Column(JSON, nullable=True)  # {"mood": 3, "energy": 2, "sleep": 4, "activity": ["tag1", "tag2"]}
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="menstrual_cycles")
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date_cycle"),)


class CachedNatalChart(Base):
    """Кеш натальной карты: вычисляем один раз и храним."""
    __tablename__ = "cached_natal_charts"

    id = Column(Integer, primary_key=True)
    astro_profile_id = Column(Integer, ForeignKey("astro_profiles.id", ondelete="CASCADE"), nullable=False, unique=True)
    positions = Column(JSON, nullable=False)  # Позиции планет
    houses = Column(JSON, nullable=False)     # Дома (включая асцендент, MC и т.д.)
    chart_metadata = Column(JSON, nullable=True)    # Метаданные (система домов, система координат и т.д.)
    computed_at = Column(DateTime, default=utc_naive_now)

    astro_profile = relationship("AstroProfile", backref="cached_natal_chart")


class CachedForecast(Base):
    """Кеш прогнозов: храним сгенерированные прогнозы."""
    __tablename__ = "cached_forecasts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    astro_profile_id = Column(Integer, ForeignKey("astro_profiles.id", ondelete="CASCADE"), nullable=False)
    forecast_type = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    forecast_date = Column(Date, nullable=False)        # Дата прогноза (для daily) или начальная дата (для weekly/monthly)
    locale = Column(String(10), nullable=False, default="ru")
    use_ai = Column(Boolean, default=False)              # Был ли использован ИИ
    forecast_data = Column(JSON, nullable=False)         # Полные данные прогноза
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", backref="cached_forecasts")
    astro_profile = relationship("AstroProfile", backref="cached_forecasts")

    __table_args__ = (
        UniqueConstraint("user_id", "astro_profile_id", "forecast_type", "forecast_date", "locale", "use_ai", name="uq_cached_forecast"),
    )


class CachedCompatibility(Base):
    """Кеш совместимости: храним рассчитанные результаты на ограниченное время."""
    __tablename__ = "cached_compatibility"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cache_key = Column(String(255), nullable=False)
    compatibility_type = Column(String(32), nullable=False)  # 'quick' | 'synastry'
    locale = Column(String(10), nullable=False, default="ru")
    result_data = Column(JSON, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", backref="cached_compatibility")

    __table_args__ = (
        UniqueConstraint("user_id", "cache_key", name="uq_cached_compatibility_key"),
    )


class CoreProfileSnapshot(Base):
    """Frozen core profile payload by user + profile hash."""
    __tablename__ = "core_profile_snapshots"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    profile_hash = Column(String(64), nullable=False)
    profile_version = Column(String(32), nullable=False, default="core-v1")
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="core_profile_snapshots")

    __table_args__ = (
        UniqueConstraint("user_id", "profile_hash", name="uq_user_core_profile_hash"),
    )


class PromptVersion(Base):
    """Stored prompt templates by module and version for evaluation and rollback."""
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True)
    module = Column(String(64), nullable=False)
    version = Column(String(64), nullable=False)
    prompt_kind = Column(String(32), nullable=False, default="system")
    label = Column(String(255), nullable=True)
    prompt_text = Column(Text, nullable=False)
    meta_payload = Column("metadata", JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    generation_logs = relationship("GenerationLog", back_populates="prompt_version")

    __table_args__ = (
        UniqueConstraint("module", "version", "prompt_kind", name="uq_prompt_version_kind"),
    )


class GenerationLog(Base):
    """One generation attempt with inputs, model settings, output and fallback state."""
    __tablename__ = "generation_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    core_profile_snapshot_id = Column(Integer, ForeignKey("core_profile_snapshots.id", ondelete="SET NULL"), nullable=True)
    prompt_version_id = Column(Integer, ForeignKey("prompt_versions.id", ondelete="SET NULL"), nullable=True)
    module = Column(String(64), nullable=False)
    surface = Column(String(64), nullable=True)
    model = Column(String(128), nullable=True)
    locale = Column(String(16), nullable=True)
    input_payload = Column(JSON, nullable=True)
    system_prompt = Column(Text, nullable=True)
    user_prompt = Column(Text, nullable=True)
    raw_response = Column(Text, nullable=True)
    normalized_response = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, default="success")
    used_fallback = Column(Boolean, nullable=False, default=False)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="generation_logs")
    core_profile_snapshot = relationship("CoreProfileSnapshot", backref="generation_logs")
    prompt_version = relationship("PromptVersion", back_populates="generation_logs")
    feedback = relationship("GenerationFeedback", back_populates="generation_log", cascade="all, delete-orphan")


class GenerationFeedback(Base):
    """Explicit user feedback and implicit lightweight quality signals for a generation."""
    __tablename__ = "generation_feedback"

    id = Column(Integer, primary_key=True)
    generation_log_id = Column(Integer, ForeignKey("generation_logs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    signal = Column(String(64), nullable=False)
    score = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)
    meta_payload = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)

    generation_log = relationship("GenerationLog", back_populates="feedback")
    user = relationship("User", back_populates="generation_feedback")


class PushDevice(Base):
    """FCM/APNs/Web push token registered for a user device."""

    __tablename__ = "push_devices"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(32), nullable=False)  # ios | android | web
    token = Column(Text, nullable=False)
    device_label = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="push_devices")
    __table_args__ = (UniqueConstraint("user_id", "token", name="uq_push_device_user_token"),)


class UserPushSchedule(Base):
    """Local-time schedule for Today rhythm pushes (morning / day / evening) and goal nudges."""

    __tablename__ = "user_push_schedules"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    timezone = Column(String(64), nullable=False, default="Europe/Moscow")
    morning_enabled = Column(Boolean, nullable=False, default=True)
    morning_time = Column(String(5), nullable=False, default="08:30")
    day_enabled = Column(Boolean, nullable=False, default=True)
    day_time = Column(String(5), nullable=False, default="13:00")
    evening_enabled = Column(Boolean, nullable=False, default=True)
    evening_time = Column(String(5), nullable=False, default="20:00")
    goal_midday_enabled = Column(Boolean, nullable=False, default=True)
    goal_midday_time = Column(String(5), nullable=False, default="12:30")
    goal_afternoon_enabled = Column(Boolean, nullable=False, default=True)
    goal_afternoon_time = Column(String(5), nullable=False, default="16:00")
    # Тихие часы (локальное время): не слать ритм/цель из крона; мгновенный goal_ack — по notify_goal_ack + тихие часы
    quiet_start = Column(String(5), nullable=False, default="22:00")
    quiet_end = Column(String(5), nullable=False, default="08:00")
    max_auto_per_day = Column(Integer, nullable=False, default=5)
    # Категории (будущие хуки читают те же флаги)
    notify_rhythm_today = Column(Boolean, nullable=False, default=True)
    notify_goal_nudges = Column(Boolean, nullable=False, default=True)
    notify_goal_ack = Column(Boolean, nullable=False, default=True)
    notify_streak_care = Column(Boolean, nullable=False, default=True)
    notify_weekly_focus = Column(Boolean, nullable=False, default=True)
    notify_tarot_card = Column(Boolean, nullable=False, default=True)
    notify_habit_reminders = Column(Boolean, nullable=False, default=True)
    notify_comeback = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="push_schedule")


class DailyGoalSnapshot(Base):
    """Latest daily goal text per user/date for goal reminder pushes."""

    __tablename__ = "daily_goal_snapshots"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_date = Column(Date, nullable=False)
    goal_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="daily_goal_snapshots")
    __table_args__ = (UniqueConstraint("user_id", "target_date", name="uq_daily_goal_user_date"),)


class PushDispatchLog(Base):
    """Dedupe log: one push kind per user per local calendar day."""

    __tablename__ = "push_dispatch_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dispatch_date = Column(Date, nullable=False)
    kind = Column(String(32), nullable=False)
    sent_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="push_dispatch_logs")
    __table_args__ = (UniqueConstraint("user_id", "dispatch_date", "kind", name="uq_push_dispatch_user_date_kind"),)


class DaySymbolState(Base):
    """Server SoT for card-of-day and day-number reveal (independent statuses).

    owner_key: ``u:{user_id}`` or ``g:{guest_session_id}``.
    Identity fields may be generated early but MUST NOT be returned until status is revealed/ready.
    """

    __tablename__ = "day_symbol_states"

    id = Column(Integer, primary_key=True)
    owner_key = Column(String(96), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    guest_session_id = Column(String(64), nullable=True)
    local_date = Column(Date, nullable=False)
    timezone_name = Column(String(64), nullable=False, default="UTC")

    card_status = Column(String(32), nullable=False, default="not_revealed")
    card_id = Column(String(32), nullable=True)
    card_orientation = Column(String(16), nullable=True)
    card_generated_at = Column(DateTime, nullable=True)
    card_revealed_at = Column(DateTime, nullable=True)
    card_reveal_source = Column(String(64), nullable=True)
    card_idempotency_key = Column(String(128), nullable=True)

    number_status = Column(String(32), nullable=False, default="not_revealed")
    number_value = Column(Integer, nullable=True)
    number_reduced = Column(Integer, nullable=True)
    number_is_master = Column(Boolean, nullable=False, default=False)
    number_title = Column(String(120), nullable=True)
    number_summary = Column(Text, nullable=True)
    number_generated_at = Column(DateTime, nullable=True)
    number_revealed_at = Column(DateTime, nullable=True)
    number_reveal_source = Column(String(64), nullable=True)
    number_idempotency_key = Column(String(128), nullable=True)

    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    __table_args__ = (
        UniqueConstraint("owner_key", "local_date", name="uq_day_symbol_owner_date"),
        UniqueConstraint("card_idempotency_key", name="uq_day_symbol_card_idem"),
        UniqueConstraint("number_idempotency_key", name="uq_day_symbol_number_idem"),
    )


class DayStoryState(Base):
    """Server SoT for day_story freshness vs fingerprint (rebuild after reveal/mood/goals).

    owner_key mirrors DaySymbolState: ``u:{user_id}`` or ``g:{guest_session_id}``.
    """

    __tablename__ = "day_story_states"

    id = Column(Integer, primary_key=True)
    owner_key = Column(String(96), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    guest_session_id = Column(String(64), nullable=True)
    local_date = Column(Date, nullable=False)
    timezone_name = Column(String(64), nullable=False, default="UTC")
    locale = Column(String(16), nullable=False, default="ru")

    # Last successfully persisted story fingerprint (matches GenerationLog.input_payload).
    fingerprint = Column(String(64), nullable=True)
    # Current expected fingerprint from live inputs (symbols/mood/goals/…).
    expected_fingerprint = Column(String(64), nullable=True)
    stale = Column(Boolean, nullable=False, default=False)
    # Bumped on every input change that invalidates story; used to drop stale LLM races.
    generation_seq = Column(Integer, nullable=False, default=0)
    last_generation_log_id = Column(Integer, ForeignKey("generation_logs.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    __table_args__ = (UniqueConstraint("owner_key", "local_date", name="uq_day_story_owner_date"),)


class GuestSession(Base):
    """Server-side guest identity for value-first funnel + protected claim."""

    __tablename__ = "guest_sessions"

    id = Column(Integer, primary_key=True)
    guest_session_id = Column(String(64), nullable=False, unique=True)
    # Secret bound to browser/device; hashed at rest. Required for progress writes.
    session_secret_hash = Column(String(128), nullable=False)
    locale = Column(String(16), nullable=True)
    timezone_name = Column(String(64), nullable=True)
    # Short-lived claim token (hashed); issued only for auth completion flow.
    claim_token_hash = Column(String(128), nullable=True)
    claim_token_expires_at = Column(DateTime, nullable=True)
    claim_nonce = Column(String(64), nullable=True)
    claimed_at = Column(DateTime, nullable=True)
    claimed_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    # After claim, guest session can no longer mutate user data.
    sealed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)


class GuestDaySnapshot(Base):
    """Server SoT for guest Today progress (mood/goals/onboarding/story…) before claim."""

    __tablename__ = "guest_day_snapshots"

    id = Column(Integer, primary_key=True)
    guest_session_id = Column(String(64), nullable=False)
    local_date = Column(Date, nullable=False)
    timezone_name = Column(String(64), nullable=False, default="UTC")
    locale = Column(String(16), nullable=False, default="ru")

    mood = Column(JSON, nullable=True)  # {mood, mood_scale, morning_mood_id, …}
    goals = Column(JSON, nullable=True)  # {day_goal, goals:[]}
    onboarding = Column(JSON, nullable=True)  # {intent_theme, reality_state, …}
    first_result = Column(JSON, nullable=True)  # First Today package / contract snapshot
    ritual = Column(JSON, nullable=True)  # RitualPersistedState
    today_state = Column(JSON, nullable=True)  # DayEngagementState + partial Today
    day_story = Column(JSON, nullable=True)  # story payload if generated for guest
    story_fingerprint = Column(String(64), nullable=True)
    story_status = Column(String(32), nullable=True)
    profile_draft = Column(JSON, nullable=True)  # guest profile draft fields (non-secret)

    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    __table_args__ = (UniqueConstraint("guest_session_id", "local_date", name="uq_guest_day_session_date"),)


class GuestClaimRecord(Base):
    """Idempotent claim audit: guest_session_id + target_user_id."""

    __tablename__ = "guest_claim_records"

    id = Column(Integer, primary_key=True)
    guest_session_id = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    local_date = Column(Date, nullable=True)
    claim_status = Column(String(32), nullable=False, default="completed")
    transferred_blocks = Column(JSON, nullable=False, default=list)
    conflicts = Column(JSON, nullable=False, default=list)
    story_status = Column(String(32), nullable=True)
    story_refresh_required = Column(Boolean, nullable=False, default=False)
    redirect_target = Column(String(256), nullable=False, default="/today?first=1")
    result_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_naive_now)

    __table_args__ = (
        UniqueConstraint("guest_session_id", "user_id", name="uq_guest_claim_session_user"),
    )


class MeaningEvent(Base):
    """Unified event stream for Meaning Rings scoring."""

    __tablename__ = "meaning_events"

    id = Column(Integer, primary_key=True)
    event_id = Column(String(64), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(64), nullable=False)
    event_source = Column(String(32), nullable=False)
    event_time = Column(DateTime, nullable=False, default=utc_naive_now)
    local_date = Column(Date, nullable=False)
    quality_score = Column(Float, nullable=False, default=1.0)
    payload = Column(JSON, nullable=True)
    idempotency_key = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)

    user = relationship("User", back_populates="meaning_events")
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_meaning_event_user_idempotency"),
    )


class UserActiveKnowledge(Base):
    """Persisted Active Knowledge records for Branch A hot path (day_active_knowledge_v1 payload)."""

    __tablename__ = "user_active_knowledge"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    knowledge_id = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_naive_now)
    updated_at = Column(DateTime, default=utc_naive_now, onupdate=utc_naive_now)

    user = relationship("User", back_populates="active_knowledge_records")
    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", name="uq_user_active_knowledge"),
    )
