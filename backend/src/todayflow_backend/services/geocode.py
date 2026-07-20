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


# Major RU / CIS cities frequently missing from the curated list above.
CITY_DATA.extend(
    [
        {"name": "Novosibirsk", "local_name": "Новосибирск", "country": "Russia", "latitude": 55.0084, "longitude": 82.9357},
        {"name": "Yekaterinburg", "local_name": "Екатеринбург", "country": "Russia", "latitude": 56.8389, "longitude": 60.6057},
        {"name": "Kazan", "local_name": "Казань", "country": "Russia", "latitude": 55.7961, "longitude": 49.1064},
        {"name": "Nizhny Novgorod", "local_name": "Нижний Новгород", "country": "Russia", "latitude": 56.2965, "longitude": 43.9361},
        {"name": "Chelyabinsk", "local_name": "Челябинск", "country": "Russia", "latitude": 55.1644, "longitude": 61.4368},
        {"name": "Samara", "local_name": "Самара", "country": "Russia", "latitude": 53.1959, "longitude": 50.1002},
        {"name": "Omsk", "local_name": "Омск", "country": "Russia", "latitude": 54.9885, "longitude": 73.3242},
        {"name": "Rostov-on-Don", "local_name": "Ростов-на-Дону", "country": "Russia", "latitude": 47.2357, "longitude": 39.7015},
        {"name": "Ufa", "local_name": "Уфа", "country": "Russia", "latitude": 54.7388, "longitude": 55.9721},
        {"name": "Krasnoyarsk", "local_name": "Красноярск", "country": "Russia", "latitude": 56.0153, "longitude": 92.8932},
        {"name": "Voronezh", "local_name": "Воронеж", "country": "Russia", "latitude": 51.6720, "longitude": 39.1843},
        {"name": "Perm", "local_name": "Пермь", "country": "Russia", "latitude": 58.0105, "longitude": 56.2502},
        {"name": "Volgograd", "local_name": "Волгоград", "country": "Russia", "latitude": 48.7080, "longitude": 44.5133},
        {"name": "Krasnodar", "local_name": "Краснодар", "country": "Russia", "latitude": 45.0355, "longitude": 38.9753},
        {"name": "Saratov", "local_name": "Саратов", "country": "Russia", "latitude": 51.5336, "longitude": 46.0343},
        {"name": "Tyumen", "local_name": "Тюмень", "country": "Russia", "latitude": 57.1522, "longitude": 65.5272},
        {"name": "Tolyatti", "local_name": "Тольятти", "country": "Russia", "latitude": 53.5303, "longitude": 49.3461},
        {"name": "Izhevsk", "local_name": "Ижевск", "country": "Russia", "latitude": 56.8527, "longitude": 53.2115},
        {"name": "Barnaul", "local_name": "Барнаул", "country": "Russia", "latitude": 53.3548, "longitude": 83.7698},
        {"name": "Irkutsk", "local_name": "Иркутск", "country": "Russia", "latitude": 52.2869, "longitude": 104.3050},
        {"name": "Khabarovsk", "local_name": "Хабаровск", "country": "Russia", "latitude": 48.4827, "longitude": 135.0838},
        {"name": "Vladivostok", "local_name": "Владивосток", "country": "Russia", "latitude": 43.1155, "longitude": 131.8855},
        {"name": "Yaroslavl", "local_name": "Ярославль", "country": "Russia", "latitude": 57.6261, "longitude": 39.8845},
        {"name": "Tomsk", "local_name": "Томск", "country": "Russia", "latitude": 56.4846, "longitude": 84.9476},
        {"name": "Kemerovo", "local_name": "Кемерово", "country": "Russia", "latitude": 55.3549, "longitude": 86.0873},
        {"name": "Orenburg", "local_name": "Оренбург", "country": "Russia", "latitude": 51.7682, "longitude": 55.0970},
        {"name": "Novokuznetsk", "local_name": "Новокузнецк", "country": "Russia", "latitude": 53.7596, "longitude": 87.1216},
        {"name": "Ryazan", "local_name": "Рязань", "country": "Russia", "latitude": 54.6292, "longitude": 39.7363},
        {"name": "Astrakhan", "local_name": "Астрахань", "country": "Russia", "latitude": 46.3497, "longitude": 48.0408},
        {"name": "Penza", "local_name": "Пенза", "country": "Russia", "latitude": 53.1950, "longitude": 45.0183},
        {"name": "Lipetsk", "local_name": "Липецк", "country": "Russia", "latitude": 52.6088, "longitude": 39.5992},
        {"name": "Kirov", "local_name": "Киров", "country": "Russia", "latitude": 58.6035, "longitude": 49.6680},
        {"name": "Cheboksary", "local_name": "Чебоксары", "country": "Russia", "latitude": 56.1439, "longitude": 47.2489},
        {"name": "Kaliningrad", "local_name": "Калининград", "country": "Russia", "latitude": 54.7104, "longitude": 20.4522},
        {"name": "Tula", "local_name": "Тула", "country": "Russia", "latitude": 54.1961, "longitude": 37.6182},
        {"name": "Kursk", "local_name": "Курск", "country": "Russia", "latitude": 51.7373, "longitude": 36.1873},
        {"name": "Stavropol", "local_name": "Ставрополь", "country": "Russia", "latitude": 45.0428, "longitude": 41.9734},
        {"name": "Ulyanovsk", "local_name": "Ульяновск", "country": "Russia", "latitude": 54.3142, "longitude": 48.4031},
        {"name": "Ivanovo", "local_name": "Иваново", "country": "Russia", "latitude": 56.9972, "longitude": 40.9714},
        {"name": "Bryansk", "local_name": "Брянск", "country": "Russia", "latitude": 53.2521, "longitude": 34.3717},
        {"name": "Sochi", "local_name": "Сочи", "country": "Russia", "latitude": 43.6028, "longitude": 39.7342},
        {"name": "Sevastopol", "local_name": "Севастополь", "country": "Russia", "latitude": 44.6166, "longitude": 33.5254},
        {"name": "Simferopol", "local_name": "Симферополь", "country": "Russia", "latitude": 44.9521, "longitude": 34.1024},
        {"name": "Kharkiv", "local_name": "Харьков", "country": "Ukraine", "latitude": 49.9935, "longitude": 36.2304},
        {"name": "Odessa", "local_name": "Одесса", "country": "Ukraine", "latitude": 46.4825, "longitude": 30.7233},
        {"name": "Dnipro", "local_name": "Днепр", "country": "Ukraine", "latitude": 48.4647, "longitude": 35.0462},
        {"name": "Lviv", "local_name": "Львов", "country": "Ukraine", "latitude": 49.8397, "longitude": 24.0297},
        {"name": "Gomel", "local_name": "Гомель", "country": "Belarus", "latitude": 52.4412, "longitude": 30.9878},
        {"name": "Brest", "local_name": "Брест", "country": "Belarus", "latitude": 52.0976, "longitude": 23.7341},
    ]
)

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
    "новосибирск": "Novosibirsk",
    "екатеринбург": "Yekaterinburg",
    "казань": "Kazan",
    "нижний новгород": "Nizhny Novgorod",
    "челябинск": "Chelyabinsk",
    "самара": "Samara",
    "омск": "Omsk",
    "ростов на дону": "Rostov-on-Don",
    "ростов-на-дону": "Rostov-on-Don",
    "уфа": "Ufa",
    "красноярск": "Krasnoyarsk",
    "воронеж": "Voronezh",
    "пермь": "Perm",
    "волгоград": "Volgograd",
    "краснодар": "Krasnodar",
    "сочи": "Sochi",
    "харьков": "Kharkiv",
    "одесса": "Odessa",
    "львов": "Lviv",
}


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "")
    # Strip bilingual "Город / City, Country" display labels saved by older clients.
    if " / " in normalized:
        normalized = normalized.split(" / ", 1)[0]
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
        offline = [self._serialize_record(record) for _, _, record in scored[:limit]]
        if len(offline) >= min(3, limit):
            return offline
        online = _suggest_online(query.strip(), limit=limit)
        if not online:
            return offline
        # Prefer offline hits first, then fill from Nominatim without duplicates.
        merged: list[dict] = list(offline)
        seen_keys = {
            f"{_normalize(str(item.get('name') or ''))}|{_normalize(str(item.get('country') or ''))}"
            for item in merged
        }
        for item in online:
            key = f"{_normalize(str(item.get('name') or ''))}|{_normalize(str(item.get('country') or ''))}"
            if key in seen_keys:
                continue
            seen_keys.add(key)
            merged.append(item)
            if len(merged) >= limit:
                break
        return merged

    def _serialize_record(self, record: dict) -> dict:
        local_name = record.get("local_name")
        # Prefer a clean single-language label for persistence; keep bilingual only as display hint.
        display_name = f"{local_name or record['name']}, {record['country']}"
        return {
            "name": record["name"],
            "local_name": local_name,
            "display_name": display_name,
            "country": record["country"],
            "latitude": record["latitude"],
            "longitude": record["longitude"],
        }


