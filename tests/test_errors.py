"""Tests focused on every documented error path."""

from __future__ import annotations

import pytest

import pigeon


def test_parse_error_is_subclass_of_plural_form_error():
    assert issubclass(pigeon.ParseError, pigeon.PluralFormError)


def test_evaluation_error_is_subclass_of_plural_form_error():
    assert issubclass(pigeon.EvaluationError, pigeon.PluralFormError)


def test_unknown_locale_error_is_subclass_of_plural_form_error():
    assert issubclass(pigeon.UnknownLocaleError, pigeon.PluralFormError)


def test_parse_error_carries_position():
    with pytest.raises(pigeon.ParseError) as info:
        pigeon.parse("nplurals=@; plural=0;")
    assert info.value.position == 9


def test_parse_error_position_can_be_none():
    error = pigeon.ParseError("no position")
    assert error.position is None


def test_parse_error_at_end_of_input():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("nplurals=2;")


def test_parse_error_for_missing_equal():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("nplurals 2; plural=0;")


def test_parse_error_for_unbalanced_ternary():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("nplurals=2; plural=(n == 1 ? 0);")


def test_evaluation_error_for_runtime_division_by_zero():
    compiled = pigeon.parse("nplurals=2; plural=n / 0;")
    with pytest.raises(pigeon.EvaluationError):
        compiled.evaluate(5)


def test_evaluation_error_for_runtime_modulo_by_zero():
    compiled = pigeon.parse("nplurals=2; plural=n % 0;")
    with pytest.raises(pigeon.EvaluationError):
        compiled.evaluate(5)


def test_unknown_locale_for_select():
    with pytest.raises(pigeon.UnknownLocaleError) as info:
        pigeon.select("zz", 1)
    assert "zz" in str(info.value)


def test_unknown_locale_for_forms_for():
    with pytest.raises(pigeon.UnknownLocaleError) as info:
        pigeon.forms_for("not-a-real-locale")
    assert "not-a-real-locale" in str(info.value)


def test_normalise_locale_rejects_non_string():
    from pigeon._locales import normalise_locale
    with pytest.raises(TypeError):
        normalise_locale(123)


def test_normalise_locale_rejects_empty_string():
    from pigeon._locales import normalise_locale
    with pytest.raises(ValueError):
        normalise_locale("")
