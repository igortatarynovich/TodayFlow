"""Offline geocoder backed by a curated city dataset."""

from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from urllib.parse import quote
from urllib.request import Request, urlopen
from typing import Dict, Optional

CITY_DATA = [
    {"name": "New York", "local_name": "Нью-Йорк", "country": "United States", "latitude": 40.7128, "longitude": -74.006},
    {"name": "Los Angeles", "local_name": "Лос-Анджелес", "country": "United States", "latitude": 34.0522, "longitude": -118.2437},
    {"name": "Chicago", "local_name": "Чикаго", "country": "United States", "latitude": 41.8781, "longitude": -87.6298},
    {"name": "Miami", "local_name": "Майами", "country": "United States", "latitude": 25.7617, "longitude": -80.1918},
    {"name": "Toronto", "local_name": "Торонто", "country": "Canada", "latitude": 43.6532, "longitude": -79.3832},
    {"name": "Vancouver", "local_name": "Ванкувер", "country": "Canada", "latitude": 49.2827, "longitude": -123.1207},
    {"name": "Mexico City", "local_name": "Мехико", "country": "Mexico", "latitude": 19.4326, "longitude": -99.1332},
    {"name": "São Paulo", "local_name": "Сан-Паулу", "country": "Brazil", "latitude": -23.5505, "longitude": -46.6333},
    {"name": "Buenos Aires", "local_name": "Буэнос-Айрес", "country": "Argentina", "latitude": -34.6037, "longitude": -58.3816},
    {"name": "London", "local_name": "Лондон", "country": "United Kingdom", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "Paris", "local_name": "Париж", "country": "France", "latitude": 48.8566, "longitude": 2.3522},
    {"name": "Berlin", "local_name": "Берлин", "country": "Germany", "latitude": 52.52, "longitude": 13.405},
    {"name": "Moscow", "local_name": "Москва", "country": "Russia", "latitude": 55.7558, "longitude": 37.6176},
    {"name": "Saint Petersburg", "local_name": "Санкт-Петербург", "country": "Russia", "latitude": 59.9311, "longitude": 30.3609},
    {"name": "Minsk", "local_name": "Минск", "country": "Belarus", "latitude": 53.9045, "longitude": 27.5615},
    {"name": "Kyiv", "local_name": "Киев", "country": "Ukraine", "latitude": 50.4501, "longitude": 30.5234},
    {"name": "Riga", "local_name": "Рига", "country": "Latvia", "latitude": 56.9496, "longitude": 24.1052},
    {"name": "Vilnius", "local_name": "Вильнюс", "country": "Lithuania", "latitude": 54.6872, "longitude": 25.2797},
    {"name": "Tallinn", "local_name": "Таллин", "country": "Estonia", "latitude": 59.4370, "longitude": 24.7536},
    {"name": "Tbilisi", "local_name": "Тбилиси", "country": "Georgia", "latitude": 41.7151, "longitude": 44.8271},
    {"name": "Yerevan", "local_name": "Ереван", "country": "Armenia", "latitude": 40.1792, "longitude": 44.4991},
    {"name": "Astana", "local_name": "Астана", "country": "Kazakhstan", "latitude": 51.1605, "longitude": 71.4704},
    {"name": "Almaty", "local_name": "Алматы", "country": "Kazakhstan", "latitude": 43.2389, "longitude": 76.8897},
    {"name": "Madrid", "local_name": "Мадрид", "country": "Spain", "latitude": 40.4168, "longitude": -3.7038},
    {"name": "Barcelona", "local_name": "Барселона", "country": "Spain", "latitude": 41.3874, "longitude": 2.1686},
    {"name": "Rome", "local_name": "Рим", "country": "Italy", "latitude": 41.9028, "longitude": 12.4964},
    {"name": "Amsterdam", "local_name": "Амстердам", "country": "Netherlands", "latitude": 52.3667, "longitude": 4.8945},
    {"name": "Stockholm", "local_name": "Стокгольм", "country": "Sweden", "latitude": 59.3293, "longitude": 18.0686},
    {"name": "Oslo", "local_name": "Осло", "country": "Norway", "latitude": 59.9139, "longitude": 10.7522},
    {"name": "Copenhagen", "local_name": "Копенгаген", "country": "Denmark", "latitude": 55.6761, "longitude": 12.5683},
    {"name": "Helsinki", "local_name": "Хельсинки", "country": "Finland", "latitude": 60.1699, "longitude": 24.9384},
    {"name": "Warsaw", "local_name": "Варшава", "country": "Poland", "latitude": 52.2297, "longitude": 21.0122},
    {"name": "Prague", "local_name": "Прага", "country": "Czech Republic", "latitude": 50.0755, "longitude": 14.4378},
    {"name": "Vienna", "local_name": "Вена", "country": "Austria", "latitude": 48.2082, "longitude": 16.3738},
    {"name": "Zurich", "local_name": "Цюрих", "country": "Switzerland", "latitude": 47.3769, "longitude": 8.5417},
    {"name": "Lisbon", "local_name": "Лиссабон", "country": "Portugal", "latitude": 38.7223, "longitude": -9.1393},
    {"name": "Istanbul", "local_name": "Стамбул", "country": "Turkey", "latitude": 41.0082, "longitude": 28.9784},
    {"name": "Athens", "local_name": "Афины", "country": "Greece", "latitude": 37.9838, "longitude": 23.7275},
    {"name": "Dubai", "local_name": "Дубай", "country": "United Arab Emirates", "latitude": 25.2048, "longitude": 55.2708},
    {"name": "Tel Aviv", "local_name": "Тель-Авив", "country": "Israel", "latitude": 32.0853, "longitude": 34.7818},
    {"name": "Johannesburg", "local_name": "Йоханнесбург", "country": "South Africa", "latitude": -26.2041, "longitude": 28.0473},
    {"name": "Nairobi", "local_name": "Найроби", "country": "Kenya", "latitude": -1.2921, "longitude": 36.8219},
    {"name": "Lagos", "local_name": "Лагос", "country": "Nigeria", "latitude": 6.5244, "longitude": 3.3792},
    {"name": "Cairo", "local_name": "Каир", "country": "Egypt", "latitude": 30.0444, "longitude": 31.2357},
    {"name": "Mumbai", "local_name": "Мумбаи", "country": "India", "latitude": 19.076, "longitude": 72.8777},
    {"name": "Delhi", "local_name": "Дели", "country": "India", "latitude": 28.6139, "longitude": 77.209},
    {"name": "Bengaluru", "local_name": "Бангалор", "country": "India", "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Bangkok", "local_name": "Бангкок", "country": "Thailand", "latitude": 13.7563, "longitude": 100.5018},
    {"name": "Singapore", "local_name": "Сингапур", "country": "Singapore", "latitude": 1.3521, "longitude": 103.8198},
    {"name": "Hong Kong", "local_name": "Гонконг", "country": "China", "latitude": 22.3193, "longitude": 114.1694},
    {"name": "Shanghai", "local_name": "Шанхай", "country": "China", "latitude": 31.2304, "longitude": 121.4737},
    {"name": "Beijing", "local_name": "Пекин", "country": "China", "latitude": 39.9042, "longitude": 116.4074},
    {"name": "Seoul", "local_name": "Сеул", "country": "South Korea", "latitude": 37.5665, "longitude": 126.978},
    {"name": "Tokyo", "local_name": "Токио", "country": "Japan", "latitude": 35.6762, "longitude": 139.6503},
    {"name": "Kyoto", "local_name": "Киото", "country": "Japan", "latitude": 35.0116, "longitude": 135.7681},
    {"name": "Sydney", "local_name": "Сидней", "country": "Australia", "latitude": -33.8688, "longitude": 151.2093},
    {"name": "Melbourne", "local_name": "Мельбурн", "country": "Australia", "latitude": -37.8136, "longitude": 144.9631},
    {"name": "Brisbane", "local_name": "Брисбен", "country": "Australia", "latitude": -27.4698, "longitude": 153.0251},
    {"name": "Auckland", "local_name": "Окленд", "country": "New Zealand", "latitude": -36.8485, "longitude": 174.7633},
    {"name": "Wellington", "local_name": "Веллингтон", "country": "New Zealand", "latitude": -41.2866, "longitude": 174.7756},
]