def _map_nominatim_hit(first: dict, *, query: str) -> Optional[dict]:
    lat = first.get("lat")
    lon = first.get("lon")
    if lat is None or lon is None:
        return None
    display_name = str(first.get("display_name") or query)
    parts = [p.strip() for p in display_name.split(",") if p.strip()]
    city = parts[0] if parts else query
    country = parts[-1] if len(parts) > 1 else "Unknown"
    return {
        "name": city,
        "local_name": city,
        "display_name": f"{city}, {country}",
        "country": country,
        "latitude": float(lat),
        "longitude": float(lon),
    }


@lru_cache(maxsize=512)
def _lookup_online(query: str) -> Optional[dict]:
    if not query:
        return None
    hits = _suggest_online(query, limit=1)
    return hits[0] if hits else None


@lru_cache(maxsize=256)
def _suggest_online(query: str, limit: int = 8) -> tuple:
    """Nominatim multi-result fallback for cities outside the offline set."""
    if not query:
        return ()
    url = (
        "https://nominatim.openstreetmap.org/search"
        f"?format=jsonv2&addressdetails=1&limit={max(1, min(int(limit), 12))}&q={quote(query)}"
    )
    request = Request(
        url,
        headers={
            "User-Agent": "TodayFlow/1.0 (support@todayflow.app)",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=2.4) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, list) or not payload:
                return ()
            out: list[dict] = []
            for row in payload:
                if not isinstance(row, dict):
                    continue
                mapped = _map_nominatim_hit(row, query=query)
                if mapped:
                    out.append(mapped)
            return tuple(out)
    except Exception:
        return ()
