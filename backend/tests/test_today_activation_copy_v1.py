"""Shared Wave 2 activation copy — no planet/aspect jargon."""

from todayflow_backend.services.today_activation_copy_v1 import (
    aspect_class_label_short,
    aspect_class_why_short,
)


def test_why_and_label_share_aspect_classes_without_jargon():
    why = aspect_class_why_short("trine")
    label = aspect_class_label_short("trine", "venus")
    assert "опора" in why.lower() or "мягче" in label.lower()
    assert label == "Контакт мягче"
    for sample in (
        why,
        label,
        aspect_class_why_short("square"),
        aspect_class_label_short("square", "mars"),
    ):
        low = sample.lower()
        assert "трин" not in low
        assert "квадрат" not in low
        assert "венера" not in low
        assert "марс" not in low


def test_timeline_labels_distinct_by_body():
    soft_a = aspect_class_label_short("trine", "venus")
    soft_b = aspect_class_label_short("trine", "moon")
    hard_a = aspect_class_label_short("square", "mars")
    hard_b = aspect_class_label_short("square", "mercury")
    assert soft_a != soft_b
    assert hard_a != hard_b
    assert "сигнал дня" not in soft_a.lower()
    assert "сигнал дня" not in hard_a.lower()


def test_sun_square_is_lived_not_noun_pair():
    label = aspect_class_label_short("square", "sun")
    assert "в трении" not in label.lower()
    assert "ясность" in label.lower()


def test_soft_why_is_domain_distinct():
    whys = [aspect_class_why_short("trine", d) for d in ("work", "money", "relationships", "energy")]
    assert len(set(whys)) == 4
    assert "Есть опора — можно опереться" not in whys


def test_hard_why_is_domain_distinct():
    whys = [aspect_class_why_short("square", d) for d in ("work", "money", "relationships", "energy")]
    assert len(set(whys)) == 4