CITY_ALIASES = {
    # Russian/Cyrillic aliases
    "москва": "Moscow",
    "санкт петербург": "Saint Petersburg",
    "санкт-петербург": "Saint Petersburg",
    "петербург": "Saint Petersburg",
    "минск": "Minsk",
    "киев": "Kyiv",
    "варшава": "Warsaw",
    "прага": "Prague",
    "вена": "Vienna",
    "берлин": "Berlin",
    "париж": "Paris",
    "лондон": "London",
    "рим": "Rome",
    "барселона": "Barcelona",
    "мадрид": "Madrid",
    "амстердам": "Amsterdam",
    "стамбул": "Istanbul",
    "дубай": "Dubai",
    "нью йорк": "New York",
    "лос анджелес": "Los Angeles",
    "чикаго": "Chicago",
    "майами": "Miami",
    "торонто": "Toronto",
    "тбилиси": "Tbilisi",
    "ереван": "Yerevan",
    "астана": "Astana",
    "алматы": "Almaty",
}


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "")
    normalized = normalized.replace("г.", " ").replace("город", " ")
    return " ".join(normalized.casefold().split())


@lru_cache(maxsize=1)
def _load_dataset() -> Dict[str, dict]:
    lookup: Dict[str, dict] = {}
    for record in CITY_DATA:
        city_key = _normalize(record["name"])
        combo_key = _normalize(f"{record['name']}, {record['country']}")
        lookup[city_key] = record
        lookup[combo_key] = record
        local_name = record.get("local_name")
        if local_name:
            lookup[_normalize(local_name)] = record
            lookup[_normalize(f"{local_name}, {record['country']}")] = record
    # Alias keys map to existing records by english city names.
    for alias, city_name in CITY_ALIASES.items():
        target = lookup.get(_normalize(city_name))
        if target:
            lookup[_normalize(alias)] = target
    return lookup


