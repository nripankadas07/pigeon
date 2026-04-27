"""Tests for the top-level ``pigeon.evaluate`` and ``pigeon.nplurals`` helpers."""

from __future__ import annotations

import pytest

import pigeon


def test_evaluate_returns_zero_one_for_english():
    compiled = pigeon.parse(pigeon.forms_for("en"))
    assert pigeon.evaluate(compiled, 1) == 0
    assert pigeon.evaluate(compiled, 7) == 1


def test_evaluate_rejects_non_compiled_first_argument():
    with pytest.raises(TypeError):
        pigeon.evaluate("nplurals=1; plural=0;", 1)


def test_nplurals_returns_declared_count():
    compiled = pigeon.parse(pigeon.forms_for("ar"))
    assert pigeon.nplurals(compiled) == 6


def test_nplurals_rejects_non_compiled_argument():
    with pytest.raises(TypeError):
        pigeon.nplurals("nope")


def test_evaluate_after_repeated_parse_yields_same_result():
    plural_form = pigeon.forms_for("ru")
    first = pigeon.parse(plural_form)
    second = pigeon.parse(plural_form)
    for value in [0, 1, 2, 5, 21, 22, 100, 1001]:
        assert first.evaluate(value) == second.evaluate(value)


def test_compiled_is_dataclass_with_meaningful_attributes():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    assert compiled.nplurals == 2
    assert compiled.source == "nplurals=2; plural=(n != 1);"
    assert isinstance(compiled.expression, (pigeon.BinaryOp, pigeon.UnaryOp, pigeon.Ternary, pigeon.IntLit, pigeon.NRef))
