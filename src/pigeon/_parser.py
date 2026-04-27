"""Tokenizer and recursive-descent parser for POSIX gettext plural-form expressions.

Grammar (whitespace permitted between tokens; ``//``-style comments are not
supported because real Plural-Forms strings never use them)::

    plural_form     := 'nplurals' '=' INT ';' 'plural' '=' expr ';'?
    expr            := ternary
    ternary         := lor ('?' expr ':' expr)?
    lor             := land ('||' land)*
    land            := equality ('&&' equality)*
    equality        := relational (('==' | '!=') relational)*
    relational      := additive (('<' | '<=' | '>' | '>=') additive)*
    additive        := multiplicative (('+' | '-') multiplicative)*
    multiplicative  := unary (('*' | '/' | '%') unary)*
    unary           := ('!' | '-' | '+') unary | primary
    primary         := INT | 'n' | '(' expr ')'

The integer-literal token accepts decimal, hex (``0x...``) and octal (``0...``)
forms because gettext implementations have historically accepted them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ._errors import ParseError
from ._eval import BinaryOp, IntLit, NRef, Node, Ternary, UnaryOp


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    position: int


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    length = len(source)
    while index < length:
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if char == ";":
            tokens.append(Token("SEMI", ";", index)); index += 1; continue
        if char == "(":
            tokens.append(Token("LPAREN", "(", index)); index += 1; continue
        if char == ")":
            tokens.append(Token("RPAREN", ")", index)); index += 1; continue
        if char == "?":
            tokens.append(Token("QMARK", "?", index)); index += 1; continue
        if char == ":":
            tokens.append(Token("COLON", ":", index)); index += 1; continue
        if char.isdigit():
            literal, index = _read_integer(source, index)
            tokens.append(Token("INT", literal, index - len(literal)))
            continue
        if char.isalpha() or char == "_":
            ident, index = _read_identifier(source, index)
            tokens.append(Token("IDENT", ident, index - len(ident)))
            continue
        op, index = _read_operator(source, index)
        if op is None:
            raise ParseError(f"unexpected character {char!r} at position {index}", index)
        tokens.append(Token("OP", op, index - len(op)))
    return tokens


def _read_integer(source: str, index: int) -> tuple[str, int]:
    start = index
    if source[index] == "0" and index + 1 < len(source) and source[index + 1] in "xX":
        index += 2
        digits_start = index
        while index < len(source) and source[index] in "0123456789abcdefABCDEF":
            index += 1
        if index == digits_start:
            raise ParseError("invalid hexadecimal literal", start)
        return source[start:index], index
    while index < len(source) and source[index].isdigit():
        index += 1
    return source[start:index], index


def _read_identifier(source: str, index: int) -> tuple[str, int]:
    start = index
    while index < len(source) and (source[index].isalnum() or source[index] == "_"):
        index += 1
    return source[start:index], index


_TWO_CHAR_OPS = {"==", "!=", "<=", ">=", "&&", "||"}
_ONE_CHAR_OPS = set("+-*/%<>!=")


def _read_operator(source: str, index: int) -> tuple[str | None, int]:
    if index + 1 < len(source):
        candidate = source[index : index + 2]
        if candidate in _TWO_CHAR_OPS:
            return candidate, index + 2
    char = source[index]
    if char in _ONE_CHAR_OPS:
        return char, index + 1
    return None, index


@dataclass
class Compiled:
    nplurals: int
    expression: Node
    source: str

    def evaluate(self, n: int | float) -> int:
        return select_index(self, n)


def parse(source: str) -> Compiled:
    if not isinstance(source, str):
        raise TypeError("plural-form source must be a string")
    if not source.strip():
        raise ParseError("empty plural-form string")
    tokens = tokenize(source)
    parser = _Parser(tokens, source)
    return parser.parse_plural_form()


def parse_expression(source: str) -> Node:
    if not isinstance(source, str):
        raise TypeError("expression source must be a string")
    tokens = tokenize(source)
    parser = _Parser(tokens, source)
    expression = parser.parse_expression()
    parser.expect_eof()
    return expression


def select_index(compiled: Compiled, n: int | float) -> int:
    from ._eval import evaluate_node
    integer_n = _coerce_n(n)
    raw = evaluate_node(compiled.expression, integer_n)
    if raw < 0:
        raw = 0
    if raw >= compiled.nplurals:
        raw = compiled.nplurals - 1
    return raw


def _coerce_n(n: int | float) -> int:
    if isinstance(n, bool):
        raise TypeError("plural operand must be a number, got bool")
    if isinstance(n, int):
        return abs(n)
    if isinstance(n, float):
        if n != n or n in (float("inf"), float("-inf")):
            raise ValueError("plural operand must be a finite number")
        return abs(int(n))
    raise TypeError(f"plural operand must be int or float, got {type(n).__name__}")


class _Parser:
    def __init__(self, tokens: Iterable[Token], source: str) -> None:
        self._tokens: list[Token] = list(tokens)
        self._index = 0
        self._source = source

    def _peek(self, offset: int = 0) -> Token | None:
        target = self._index + offset
        if target >= len(self._tokens):
            return None
        return self._tokens[target]

    def _consume(self) -> Token:
        token = self._tokens[self._index]
        self._index += 1
        return token

    def _match(self, kind: str, text: str | None = None) -> Token | None:
        token = self._peek()
        if token is None or token.kind != kind:
            return None
        if text is not None and token.text != text:
            return None
        return self._consume()

    def _expect(self, kind: str, text: str | None = None) -> Token:
        token = self._peek()
        if token is None:
            raise ParseError(f"unexpected end of input (expected {text or kind})", len(self._source))
        if token.kind != kind or (text is not None and token.text != text):
            raise ParseError(f"expected {text or kind} at position {token.position}, got {token.text!r}", token.position)
        return self._consume()

    def expect_eof(self) -> None:
        token = self._peek()
        if token is not None:
            raise ParseError(f"unexpected trailing token {token.text!r} at position {token.position}", token.position)

    def parse_plural_form(self) -> Compiled:
        nplurals_keyword = self._expect("IDENT", "nplurals")
        self._expect("OP", "=")
        nplurals_token = self._expect("INT")
        nplurals_value = _parse_int_literal(nplurals_token.text, nplurals_token.position)
        if nplurals_value <= 0:
            raise ParseError(f"nplurals must be a positive integer, got {nplurals_value}", nplurals_keyword.position)
        self._expect("SEMI")
        self._expect("IDENT", "plural")
        self._expect("OP", "=")
        expression = self.parse_expression()
        while self._match("SEMI") is not None:
            pass
        self.expect_eof()
        return Compiled(nplurals=nplurals_value, expression=expression, source=self._source)

    def parse_expression(self) -> Node:
        return self._parse_ternary()

    def _parse_ternary(self) -> Node:
        condition = self._parse_logical_or()
        if self._match("QMARK") is not None:
            then_branch = self._parse_ternary()
            self._expect("COLON")
            else_branch = self._parse_ternary()
            return Ternary(condition=condition, then_branch=then_branch, else_branch=else_branch)
        return condition

    def _parse_logical_or(self) -> Node:
        left = self._parse_logical_and()
        while self._match("OP", "||") is not None:
            right = self._parse_logical_and()
            left = BinaryOp("||", left, right)
        return left

    def _parse_logical_and(self) -> Node:
        left = self._parse_equality()
        while self._match("OP", "&&") is not None:
            right = self._parse_equality()
            left = BinaryOp("&&", left, right)
        return left

    def _parse_equality(self) -> Node:
        left = self._parse_relational()
        while True:
            for operator in ("==", "!="):
                if self._match("OP", operator) is not None:
                    right = self._parse_relational()
                    left = BinaryOp(operator, left, right)
                    break
            else:
                return left

    def _parse_relational(self) -> Node:
        left = self._parse_additive()
        while True:
            for operator in ("<=", ">=", "<", ">"):
                if self._match("OP", operator) is not None:
                    right = self._parse_additive()
                    left = BinaryOp(operator, left, right)
                    break
            else:
                return left

    def _parse_additive(self) -> Node:
        left = self._parse_multiplicative()
        while True:
            for operator in ("+", "-"):
                if self._match("OP", operator) is not None:
                    right = self._parse_multiplicative()
                    left = BinaryOp(operator, left, right)
                    break
            else:
                return left

    def _parse_multiplicative(self) -> Node:
        left = self._parse_unary()
        while True:
            for operator in ("*", "/", "%"):
                if self._match("OP", operator) is not None:
                    right = self._parse_unary()
                    left = BinaryOp(operator, left, right)
                    break
            else:
                return left

    def _parse_unary(self) -> Node:
        token = self._peek()
        if token is not None and token.kind == "OP" and token.text in ("!", "-", "+"):
            self._consume()
            operand = self._parse_unary()
            return UnaryOp(token.text, operand)
        return self._parse_primary()

    def _parse_primary(self) -> Node:
        token = self._peek()
        if token is None:
            raise ParseError("unexpected end of expression", len(self._source))
        if token.kind == "INT":
            self._consume()
            return IntLit(_parse_int_literal(token.text, token.position))
        if token.kind == "IDENT":
            if token.text != "n":
                raise ParseError(f"unknown identifier {token.text!r} at position {token.position}", token.position)
            self._consume()
            return NRef()
        if token.kind == "LPAREN":
            self._consume()
            expression = self.parse_expression()
            self._expect("RPAREN")
            return expression
        raise ParseError(f"unexpected token {token.text!r} at position {token.position}", token.position)


def _parse_int_literal(text: str, position: int) -> int:
    try:
        if text.startswith(("0x", "0X")):
            return int(text, 16)
        if len(text) > 1 and text.startswith("0"):
            return int(text, 8)
        return int(text, 10)
    except ValueError as exc:
        raise ParseError(f"invalid integer literal {text!r}", position) from exc
