"""Integration tests covering common gettext-style usage patterns."""

from __future__ import annotations

import pytest

import pigeon


ENGLISH_CATEGORIES = ["one", "other"]
RUSSIAN_CATEGORIES = ["one", "few", "many"]


def _category(locale, n, categories):
    return categories[pigeon.select(locale, n)]


@pytest.mark.parametrize(
    "n,expected",
    [(1, "one"), (0, "other"), (2, "other"), (21, "other"), (101, "other")],
)
def test_english_categories(n, expected):
    assert _category("en", n, ENGLISH_CATEGORIES) == expected


@pytest.mark.parametrize(
    "n,expected",
    [
        (1, "one"),
        (21, "one"),
        (101, "one"),
        (2, "few"),
        (3, "few"),
        (4, "few"),
        (22, "few"),
        (5, "many"),
        (10, "many"),
        (11, "many"),
        (15, "many"),
        (100, "many"),
        (1000, "many"),
    ],
)
def test_russian_categories(n, expected):
    assert _category("ru", n, RUSSIAN_CATEGORIES) == expected


def test_round_trip_via_compiled_caches_the_parse():
    plural_form = pigeon.forms_for("ru")
    compiled = pigeon.parse(plural_form)
    for value in range(0, 200):
        assert compiled.evaluate(value) == pigeon.select("ru", value)


def test_select_matches_evaluate_for_polish():
    plural_form = pigeon.forms_for("pl")
    compiled = pigeon.parse(plural_form)
    for value in range(0, 50):
        assert pigeon.evaluate(compiled, value) == pigeon.select("pl", value)


def test_arabic_full_table():
    expected = {0: 0, 1: 1, 2: 2, 3: 3, 5: 3, 10: 3, 11: 4, 50: 4, 99: 4, 100: 5, 101: 5, 200: 5}
    for value, category in expected.items():
        assert pigeon.select("ar", value) == category, value
