"""Compute numerology profiles from name + birth date."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Tuple

from todayflow_backend.core import models as api_models
from todayflow_backend.data import numerology as numerology_ref
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import SessionLocal
from todayflow_backend.i18n import translate


class NumerologyError(ValueError):
    """Domain error with translation key."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass
class NumerologyService:
    letter_map: Dict[str, int]
    vowels: set[str]
    master_numbers: set[int]

    def __init__(self) -> None:
        self.letter_map = numerology_ref.letters()
        self.vowels = numerology_ref.vowels()
        self.master_numbers = numerology_ref.master_numbers()

    def compute_profile(
        self,
        full_name: str,
        birth_date: str,
        *,
        locale: str | None = None,
    ) -> api_models.NumerologyProfile:
        birth_digits = [ch for ch in birth_date if ch.isdigit()]
        if len(birth_digits) < 3:
            raise NumerologyError("invalidBirthDate")

        try:
            datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError as exc:
            raise NumerologyError("invalidBirthDate") from exc

        life_path_total = sum(int(ch) for ch in birth_digits)
        life_path = self._build_number("life_path", life_path_total, locale=locale)

        normalized_letters = [ch for ch in full_name.upper() if ch.isalpha() and ch in self.letter_map]
        if not normalized_letters:
            # Date-only numerology: name layer omitted (not an error).
            return api_models.NumerologyProfile(
                name=(full_name or "").strip(),
                birth_date=birth_date,
                life_path=life_path,
                expression=None,
                soul_urge=None,
                personality=None,
            )

        expression_total = self._sum_letters(normalized_letters)
        soul_total = self._sum_letters(ch for ch in normalized_letters if ch in self.vowels)
        personality_total = self._sum_letters(ch for ch in normalized_letters if ch not in self.vowels)

        return api_models.NumerologyProfile(
            name=full_name.strip(),
            birth_date=birth_date,
            life_path=life_path,
            expression=self._build_number("expression", expression_total, locale=locale),
            soul_urge=self._build_number("soul_urge", soul_total, locale=locale),
            personality=self._build_number("personality", personality_total, locale=locale),
        )

    def save_profile(self, user_id: int, profile: api_models.NumerologyProfile, locale: str | None = None) -> None:
        from sqlalchemy.exc import IntegrityError
        
        session = SessionLocal()
        try:
            birth_date = datetime.strptime(profile.birth_date, "%Y-%m-%d").date()
            
            # Проверяем, существует ли уже профиль
            existing = (
                session.query(db_models.NumerologyProfileRecord)
                .filter_by(
                    user_id=user_id,
                    full_name=profile.name,
                    birth_date=birth_date
                )
                .first()
            )
            
            if existing:
                # Обновляем существующий профиль
                existing.data = profile.model_dump()
                existing.locale = locale
                session.commit()
            else:
                # Создаем новый профиль
                record = db_models.NumerologyProfileRecord(
                    user_id=user_id,
                    locale=locale,
                    full_name=profile.name,
                    birth_date=birth_date,
                    data=profile.model_dump(),
                )
                session.add(record)
                session.commit()
        except IntegrityError:
            # Если все же произошла ошибка уникальности, пытаемся обновить существующий
            session.rollback()
            birth_date = datetime.strptime(profile.birth_date, "%Y-%m-%d").date()
            existing = (
                session.query(db_models.NumerologyProfileRecord)
                .filter_by(
                    user_id=user_id,
                    full_name=profile.name,
                    birth_date=birth_date
                )
                .first()
            )
            if existing:
                existing.data = profile.model_dump()
                existing.locale = locale
                session.commit()
            else:
                raise
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_profiles(self, user_id: int, limit: int = 5) -> List[api_models.NumerologyProfile]:
        session = SessionLocal()
        try:
            rows = (
                session.query(db_models.NumerologyProfileRecord)
                .filter_by(user_id=user_id)
                .order_by(db_models.NumerologyProfileRecord.created_at.desc())
                .limit(limit)
                .all()
            )
            return [api_models.NumerologyProfile(**row.data) for row in rows]
        finally:
            session.close()

    def daily_number(
        self,
        *,
        reference_date: date | None = None,
        locale: str | None = None,
        reveal: bool = True,
    ) -> api_models.NumerologyDailyInsight:
        """Calendar day number.

        Module GET should call with ``reveal=False`` so the value is not
        returned before the intended user reveal action. Today morning may
        still request ``reveal=True`` until server-side ritual ack lands.
        """
        target = reference_date or date.today()
        if not reveal:
            return api_models.NumerologyDailyInsight(
                date=target.isoformat(),
                selection_status="not_selected",
                number=None,
            )
        digits = [int(ch) for ch in target.strftime("%Y%m%d")]
        total = sum(digits)
        number = self._build_number("life_path", total, locale=locale)
        return api_models.NumerologyDailyInsight(
            date=target.isoformat(),
            selection_status="selected",
            number=number,
        )

    def _sum_letters(self, letters: Iterable[str]) -> int:
        total = 0
        for ch in letters:
            total += self.letter_map.get(ch, 0)
        return total

    def _reduce(self, value: int) -> int:
        if value <= 0:
            return 0
        while value > 9 and value not in self.master_numbers:
            value = sum(int(digit) for digit in str(value))
        return value

    def _reduce_with_steps(self, digits: List[int]) -> Tuple[int, List[api_models.CalcStep], bool]:
        """Редукция с шагами. Возвращает (final, steps, is_master). Master numbers из backend."""
        master = set(self.master_numbers)
        steps: List[api_models.CalcStep] = []
        current = digits
        while True:
            expr = "+".join(str(d) for d in current)
            s = sum(current)
            steps.append(api_models.CalcStep(expression=expr, sum=s))
            if s in master or s < 10:
                return (s, steps, s in master)
            current = [int(c) for c in str(s)]

    def life_path_calc(self, birth_date: str) -> api_models.NumerologyCalcResult:
        """Life Path: цифры даты YYYY-MM-DD без разделителей → сумма → редукция."""
        try:
            datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError as exc:
            raise NumerologyError("invalidBirthDate") from exc
        digits = [int(c) for c in birth_date if c.isdigit()]
        if len(digits) < 3:
            raise NumerologyError("invalidBirthDate")
        number, steps, is_master = self._reduce_with_steps(digits)
        master_list = sorted(self.master_numbers)
        return api_models.NumerologyCalcResult(
            calc_type="life_path",
            input={"birth_date": birth_date},
            output={"number": number, "steps": [s.model_dump() for s in steps]},
            is_master=is_master,
            master_numbers=master_list,
        )

    def birthday_number_calc(self, birth_day: int) -> api_models.NumerologyCalcResult:
        """Birthday Number: день месяца 1–31 → редукция."""
        if not 1 <= birth_day <= 31:
            raise NumerologyError("invalidBirthDate")
        digits = [int(c) for c in str(birth_day)]
        number, steps, is_master = self._reduce_with_steps(digits)
        master_list = sorted(self.master_numbers)
        return api_models.NumerologyCalcResult(
            calc_type="birthday_number",
            input={"birth_day": birth_day},
            output={"number": number, "steps": [s.model_dump() for s in steps]},
            is_master=is_master,
            master_numbers=master_list,
        )

    def personal_year_calc(self, birth_day: int, birth_month: int, year: int) -> api_models.NumerologyCalcResult:
        """Personal Year: birth_day + birth_month + year_digits_sum → редукция."""
        if not 1 <= birth_day <= 31 or not 1 <= birth_month <= 12:
            raise NumerologyError("invalidBirthDate")
        year_digits_sum = sum(int(c) for c in str(year))
        total = birth_day + birth_month + year_digits_sum
        steps: List[api_models.CalcStep] = [
            api_models.CalcStep(expression=f"{birth_day}+{birth_month}+{year_digits_sum}", sum=total),
        ]
        master = set(self.master_numbers)
        if total in master or total < 10:
            number, is_master = total, total in master
        else:
            current = [int(c) for c in str(total)]
            while True:
                expr = "+".join(str(d) for d in current)
                s = sum(current)
                steps.append(api_models.CalcStep(expression=expr, sum=s))
                if s in master or s < 10:
                    number, is_master = s, s in master
                    break
                current = [int(c) for c in str(s)]
        master_list = sorted(self.master_numbers)
        return api_models.NumerologyCalcResult(
            calc_type="personal_year",
            input={"birth_day": birth_day, "birth_month": birth_month, "year": year},
            output={"number": number, "steps": [s.model_dump() for s in steps]},
            is_master=is_master,
            master_numbers=master_list,
        )

    def _build_number(self, kind: str, total: int, *, locale: str | None) -> api_models.NumerologyNumber:
        reduced = self._reduce(total)
        label = translate(
            f"numerology.{kind}.title",
            locale=locale,
            default=kind.replace("_", " ").title(),
        )
        summary = self._translate_summary(kind, reduced, locale)
        return api_models.NumerologyNumber(
            title=label,
            value=total,
            reduced_value=reduced,
            is_master=reduced in self.master_numbers,
            summary=summary,
        )

    def _translate_summary(self, kind: str, value: int, locale: str | None) -> str:
        if value <= 0:
            return translate(
                "numerology.number.summary.0",
                locale=locale,
                default="This number asks for silence before action.",
            )
        specific = translate(
            f"numerology.{kind}.summary.{value}",
            locale=locale,
            default=None,
        )
        if specific:
            return specific
        general = translate(
            f"numerology.number.summary.{value}",
            locale=locale,
            default=None,
        )
        if general:
            return general
        return translate(
            "numerology.number.summary.default",
            locale=locale,
            default="This number invites reflection on how you express and direct your energy.",
        )


_NUM_SERVICE = NumerologyService()


def get_numerology_service() -> NumerologyService:
    return _NUM_SERVICE
