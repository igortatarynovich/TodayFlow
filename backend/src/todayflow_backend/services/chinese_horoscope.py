"""Chinese (Eastern) Zodiac horoscope service."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

CHINESE_ZODIAC_ANIMALS = [
    "Rat",      # 鼠 - 1924, 1936, 1948, 1960, 1972, 1984, 1996, 2008, 2020, 2032
    "Ox",       # 牛 - 1925, 1937, 1949, 1961, 1973, 1985, 1997, 2009, 2021, 2033
    "Tiger",    # 虎 - 1926, 1938, 1950, 1962, 1974, 1986, 1998, 2010, 2022, 2034
    "Rabbit",   # 兔 - 1927, 1939, 1951, 1963, 1975, 1987, 1999, 2011, 2023, 2035
    "Dragon",   # 龙 - 1928, 1940, 1952, 1964, 1976, 1988, 2000, 2012, 2024, 2036
    "Snake",    # 蛇 - 1929, 1941, 1953, 1965, 1977, 1989, 2001, 2013, 2025, 2037
    "Horse",    # 马 - 1930, 1942, 1954, 1966, 1978, 1990, 2002, 2014, 2026, 2038
    "Goat",     # 羊 - 1931, 1943, 1955, 1967, 1979, 1991, 2003, 2015, 2027, 2039
    "Monkey",   # 猴 - 1932, 1944, 1956, 1968, 1980, 1992, 2004, 2016, 2028, 2040
    "Rooster",  # 鸡 - 1933, 1945, 1957, 1969, 1981, 1993, 2005, 2017, 2029, 2041
    "Dog",      # 狗 - 1934, 1946, 1958, 1970, 1982, 1994, 2006, 2018, 2030, 2042
    "Pig",      # 猪 - 1935, 1947, 1959, 1971, 1983, 1995, 2007, 2019, 2031, 2043
]

CHINESE_ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]

# Chinese New Year dates (approximate, varies by year)
CHINESE_NEW_YEAR_DATES = {
    2020: date(2020, 1, 25),
    2021: date(2021, 2, 12),
    2022: date(2022, 2, 1),
    2023: date(2023, 1, 22),
    2024: date(2024, 2, 10),
    2025: date(2025, 1, 29),
    2026: date(2026, 2, 17),
    2027: date(2027, 2, 6),
    2028: date(2028, 1, 26),
    2029: date(2029, 2, 13),
    2030: date(2030, 2, 3),
}


class ChineseHoroscopeService:
    """Service for calculating Chinese Zodiac horoscope."""

    def calculate(self, birth_date: date) -> dict:
        """Calculate Chinese Zodiac sign and element for birth date."""
        # Determine the Chinese calendar year
        chinese_year = self._get_chinese_year(birth_date)
        
        # Calculate animal sign (12-year cycle)
        animal_index = (chinese_year - 4) % 12
        animal = CHINESE_ZODIAC_ANIMALS[animal_index]
        
        # Calculate element (10-year cycle, but actually 2-year cycle)
        element_index = ((chinese_year - 4) % 10) // 2
        element = CHINESE_ELEMENTS[element_index]
        
        return {
            "animal": animal,
            "element": element,
            "chinese_year": chinese_year,
            "description": self._get_description(animal, element),
            "traits": self._get_traits(animal, element),
            "compatibility": self._get_compatibility(animal_index),
        }

    def _get_chinese_year(self, birth_date: date) -> int:
        """Get Chinese calendar year for a given date."""
        year = birth_date.year
        
        # Approximate Chinese New Year date for the year
        # If birth date is before Chinese New Year, use previous year
        if year in CHINESE_NEW_YEAR_DATES:
            new_year_date = CHINESE_NEW_YEAR_DATES[year]
            if birth_date < new_year_date:
                return year - 1
        
        # For years not in our table, approximate
        # Chinese New Year is usually between Jan 21 and Feb 20
        if birth_date.month == 1 or (birth_date.month == 2 and birth_date.day < 20):
            # Check if we need to go back a year
            if year in CHINESE_NEW_YEAR_DATES:
                new_year_date = CHINESE_NEW_YEAR_DATES[year]
                if birth_date < new_year_date:
                    return year - 1
        
        return year

    def _get_description(self, animal: str, element: str) -> str:
        """Get description for animal and element combination."""
        descriptions = {
            ("Rat", "Wood"): "Innovative and resourceful, Wood Rat combines creativity with practicality.",
            ("Rat", "Fire"): "Energetic and ambitious, Fire Rat is driven by passion and determination.",
            ("Rat", "Earth"): "Stable and reliable, Earth Rat values security and tradition.",
            ("Rat", "Metal"): "Sharp and analytical, Metal Rat excels in strategic thinking.",
            ("Rat", "Water"): "Adaptive and intuitive, Water Rat flows with change.",
            ("Ox", "Wood"): "Patient and methodical, Wood Ox builds lasting foundations.",
            ("Ox", "Fire"): "Strong-willed and persistent, Fire Ox never gives up.",
            ("Ox", "Earth"): "Grounded and dependable, Earth Ox is the pillar of stability.",
            ("Ox", "Metal"): "Precise and disciplined, Metal Ox values order and structure.",
            ("Ox", "Water"): "Calm and steady, Water Ox moves with deliberate purpose.",
            ("Tiger", "Wood"): "Bold and adventurous, Wood Tiger seeks new horizons.",
            ("Tiger", "Fire"): "Passionate and dynamic, Fire Tiger leads with intensity.",
            ("Tiger", "Earth"): "Balanced and practical, Earth Tiger combines courage with wisdom.",
            ("Tiger", "Metal"): "Fierce and determined, Metal Tiger fights for what matters.",
            ("Tiger", "Water"): "Adaptive and intuitive, Water Tiger flows with opportunities.",
            ("Rabbit", "Wood"): "Gentle and creative, Wood Rabbit brings beauty to life.",
            ("Rabbit", "Fire"): "Warm and sociable, Fire Rabbit lights up any room.",
            ("Rabbit", "Earth"): "Stable and nurturing, Earth Rabbit creates safe spaces.",
            ("Rabbit", "Metal"): "Refined and elegant, Metal Rabbit values quality and precision.",
            ("Rabbit", "Water"): "Intuitive and empathetic, Water Rabbit understands emotions deeply.",
            ("Dragon", "Wood"): "Visionary and expansive, Wood Dragon brings ideas to life.",
            ("Dragon", "Fire"): "Powerful and charismatic, Fire Dragon commands attention.",
            ("Dragon", "Earth"): "Grounded and ambitious, Earth Dragon builds empires.",
            ("Dragon", "Metal"): "Strong and determined, Metal Dragon achieves greatness.",
            ("Dragon", "Water"): "Adaptive and wise, Water Dragon flows with power.",
            ("Snake", "Wood"): "Wise and insightful, Wood Snake sees beneath the surface.",
            ("Snake", "Fire"): "Passionate and magnetic, Fire Snake draws others in.",
            ("Snake", "Earth"): "Practical and strategic, Earth Snake plans carefully.",
            ("Snake", "Metal"): "Sharp and focused, Metal Snake cuts through complexity.",
            ("Snake", "Water"): "Intuitive and mysterious, Water Snake understands hidden truths.",
            ("Horse", "Wood"): "Free-spirited and energetic, Wood Horse seeks adventure.",
            ("Horse", "Fire"): "Passionate and independent, Fire Horse runs wild.",
            ("Horse", "Earth"): "Stable and reliable, Earth Horse provides steady support.",
            ("Horse", "Metal"): "Strong and determined, Metal Horse never stops.",
            ("Horse", "Water"): "Adaptive and flowing, Water Horse moves with grace.",
            ("Goat", "Wood"): "Creative and gentle, Wood Goat brings artistic beauty.",
            ("Goat", "Fire"): "Warm and expressive, Fire Goat shares joy freely.",
            ("Goat", "Earth"): "Nurturing and stable, Earth Goat creates harmony.",
            ("Goat", "Metal"): "Refined and elegant, Metal Goat values quality.",
            ("Goat", "Water"): "Intuitive and empathetic, Water Goat understands feelings.",
            ("Monkey", "Wood"): "Clever and inventive, Wood Monkey creates solutions.",
            ("Monkey", "Fire"): "Energetic and playful, Fire Monkey brings excitement.",
            ("Monkey", "Earth"): "Practical and resourceful, Earth Monkey gets things done.",
            ("Monkey", "Metal"): "Sharp and analytical, Metal Monkey solves problems.",
            ("Monkey", "Water"): "Adaptive and quick, Water Monkey flows with change.",
            ("Rooster", "Wood"): "Organized and creative, Wood Rooster brings order.",
            ("Rooster", "Fire"): "Bold and confident, Fire Rooster leads with style.",
            ("Rooster", "Earth"): "Reliable and practical, Earth Rooster keeps promises.",
            ("Rooster", "Metal"): "Precise and disciplined, Metal Rooster values excellence.",
            ("Rooster", "Water"): "Adaptive and observant, Water Rooster notices details.",
            ("Dog", "Wood"): "Loyal and protective, Wood Dog stands by friends.",
            ("Dog", "Fire"): "Passionate and devoted, Fire Dog fights for justice.",
            ("Dog", "Earth"): "Stable and reliable, Earth Dog is a true friend.",
            ("Dog", "Metal"): "Strong and determined, Metal Dog never gives up.",
            ("Dog", "Water"): "Intuitive and caring, Water Dog understands others.",
            ("Pig", "Wood"): "Generous and creative, Wood Pig shares abundance.",
            ("Pig", "Fire"): "Warm and sociable, Fire Pig brings people together.",
            ("Pig", "Earth"): "Stable and nurturing, Earth Pig provides comfort.",
            ("Pig", "Metal"): "Determined and focused, Metal Pig achieves goals.",
            ("Pig", "Water"): "Intuitive and flowing, Water Pig adapts easily.",
        }
        return descriptions.get((animal, element), f"{element} {animal} combines the qualities of both.")

    def _get_traits(self, animal: str, element: str) -> list[str]:
        """Get key traits for animal and element."""
        base_traits = {
            "Rat": ["Resourceful", "Quick-witted", "Charming", "Persistent"],
            "Ox": ["Diligent", "Dependable", "Strong", "Determined"],
            "Tiger": ["Brave", "Confident", "Competitive", "Independent"],
            "Rabbit": ["Gentle", "Artistic", "Peaceful", "Intuitive"],
            "Dragon": ["Ambitious", "Charismatic", "Confident", "Intelligent"],
            "Snake": ["Wise", "Mysterious", "Intuitive", "Elegant"],
            "Horse": ["Energetic", "Independent", "Adventurous", "Free-spirited"],
            "Goat": ["Creative", "Gentle", "Peaceful", "Artistic"],
            "Monkey": ["Clever", "Witty", "Curious", "Versatile"],
            "Rooster": ["Observant", "Hardworking", "Confident", "Precise"],
            "Dog": ["Loyal", "Honest", "Reliable", "Protective"],
            "Pig": ["Generous", "Diligent", "Compassionate", "Optimistic"],
        }
        
        element_modifiers = {
            "Wood": ["Creative", "Flexible", "Growth-oriented"],
            "Fire": ["Passionate", "Energetic", "Dynamic"],
            "Earth": ["Stable", "Practical", "Grounded"],
            "Metal": ["Precise", "Disciplined", "Strong"],
            "Water": ["Adaptive", "Intuitive", "Flowing"],
        }
        
        traits = base_traits.get(animal, []) + element_modifiers.get(element, [])
        return list(set(traits))[:6]  # Return unique traits, max 6

    def _get_compatibility(self, animal_index: int) -> list[str]:
        """Get compatible animals (4-year cycle compatibility)."""
        # Best matches are typically 4 years apart (trine)
        compatible_indices = [
            (animal_index + 4) % 12,
            (animal_index - 4) % 12,
        ]
        compatible = [CHINESE_ZODIAC_ANIMALS[i] for i in compatible_indices]
        return compatible


def get_chinese_horoscope_service() -> ChineseHoroscopeService:
    return ChineseHoroscopeService()

