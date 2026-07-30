"""Shared Wave 2 activation copy — no planet/aspect jargon."""

from todayflow_backend.services.today_activation_copy_v1 import (
    aspect_class_label_short,
    aspect_class_why_short,
)


def test_why_and_label_share_aspect_classes_without_jargon():
    why = aspect_class_why_short("trine")
    label = aspect_class_label_short("trine")
    assert "опора" in why.lower()
    assert label == "Есть опора"
    for sample in (why, label, aspect_class_why_short("square"), aspect_class_label_short("square")):
        low = sample.lower()
        assert "трин" not in low
        assert "квадрат" not in low
        assert "венера" not in low
        assert "марс" not in low


def test_soft_why_is_domain_distinct():
    whys = [aspect_class_why_short("trine", d) for d in ("work", "money", "relationships", "energy")]
    assert len(set(whys)) == 4
    assert "Есть опора — можно опереться" not in whys


def test_hard_why_is_domain_distinct():
    whys = [aspect_class_why_short("square", d) for d in ("work", "money", "relationships", "energy")]
    assert len(set(whys)) == 4
