"""Tests for the built-in locale plural-form table."""

from __future__ import annotations

import pytest

import pigeon


def test_available_locales_includes_common_choices():
    locales = pigeon.available_locales()
    assert "en" in locales
    assert "fr" in locales
    assert "ru" in locales
    assert "ja" in locales
    assert "ar" in locales
    assert "pt_BR" in locales


def test_available_locales_returns_sorted_tuple():
    locales = pigeon.available_locales()
    assert isinstance(locales, tuple)
    assert list(locales) == sorted(locales)


def test_every_built_in_form_parses_cleanly():
    for locale, plural_form in pigeon.PLURAL_FORMS.items():
        compiled = pigeon.parse(plural_form)
        assert compiled.nplurals >= 1, locale


def test_forms_for_returns_canonical_string():
    assert pigeon.forms_for("en") == "nplurals=2; plural=(n != 1);"


def test_forms_for_falls_back_from_region_to_language():
    assert pigeon.forms_for("en_US") == pigeon.forms_for("en")


def test_forms_for_explicit_region_overrides_language_default():
    assert pigeon.forms_for("pt_BR") != pigeon.forms_for("pt")


def test_forms_for_strips_encoding_suffix():
    assert pigeon.forms_for("en_US.UTF-8") == pigeon.forms_for("en")


def test_forms_for_strips_modifier():
    assert pigeon.forms_for("ca_ES@valencia") == pigeon.forms_for("ca")


def test_forms_for_accepts_dash_separator():
    assert pigeon.forms_for("pt-BR") == pigeon.forms_for("pt_BR")


def test_forms_for_unknown_locale_raises():
    with pytest.raises(pigeon.UnknownLocaleError):
        pigeon.forms_for("xx_XX")


def test_forms_for_empty_locale_raises():
    with pytest.raises(ValueError):
        pigeon.forms_for("")


def test_forms_for_non_string_raises():
    with pytest.raises(TypeError):
        pigeon.forms_for(123)


@pytest.mark.parametrize("n,expected", [(0, 1), (1, 0), (2, 1), (5, 1), (100, 1)])
def test_select_english(n, expected):
    assert pigeon.select("en", n) == expected


@pytest.mark.parametrize("n,expected", [(0, 0), (1, 0), (2, 1), (5, 1)])
def test_select_french_treats_zero_as_singular(n, expected):
    assert pigeon.select("fr", n) == expected


@pytest.mark.parametrize("n,expected", [(1, 0), (21, 0), (101, 0), (2, 1), (3, 1), (4, 1), (22, 1), (5, 2), (11, 2), (15, 2)])
def test_select_russian(n, expected):
    assert pigeon.select("ru", n) == expected


@pytest.mark.parametrize("n,expected", [(0, 0), (1, 0), (2, 0), (10, 0), (99, 0), (1000, 0)])
def test_select_japanese_always_returns_zero(n, expected):
    assert pigeon.select("ja", n) == expected


@pytest.mark.parametrize("n,expected", [(0, 0), (1, 1), (2, 2), (3, 3), (10, 3), (11, 4), (100, 5)])
def test_select_arabic_six_categories(n, expected):
    assert pigeon.select("ar", n) == expected


@pytest.mark.parametrize("n,expected", [(1, 0), (2, 1), (3, 1), (4, 1), (5, 2), (10, 2), (101, 2)])
def test_select_polish(n, expected):
    assert pigeon.select("pl", n) == expected


def test_select_unknown_locale_raises():
    with pytest.raises(pigeon.UnknownLocaleError):
        pigeon.select("xx", 1)


def test_select_falls_back_to_language():
    assert pigeon.select("de_AT", 1) == 0
    assert pigeon.select("de_AT", 2) == 1


def test_select_handles_locale_dash_form():
    assert pigeon.select("pt-BR", 0) == 0
    assert pigeon.select("pt-BR", 2) == 1
