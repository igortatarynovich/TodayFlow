"""Synthesis runner — no projector fallback on fail."""

from __future__ import annotations

from todayflow_backend.services import life_spheres_synthesis_run_v0 as syn
from todayflow_backend.services.life_spheres_synthesis_run_v0 import SPHERES_SOURCE


def _foundations() -> dict:
    return {
        "locale": "ru",
        "identity": {
            "identity_core": "Держит смысл через тёплый контакт и ясную заботу о близких.",
            "strengths": ["Забота", "Ясность", "Верность"],
            "growth_zones": ["Слияние", "Обида", "Мягкое нет"],
        },
        "styles": {
            "relationship_style": "Близость через тёплые слова и предсказуемый темп без давления.",
            "money_style": "Деньги как спокойная безопасность и малые регулярные шаги.",
            "decision_style": "Решения через один свой критерий и короткий дедлайн.",
        },
        "natal": {
            "sun_sign": "Leo",
            "venus_sign": "Cancer",
            "jupiter_sign": "Cancer",
            "saturn_sign": "Capricorn",
            "mercury_sign": "Leo",
            "houses_available": False,
            "houses": {},
        },
    }


def test_synthesis_validation_fail_omits_without_projector(monkeypatch) -> None:
    monkeypatch.setattr(syn, "is_llm_chat_configured", lambda: True)

    def bad_call(**kwargs):
        return {
            "how": "коротко",
            "need": "x",
            "risk": "y",
            "turns_on": "z",
            "turns_off": "w",
            "helps": "v",
        }, "{}"

    monkeypatch.setattr(syn, "_call_sphere_llm", bad_call)
    spheres, meta = syn.synthesize_life_spheres_v0(_foundations(), max_retries=0)
    assert spheres == {}
    assert meta["spheres_source"] == SPHERES_SOURCE
    assert meta["ok"] is False
    assert all(o.get("reason") == "synthesis_validation_failed" for o in meta["spheres_omitted"])


def test_synthesis_accepts_validated_fields(monkeypatch) -> None:
    monkeypatch.setattr(syn, "is_llm_chat_configured", lambda: True)
    by_sphere = {
        "Любовь": {
            "how": (
                "В близости ты сначала проверяешь эмоциональную безопасность, прежде чем раскрыться. "
                "Замечаешь заботу через постоянство и мелкие действия рядом."
            ),
            "need": "Тебе нужен контакт, где тепло не приходится заслуживать ускорением темпа.",
            "risk": "Желание сохранить близость может заставлять долго молчать о том, что ранит.",
            "turns_on": "Когда человек помнит детали и выполняет обещанное без давления.",
            "turns_off": "Давление на быстрый ответ и непредсказуемые исчезновения.",
            "helps": "Назови дискомфорт одной ясной фразой, не дожидаясь дистанции.",
        },
        "Деньги": {
            "how": (
                "Ты спокойнее наращиваешь ценность регулярными шагами и понятным запасом. "
                "Рост без чувства безопасности для себя и близких не удерживается."
            ),
            "need": "Тебе нужна ясная база запаса, прежде чем расширять денежный горизонт.",
            "risk": "Забота о безопасности может тормозить даже полезный смелый вклад.",
            "turns_on": "Когда сумма, срок и цель названы без тумана.",
            "turns_off": "Когда требуют риск без потолка и без опоры цифр.",
            "helps": "Зафиксируй одну небольшую сумму регулярного пополнения на этой неделе.",
        },
        "Решения": {
            "how": (
                "Ты превращаешь выбор в график: критерий, срок и ответственность на себе. "
                "Нерешённое ощущается как долг перед собой, а не как свободный поиск."
            ),
            "need": "Тебе нужна рамка из одного критерия и короткого дедлайна до пересмотра.",
            "risk": "Дисциплина срока может превратиться в жёсткость без права на мягкий пересмотр.",
            "turns_on": "Когда выбор записан с датой первого шага.",
            "turns_off": "Когда варианты плодятся без точки закрытия.",
            "helps": "Запиши один критерий и срок проверки, затем закрой остальные ветки.",
        },
    }

    def good_call(*, system: str, user: str, temperature: float, max_tokens: int):
        for name, row in by_sphere.items():
            if f"Сфера: {name}" in user:
                return row, "{}"
        return by_sphere["Любовь"], "{}"

    monkeypatch.setattr(syn, "_call_sphere_llm", good_call)
    spheres, meta = syn.synthesize_life_spheres_v0(_foundations(), max_retries=0)
    assert set(spheres.keys()) == {"love", "money", "decisions"}
    assert meta["spheres_source"] == SPHERES_SOURCE
    assert meta["ok"] is True
    assert "how" in spheres["love"] and len(spheres["love"]["how"]) >= 40
