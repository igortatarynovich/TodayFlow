"""Zoroastrian horoscope service."""

from __future__ import annotations

from datetime import date
from typing import Optional

# Zoroastrian calendar has 12 months, each associated with a deity/guardian
ZOROASTRIAN_MONTHS = [
    "Fravardin",   # Guardian of souls, protection
    "Ardibehesht", # Fire, truth, order
    "Khordad",     # Perfection, health
    "Tir",         # Rain, fertility
    "Amurdad",     # Immortality, plants
    "Shahrevar",   # Metals, minerals, power
    "Mehr",        # Sun, friendship, love
    "Aban",        # Water, purification
    "Azar",        # Fire, energy
    "Dey",         # Creator, law
    "Bahman",      # Good mind, wisdom
    "Esfand",      # Earth, humility, devotion
]

# Zoroastrian calendar days (1-30 per month)
ZOROASTRIAN_DAYS = [
    "Ahura Mazda", "Bahman", "Ardibehesht", "Shahrevar", "Khordad",
    "Amurdad", "Dey", "Azar", "Aban", "Khorshid",
    "Mah", "Tir", "Gosh", "Dey", "Mehr",
    "Sorush", "Rashn", "Farvardin", "Bahram", "Ram",
    "Bad", "Dey", "Din", "Ashishvangh", "Ashtad",
    "Asman", "Zamyad", "Mantraspand", "Aniran", "Ahura Mazda",
]


class ZoroastrianHoroscopeService:
    """Service for calculating Zoroastrian horoscope."""

    def calculate(self, birth_date: date) -> dict:
        """Calculate Zoroastrian horoscope for birth date."""
        # Zoroastrian calendar is complex, using simplified version
        # Based on Persian calendar month and day
        
        month = birth_date.month
        day = birth_date.day
        
        # Map to Zoroastrian month (simplified)
        zoroastrian_month = ZOROASTRIAN_MONTHS[(month - 1) % 12]
        
        # Map to Zoroastrian day (simplified, using day of month)
        zoroastrian_day_index = (day - 1) % 30
        zoroastrian_day = ZOROASTRIAN_DAYS[zoroastrian_day_index]
        
        return {
            "month": zoroastrian_month,
            "day": zoroastrian_day,
            "description": self._get_description(zoroastrian_month, zoroastrian_day),
            "traits": self._get_traits(zoroastrian_month),
            "deity": self._get_deity_info(zoroastrian_month),
        }

    def _get_description(self, month: str, day: str) -> str:
        """Get description for month and day combination."""
        month_descriptions = {
            "Fravardin": "Under the protection of Fravardin, guardian of souls. You value protection and spiritual growth.",
            "Ardibehesht": "Blessed by Ardibehesht, keeper of fire and truth. You seek order and authenticity.",
            "Khordad": "Guided by Khordad, symbol of perfection. You strive for health and completeness.",
            "Tir": "Influenced by Tir, bringer of rain. You nurture growth and fertility in all things.",
            "Amurdad": "Protected by Amurdad, guardian of immortality. You value life and natural growth.",
            "Shahrevar": "Empowered by Shahrevar, master of metals. You possess strength and determination.",
            "Mehr": "Illuminated by Mehr, the sun. You radiate warmth, friendship, and love.",
            "Aban": "Cleansed by Aban, the waters. You seek purification and emotional depth.",
            "Azar": "Energized by Azar, the fire. You bring passion and transformation.",
            "Dey": "Inspired by Dey, the creator. You value law, justice, and creation.",
            "Bahman": "Wise under Bahman, the good mind. You seek wisdom and understanding.",
            "Esfand": "Grounded by Esfand, the earth. You embody humility and devotion.",
        }
        return month_descriptions.get(month, f"Under the influence of {month}.")

    def _get_traits(self, month: str) -> list[str]:
        """Get key traits for the month."""
        traits_map = {
            "Fravardin": ["Protective", "Spiritual", "Guardian", "Nurturing"],
            "Ardibehesht": ["Truthful", "Orderly", "Authentic", "Focused"],
            "Khordad": ["Perfectionist", "Health-conscious", "Complete", "Balanced"],
            "Tir": ["Nurturing", "Fertile", "Growth-oriented", "Caring"],
            "Amurdad": ["Life-loving", "Natural", "Immortal-spirited", "Vital"],
            "Shahrevar": ["Strong", "Determined", "Powerful", "Resilient"],
            "Mehr": ["Warm", "Friendly", "Loving", "Radiant"],
            "Aban": ["Pure", "Emotional", "Deep", "Cleansing"],
            "Azar": ["Passionate", "Energetic", "Transformative", "Fiery"],
            "Dey": ["Creative", "Just", "Lawful", "Inspired"],
            "Bahman": ["Wise", "Thoughtful", "Understanding", "Intelligent"],
            "Esfand": ["Humble", "Devoted", "Grounded", "Earthly"],
        }
        return traits_map.get(month, ["Balanced", "Spiritual"])

    def _get_deity_info(self, month: str) -> dict:
        """Get deity/guardian information."""
        deity_info = {
            "Fravardin": {
                "name": "Fravardin",
                "domain": "Protection of souls, spiritual growth",
                "symbol": "Guardian spirits",
            },
            "Ardibehesht": {
                "name": "Ardibehesht",
                "domain": "Fire, truth, cosmic order",
                "symbol": "Sacred fire",
            },
            "Khordad": {
                "name": "Khordad",
                "domain": "Perfection, health, completeness",
                "symbol": "Water of life",
            },
            "Tir": {
                "name": "Tir",
                "domain": "Rain, fertility, growth",
                "symbol": "Arrow, star",
            },
            "Amurdad": {
                "name": "Amurdad",
                "domain": "Immortality, plants, nature",
                "symbol": "Tree of life",
            },
            "Shahrevar": {
                "name": "Shahrevar",
                "domain": "Metals, minerals, power",
                "symbol": "Metal, strength",
            },
            "Mehr": {
                "name": "Mehr",
                "domain": "Sun, friendship, love",
                "symbol": "Sun",
            },
            "Aban": {
                "name": "Aban",
                "domain": "Water, purification",
                "symbol": "Water",
            },
            "Azar": {
                "name": "Azar",
                "domain": "Fire, energy, transformation",
                "symbol": "Fire",
            },
            "Dey": {
                "name": "Dey",
                "domain": "Creator, law, justice",
                "symbol": "Creator",
            },
            "Bahman": {
                "name": "Bahman",
                "domain": "Good mind, wisdom",
                "symbol": "Wisdom",
            },
            "Esfand": {
                "name": "Esfand",
                "domain": "Earth, humility, devotion",
                "symbol": "Earth",
            },
        }
        return deity_info.get(month, {"name": month, "domain": "Spiritual guidance", "symbol": "Unknown"})


def get_zoroastrian_horoscope_service() -> ZoroastrianHoroscopeService:
    return ZoroastrianHoroscopeService()

