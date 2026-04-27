"""pigeon — POSIX gettext-style plural-form expression parser and evaluator.

A tiny, dependency-free library that parses the ``Plural-Forms`` strings
found in PO file headers and evaluates them for a given operand ``n``.

Quick example::

    >>> import pigeon
    >>> compiled = pigeon.parse("nplurals=2; plural=(n != 1);")
    >>> compiled.nplurals
    2
    >>> compiled.evaluate(1)
    0
    >>> compiled.evaluate(7)
    1

A locale-aware shortcut is provided for the common case::

    >>> pigeon.select("ru", 21)
    0
    >>> pigeon.select("ru", 5)
    2

The grammar implemented here is the C-style subset accepted by GNU
gettext: integer literals, the operand ``n``, the operators
``! + - * / % == != < <= > >= && ||``, parenthesised sub-expressions, and
the ternary ``cond ? then : else``. CLDR plural rules (``many``, ``few``,
``zero`` keywords, decimal operands) are intentionally **not** supported.
"""

from __future__ import annotations

from ._errors import (
    EvaluationError,
    ParseError,
    PluralFormError,
    UnknownLocaleError,
)
from ._eval import (
    BinaryOp,
    IntLit,
    NRef,
    Node,
    Ternary,
    UnaryOp,
    evaluate_node,
)
from ._locales import PLURAL_FORMS, lookup, normalise_locale
from ._parser import Compiled, parse, parse_expression, select_index

__all__ = [
    "parse",
    "parse_expression",
    "evaluate",
    "select",
    "forms_for",
    "nplurals",
    "available_locales",
    "Compiled",
    "Node",
    "IntLit",
    "NRef",
    "UnaryOp",
    "BinaryOp",
    "Ternary",
    "PluralFormError",
    "ParseError",
    "EvaluationError",
    "UnknownLocaleError",
    "PLURAL_FORMS",
]

__version__ = "0.1.0"


def evaluate(compiled: Compiled, n: int | float) -> int:
    if not isinstance(compiled, Compiled):
        raise TypeError("first argument must be a Compiled plural form")
    return select_index(compiled, n)


def select(locale: str, n: int | float) -> int:
    plural_form = lookup(locale)
    if plural_form is None:
        raise UnknownLocaleError(f"no built-in plural form for locale {locale!r}")
    compiled = parse(plural_form)
    return select_index(compiled, n)


def forms_for(locale: str) -> str:
    plural_form = lookup(locale)
    if plural_form is None:
        raise UnknownLocaleError(f"no built-in plural form for locale {locale!r}")
    return plural_form


def nplurals(compiled: Compiled) -> int:
    if not isinstance(compiled, Compiled):
        raise TypeError("argument must be a Compiled plural form")
    return compiled.nplurals


def available_locales() -> tuple[str, ...]:
    return tuple(sorted(PLURAL_FORMS))


del evaluate_node  # not part of the public API surface
