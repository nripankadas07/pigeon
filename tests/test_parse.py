"""Tests for the tokenizer and parser."""

from __future__ import annotations

import pytest

import pigeon
from pigeon._eval import BinaryOp, IntLit, NRef, Ternary, UnaryOp
from pigeon._parser import parse_expression, tokenize


def test_tokenize_empty_string_returns_no_tokens():
    assert tokenize("") == []


def test_tokenize_whitespace_only_returns_no_tokens():
    assert tokenize("   \t\n") == []


def test_tokenize_recognises_each_punctuation_kind():
    tokens = tokenize("(  ) ; ? :")
    assert [token.kind for token in tokens] == ["LPAREN", "RPAREN", "SEMI", "QMARK", "COLON"]


def test_tokenize_two_char_operators_take_priority():
    tokens = tokenize("== != <= >= && ||")
    assert [token.text for token in tokens] == ["==", "!=", "<=", ">=", "&&", "||"]


def test_tokenize_one_char_operators_recognised():
    tokens = tokenize("+ - * / % < > !")
    assert [token.text for token in tokens] == ["+", "-", "*", "/", "%", "<", ">", "!"]


def test_tokenize_identifier_with_underscore():
    tokens = tokenize("nplurals plural _hidden a1b")
    assert [token.text for token in tokens] == ["nplurals", "plural", "_hidden", "a1b"]


def test_tokenize_decimal_integer():
    (token,) = tokenize("12345")
    assert token.kind == "INT" and token.text == "12345"


def test_tokenize_hexadecimal_integer():
    (token,) = tokenize("0xFF")
    assert token.text == "0xFF"


def test_tokenize_position_recorded_for_each_token():
    tokens = tokenize("nplurals=2")
    assert tokens[0].position == 0
    assert tokens[1].position == 8
    assert tokens[2].position == 9


def test_tokenize_unknown_character_raises_parse_error():
    with pytest.raises(pigeon.ParseError) as info:
        tokenize("@")
    assert info.value.position == 0


def test_tokenize_invalid_hex_literal_raises():
    with pytest.raises(pigeon.ParseError):
        tokenize("0xZ")


def test_parse_simple_english_form():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    assert compiled.nplurals == 2
    assert compiled.evaluate(0) == 1
    assert compiled.evaluate(1) == 0
    assert compiled.evaluate(2) == 1


def test_parse_japanese_single_form():
    compiled = pigeon.parse("nplurals=1; plural=0;")
    assert compiled.nplurals == 1
    assert compiled.evaluate(0) == 0
    assert compiled.evaluate(99) == 0


def test_parse_french_form_uses_n_greater_than_1():
    compiled = pigeon.parse("nplurals=2; plural=(n > 1);")
    assert compiled.evaluate(0) == 0
    assert compiled.evaluate(1) == 0
    assert compiled.evaluate(2) == 1


def test_parse_strips_extra_whitespace():
    compiled = pigeon.parse("  nplurals = 2 ;\n  plural = ( n != 1 ) ;  ")
    assert compiled.nplurals == 2
    assert compiled.evaluate(1) == 0


def test_parse_allows_missing_trailing_semicolon():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1)")
    assert compiled.nplurals == 2


def test_parse_allows_multiple_trailing_semicolons():
    compiled = pigeon.parse("nplurals=2; plural=(n != 1);;;")
    assert compiled.nplurals == 2


def test_parse_empty_string_raises():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("")


def test_parse_whitespace_only_raises():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("   \n\t  ")


def test_parse_missing_nplurals_keyword_raises():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("plural=(n != 1);")


def test_parse_missing_plural_keyword_raises():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("nplurals=2;")


def test_parse_zero_nplurals_raises():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("nplurals=0; plural=0;")


def test_parse_negative_nplurals_raises():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("nplurals=-1; plural=0;")


def test_parse_unknown_identifier_in_expression_raises():
    with pytest.raises(pigeon.ParseError) as info:
        pigeon.parse("nplurals=2; plural=(m != 1);")
    assert "m" in str(info.value)


def test_parse_unbalanced_parentheses_raises():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("nplurals=2; plural=(n != 1;")


def test_parse_trailing_garbage_raises():
    with pytest.raises(pigeon.ParseError):
        pigeon.parse("nplurals=2; plural=(n != 1); garbage")


def test_parse_source_attribute_preserved():
    source = "nplurals=2; plural=(n != 1);"
    compiled = pigeon.parse(source)
    assert compiled.source == source


def test_parse_expression_returns_int_literal():
    node = parse_expression("42")
    assert node == IntLit(42)


def test_parse_expression_returns_n_reference():
    node = parse_expression("n")
    assert node == NRef()


def test_parse_expression_handles_unary_minus():
    node = parse_expression("-5")
    assert node == UnaryOp("-", IntLit(5))


def test_parse_expression_handles_logical_not():
    node = parse_expression("!n")
    assert node == UnaryOp("!", NRef())


def test_parse_expression_addition_left_associative():
    node = parse_expression("1 + 2 + 3")
    assert node == BinaryOp("+", BinaryOp("+", IntLit(1), IntLit(2)), IntLit(3))


def test_parse_expression_multiplication_binds_tighter_than_addition():
    node = parse_expression("1 + 2 * 3")
    assert node == BinaryOp("+", IntLit(1), BinaryOp("*", IntLit(2), IntLit(3)))


def test_parse_expression_parens_override_precedence():
    node = parse_expression("(1 + 2) * 3")
    assert node == BinaryOp("*", BinaryOp("+", IntLit(1), IntLit(2)), IntLit(3))


def test_parse_expression_ternary_right_associative():
    node = parse_expression("1 ? 2 : 3 ? 4 : 5")
    assert node == Ternary(IntLit(1), IntLit(2), Ternary(IntLit(3), IntLit(4), IntLit(5)))


def test_parse_expression_logical_and_or_precedence():
    node = parse_expression("1 || 2 && 3")
    assert node == BinaryOp("||", IntLit(1), BinaryOp("&&", IntLit(2), IntLit(3)))


def test_parse_expression_trailing_token_raises():
    with pytest.raises(pigeon.ParseError):
        parse_expression("n + 1 garbage")


def test_parse_expression_empty_raises():
    with pytest.raises(pigeon.ParseError):
        parse_expression("")


def test_parse_expression_hex_literal():
    node = parse_expression("0x10")
    assert node == IntLit(16)


def test_parse_expression_octal_literal():
    node = parse_expression("010")
    assert node == IntLit(8)
