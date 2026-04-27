"""Tests for the AST evaluator and Compiled.evaluate."""

from __future__ import annotations

import pytest

import pigeon


def _eval(expression, n):
    from pigeon._eval import evaluate_node
    from pigeon._parser import parse_expression
    return evaluate_node(parse_expression(expression), abs(n))


def test_eval_addition():
    assert _eval("1 + 2", 0) == 3


def test_eval_subtraction():
    assert _eval("10 - 3", 0) == 7


def test_eval_multiplication():
    assert _eval("4 * 5", 0) == 20


def test_eval_division_truncates_toward_zero():
    assert _eval("7 / 2", 0) == 3


def test_eval_modulo_basic():
    assert _eval("10 % 3", 0) == 1


def test_eval_division_negative_left_operand():
    from pigeon._eval import BinaryOp, IntLit, evaluate_node
    expression = BinaryOp("/", IntLit(-7), IntLit(2))
    assert evaluate_node(expression, 0) == -3


def test_eval_modulo_negative_left_operand_keeps_dividend_sign():
    from pigeon._eval import BinaryOp, IntLit, evaluate_node
    expression = BinaryOp("%", IntLit(-7), IntLit(2))
    assert evaluate_node(expression, 0) == -1


def test_eval_division_by_zero_raises():
    with pytest.raises(pigeon.EvaluationError):
        _eval("1 / 0", 0)


def test_eval_modulo_by_zero_raises():
    with pytest.raises(pigeon.EvaluationError):
        _eval("1 % 0", 0)


@pytest.mark.parametrize(
    "expression,operand,expected",
    [
        ("n == 1", 1, 1),
        ("n == 1", 2, 0),
        ("n != 1", 1, 0),
        ("n != 1", 2, 1),
        ("n < 5", 4, 1),
        ("n < 5", 5, 0),
        ("n <= 5", 5, 1),
        ("n > 5", 6, 1),
        ("n > 5", 5, 0),
        ("n >= 5", 5, 1),
    ],
)
def test_eval_comparison_returns_zero_or_one(expression, operand, expected):
    assert _eval(expression, operand) == expected


def test_eval_logical_and_short_circuits():
    assert _eval("0 && 1 / 0", 0) == 0


def test_eval_logical_or_short_circuits():
    assert _eval("1 || 1 / 0", 0) == 1


def test_eval_logical_not_inverts_truthiness():
    assert _eval("!0", 0) == 1
    assert _eval("!1", 0) == 0
    assert _eval("!42", 0) == 0


def test_eval_ternary_then_branch_when_truthy():
    assert _eval("n == 1 ? 100 : 200", 1) == 100


def test_eval_ternary_else_branch_when_falsy():
    assert _eval("n == 1 ? 100 : 200", 5) == 200


def test_eval_ternary_chained():
    expression = "n == 0 ? 0 : n == 1 ? 1 : 2"
    assert _eval(expression, 0) == 0
    assert _eval(expression, 1) == 1
    assert _eval(expression, 5) == 2


def test_compiled_evaluate_clamps_negative_result_to_zero():
    compiled = pigeon.parse("nplurals=2; plural=-1;")
    assert compiled.evaluate(0) == 0


def test_compiled_evaluate_clamps_overflow_to_last_index():
    compiled = pigeon.parse("nplurals=2; plural=99;")
    assert compiled.evaluate(0) == 1


def test_compiled_evaluate_accepts_float_operand():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    assert compiled.evaluate(1.0) == 0
    assert compiled.evaluate(2.5) == 1


def test_compiled_evaluate_takes_absolute_value_of_negative_n():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    assert compiled.evaluate(-1) == 0
    assert compiled.evaluate(-2) == 1


def test_compiled_evaluate_rejects_bool():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    with pytest.raises(TypeError):
        compiled.evaluate(True)


def test_compiled_evaluate_rejects_string():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    with pytest.raises(TypeError):
        compiled.evaluate("1")


def test_compiled_evaluate_rejects_nan():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    with pytest.raises(ValueError):
        compiled.evaluate(float("nan"))


def test_compiled_evaluate_rejects_infinity():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    with pytest.raises(ValueError):
        compiled.evaluate(float("inf"))