class Geocoder:
    """Simple deterministic geocoder for MVP needs."""

    def __init__(self):
        self.data = _load_dataset()

    def lookup(self, query: str | None) -> Optional[dict]:
        if not query:
            return None
        normalized = _normalize(query)
        record = self.data.get(normalized)

        if record is None and "," in normalized:
            city_only = normalized.split(",")[0].strip()
            record = self.data.get(city_only)

        if record:
            return self._serialize_record(record)
        online = _lookup_online(query.strip())
        if online:
            return online
        return None

    def suggest(self, query: str | None, limit: int = 8) -> list[dict]:
        if not query:
            return []
        normalized = _normalize(query)
        if len(normalized) < 2:
            return []

        aliases_by_city: Dict[str, list[str]] = {}
        for alias, city_name in CITY_ALIASES.items():
            aliases_by_city.setdefault(city_name, []).append(alias)

        scored: list[tuple[int, str, dict]] = []
        seen: set[str] = set()
        for record in CITY_DATA:
            city_name = record["name"]
            local_name = str(record.get("local_name") or "")
            country = record["country"]
            key = f"{city_name}|{country}"
            aliases = aliases_by_city.get(city_name, [])
            tokens = [
                city_name,
                local_name,
                country,
                f"{city_name}, {country}",
                f"{local_name}, {country}" if local_name else "",
                *aliases,
            ]
            normalized_tokens = [_normalize(token) for token in tokens if token]
            if not any(normalized in token for token in normalized_tokens):
                continue

            score = 0
            for token in normalized_tokens:
                if token == normalized:
                    score = max(score, 120)
                elif token.startswith(normalized):
                    score = max(score, 100)
                elif f" {normalized}" in token:
                    score = max(score, 75)
                elif normalized in token:
                    score = max(score, 55)
            if city_name in aliases_by_city and any(alias.startswith(normalized) for alias in aliases_by_city[city_name]):
                score += 10
            if key in seen:
                continue
            seen.add(key)
            scored.append((score, local_name or city_name, record))

        scored.sort(key=lambda item: (-item[0], item[1]))
        return [self._serialize_record(record) for _, _, record in scored[:limit]]

    def _serialize_record(self, record: dict) -> dict:
        local_name = record.get("local_name")
        display_name = f"{local_name or record['name']} / {record['name']}, {record['country']}"
        return {
            "name": record["name"],
            "local_name": local_name,
            "display_name": display_name,
            "country": record["country"],
            "latitude": record["latitude"],
            "longitude": record["longitude"],
        }


@lru_cache(maxsize=512)
def _lookup_online(query: str) -> Optional[dict]:
    if not query:
        return None
    # Public fallback geocoding; used only when offline dataset misses.
    url = (
        "https://nominatim.openstreetmap.org/search"
        f"?format=jsonv2&limit=1&q={quote(query)}"
    )
    request = Request(
        url,
        headers={
            "User-Agent": "TodayFlow/1.0 (support@todayflow.app)",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=1.8) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, list) or not payload:
                return None
            first = payload[0]
            lat = first.get("lat")
            lon = first.get("lon")
            if lat is None or lon is None:
                return None
            display_name = str(first.get("display_name") or query)
            city = display_name.split(",")[0].strip() or query
            country = display_name.split(",")[-1].strip() if "," in display_name else "Unknown"
            return {
                "name": city,
                "country": country,
                "latitude": float(lat),
                "longitude": float(lon),
            }
    except Exception:
        return None
