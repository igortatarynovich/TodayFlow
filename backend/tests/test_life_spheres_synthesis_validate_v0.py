"""False-positive guards for synthesis validators (not content quality)."""

from todayflow_backend.services.life_spheres_synthesis_validate_v0 import (
    validate_sphere_synthesis_v0,
)


def _row(**overrides: str) -> dict[str, str]:
    base = {
        "how": (
            "Ты входишь в близость через спокойное присутствие и ясную заботу. "
            "Ритм контакта важнее громких жестов и давления."
        ),
        "need": "Тебе нужно пространство, где тепло не приходится заслуживать ускорением темпа.",
        "risk": "Желание сохранить мягкость может заставлять долго молчать о дискомфорте.",
        "turns_on": "Когда человек помнит детали и выполняет обещанное без давления.",
        "turns_off": "Когда темп форсируют и пропадают без объяснения.",
        "helps": "Назови дискомфорт одной ясной фразой, не дожидаясь дистанции.",
    }
    base.update(overrides)
    return base


def test_ravnovesie_does_not_trigger_mars_ban():
    v = validate_sphere_synthesis_v0(
        _row(helps="Попроси паузу, чтобы восстановить внутреннее равновесие."),
        identity_core="Держит смысл через тёплый контакт и ясную заботу о близких.",
        relevant_style="Близость через тёплые слова и предсказуемый темп без давления.",
        sphere_cues=[
            "спокойное присутствие и ясную заботу",
            "тепло и мягкий темп без давления",
            "помнить детали и выполнять обещанное",
        ],
    )
    assert v["checks"]["no_astro_kitchen"] is True
    assert not any("kitchen leaked" in d.get("note", "") for d in v["defects"])


def test_regulyarnost_does_not_trigger_longitudinal_ban():
    v = validate_sphere_synthesis_v0(
        _row(
            how=(
                "Ты выстраиваешь денежные привычки через повторяющиеся действия, "
                "где регулярность пополнения счёта ценится выше спонтанного куша."
            )
        ),
        identity_core="Строит опору через порядок и долгие обязательства.",
        relevant_style="Деньги через структуру: учёт и правила ценности времени.",
        sphere_cues=["легче наращивать ценность регулярными шагами", "стабильность базы"],
    )
    assert v["checks"]["no_longitudinal"] is True
