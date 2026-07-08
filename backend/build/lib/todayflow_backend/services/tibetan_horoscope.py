"""Tibetan horoscope service."""

from __future__ import annotations

from datetime import date
from typing import Optional

# Tibetan calendar elements (5 elements)
TIBETAN_ELEMENTS = ["Wood", "Fire", "Earth", "Iron", "Water"]

# Tibetan animals (12-year cycle, similar to Chinese but with different names)
TIBETAN_ANIMALS = [
    "Mouse",    # 鼠
    "Ox",       # 牛
    "Tiger",    # 虎
    "Rabbit",   # 兔
    "Dragon",   # 龙
    "Snake",    # 蛇
    "Horse",    # 马
    "Sheep",    # 羊
    "Monkey",   # 猴
    "Bird",     # 鸡
    "Dog",      # 狗
    "Pig",      # 猪
]

# Tibetan Mewa (9 magic squares)
TIBETAN_MEWA = [
    "White",      # 1 - White
    "Black",      # 2 - Black
    "Blue",       # 3 - Blue
    "Green",      # 4 - Green
    "Yellow",     # 5 - Yellow
    "White",      # 6 - White
    "Red",        # 7 - Red
    "White",      # 8 - White
    "Red",        # 9 - Red
]


class TibetanHoroscopeService:
    """Service for calculating Tibetan horoscope."""

    def calculate(self, birth_date: date) -> dict:
        """Calculate Tibetan horoscope for birth date."""
        year = birth_date.year
        
        # Calculate animal (12-year cycle, starting from 1924)
        animal_index = (year - 4) % 12
        animal = TIBETAN_ANIMALS[animal_index]
        
        # Calculate element (10-year cycle, but actually 2-year cycle)
        element_index = ((year - 4) % 10) // 2
        element = TIBETAN_ELEMENTS[element_index]
        
        # Calculate Mewa (9-year cycle)
        mewa_index = ((year - 4) % 9)
        mewa = TIBETAN_MEWA[mewa_index]
        
        return {
            "animal": animal,
            "element": element,
            "mewa": mewa,
            "year": year,
            "description": self._get_description(animal, element, mewa),
            "traits": self._get_traits(animal, element),
            "mewa_meaning": self._get_mewa_meaning(mewa),
        }

    def _get_description(self, animal: str, element: str, mewa: str) -> str:
        """Get description for animal, element, and mewa combination."""
        base_description = f"{element} {animal}"
        
        descriptions = {
            ("Mouse", "Wood"): "Resourceful and creative, Wood Mouse finds innovative solutions.",
            ("Mouse", "Fire"): "Energetic and ambitious, Fire Mouse pursues goals with passion.",
            ("Mouse", "Earth"): "Practical and stable, Earth Mouse builds secure foundations.",
            ("Mouse", "Iron"): "Sharp and analytical, Iron Mouse excels in strategic thinking.",
            ("Mouse", "Water"): "Adaptive and intuitive, Water Mouse flows with change.",
            ("Ox", "Wood"): "Patient and methodical, Wood Ox creates lasting structures.",
            ("Ox", "Fire"): "Strong-willed and persistent, Fire Ox never gives up.",
            ("Ox", "Earth"): "Grounded and dependable, Earth Ox provides stability.",
            ("Ox", "Iron"): "Precise and disciplined, Iron Ox values order.",
            ("Ox", "Water"): "Calm and steady, Water Ox moves deliberately.",
            ("Tiger", "Wood"): "Bold and adventurous, Wood Tiger seeks new horizons.",
            ("Tiger", "Fire"): "Passionate and dynamic, Fire Tiger leads with intensity.",
            ("Tiger", "Earth"): "Balanced and practical, Earth Tiger combines courage with wisdom.",
            ("Tiger", "Iron"): "Fierce and determined, Iron Tiger fights for justice.",
            ("Tiger", "Water"): "Adaptive and intuitive, Water Tiger flows with opportunities.",
            ("Rabbit", "Wood"): "Gentle and creative, Wood Rabbit brings beauty to life.",
            ("Rabbit", "Fire"): "Warm and sociable, Fire Rabbit lights up gatherings.",
            ("Rabbit", "Earth"): "Stable and nurturing, Earth Rabbit creates safe spaces.",
            ("Rabbit", "Iron"): "Refined and elegant, Iron Rabbit values quality.",
            ("Rabbit", "Water"): "Intuitive and empathetic, Water Rabbit understands emotions.",
            ("Dragon", "Wood"): "Visionary and expansive, Wood Dragon brings ideas to life.",
            ("Dragon", "Fire"): "Powerful and charismatic, Fire Dragon commands attention.",
            ("Dragon", "Earth"): "Grounded and ambitious, Earth Dragon builds empires.",
            ("Dragon", "Iron"): "Strong and determined, Iron Dragon achieves greatness.",
            ("Dragon", "Water"): "Adaptive and wise, Water Dragon flows with power.",
            ("Snake", "Wood"): "Wise and insightful, Wood Snake sees beneath the surface.",
            ("Snake", "Fire"): "Passionate and magnetic, Fire Snake draws others in.",
            ("Snake", "Earth"): "Practical and strategic, Earth Snake plans carefully.",
            ("Snake", "Iron"): "Sharp and focused, Iron Snake cuts through complexity.",
            ("Snake", "Water"): "Intuitive and mysterious, Water Snake understands hidden truths.",
            ("Horse", "Wood"): "Free-spirited and energetic, Wood Horse seeks adventure.",
            ("Horse", "Fire"): "Passionate and independent, Fire Horse runs wild.",
            ("Horse", "Earth"): "Stable and reliable, Earth Horse provides support.",
            ("Horse", "Iron"): "Strong and determined, Iron Horse never stops.",
            ("Horse", "Water"): "Adaptive and flowing, Water Horse moves with grace.",
            ("Sheep", "Wood"): "Creative and gentle, Wood Sheep brings artistic beauty.",
            ("Sheep", "Fire"): "Warm and expressive, Fire Sheep shares joy freely.",
            ("Sheep", "Earth"): "Nurturing and stable, Earth Sheep creates harmony.",
            ("Sheep", "Iron"): "Refined and elegant, Iron Sheep values quality.",
            ("Sheep", "Water"): "Intuitive and empathetic, Water Sheep understands feelings.",
            ("Monkey", "Wood"): "Clever and inventive, Wood Monkey creates solutions.",
            ("Monkey", "Fire"): "Energetic and playful, Fire Monkey brings excitement.",
            ("Monkey", "Earth"): "Practical and resourceful, Earth Monkey gets things done.",
            ("Monkey", "Iron"): "Sharp and analytical, Iron Monkey solves problems.",
            ("Monkey", "Water"): "Adaptive and quick, Water Monkey flows with change.",
            ("Bird", "Wood"): "Organized and creative, Wood Bird brings order.",
            ("Bird", "Fire"): "Bold and confident, Fire Bird leads with style.",
            ("Bird", "Earth"): "Reliable and practical, Earth Bird keeps promises.",
            ("Bird", "Iron"): "Precise and disciplined, Iron Bird values excellence.",
            ("Bird", "Water"): "Adaptive and observant, Water Bird notices details.",
            ("Dog", "Wood"): "Loyal and protective, Wood Dog stands by friends.",
            ("Dog", "Fire"): "Passionate and devoted, Fire Dog fights for justice.",
            ("Dog", "Earth"): "Stable and reliable, Earth Dog is a true friend.",
            ("Dog", "Iron"): "Strong and determined, Iron Dog never gives up.",
            ("Dog", "Water"): "Intuitive and caring, Water Dog understands others.",
            ("Pig", "Wood"): "Generous and creative, Wood Pig shares abundance.",
            ("Pig", "Fire"): "Warm and sociable, Fire Pig brings people together.",
            ("Pig", "Earth"): "Stable and nurturing, Earth Pig provides comfort.",
            ("Pig", "Iron"): "Determined and focused, Iron Pig achieves goals.",
            ("Pig", "Water"): "Intuitive and flowing, Water Pig adapts easily.",
        }
        
        animal_element_desc = descriptions.get((animal, element), f"{element} {animal} combines unique qualities.")
        
        mewa_desc = self._get_mewa_meaning(mewa)
        
        return f"{animal_element_desc} Under the influence of {mewa} Mewa, {mewa_desc}"

    def _get_traits(self, animal: str, element: str) -> list[str]:
        """Get key traits for animal and element."""
        base_traits = {
            "Mouse": ["Resourceful", "Quick-witted", "Charming", "Persistent"],
            "Ox": ["Diligent", "Dependable", "Strong", "Determined"],
            "Tiger": ["Brave", "Confident", "Competitive", "Independent"],
            "Rabbit": ["Gentle", "Artistic", "Peaceful", "Intuitive"],
            "Dragon": ["Ambitious", "Charismatic", "Confident", "Intelligent"],
            "Snake": ["Wise", "Mysterious", "Intuitive", "Elegant"],
            "Horse": ["Energetic", "Independent", "Adventurous", "Free-spirited"],
            "Sheep": ["Creative", "Gentle", "Peaceful", "Artistic"],
            "Monkey": ["Clever", "Witty", "Curious", "Versatile"],
            "Bird": ["Observant", "Hardworking", "Confident", "Precise"],
            "Dog": ["Loyal", "Honest", "Reliable", "Protective"],
            "Pig": ["Generous", "Diligent", "Compassionate", "Optimistic"],
        }
        
        element_modifiers = {
            "Wood": ["Creative", "Flexible", "Growth-oriented"],
            "Fire": ["Passionate", "Energetic", "Dynamic"],
            "Earth": ["Stable", "Practical", "Grounded"],
            "Iron": ["Precise", "Disciplined", "Strong"],
            "Water": ["Adaptive", "Intuitive", "Flowing"],
        }
        
        traits = base_traits.get(animal, []) + element_modifiers.get(element, [])
        return list(set(traits))[:6]

    def _get_mewa_meaning(self, mewa: str) -> str:
        """Get meaning for Mewa color."""
        meanings = {
            "White": "bringing clarity, purity, and new beginnings",
            "Black": "representing depth, mystery, and transformation",
            "Blue": "symbolizing wisdom, communication, and healing",
            "Green": "indicating growth, harmony, and balance",
            "Yellow": "representing earth, stability, and grounding",
            "Red": "symbolizing energy, passion, and action",
        }
        return meanings.get(mewa, "influencing your spiritual path")


def get_tibetan_horoscope_service() -> TibetanHoroscopeService:
    return TibetanHoroscopeService()

