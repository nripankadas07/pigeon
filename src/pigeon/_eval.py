"""AST node definitions and evaluator for pigeon plural-form expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from ._errors import EvaluationError


@dataclass(frozen=True)
class IntLit:
    """Integer literal."""

    value: int


@dataclass(frozen=True)
class NRef:
    """Reference to the operand variable ``n``."""


@dataclass(frozen=True)
class UnaryOp:
    """Unary operator: ``!expr`` or ``-expr``."""

    op: str
    operand: "Node"


@dataclass(frozen=True)
class BinaryOp:
    """Binary operator: arithmetic / comparison / logical."""

    op: str
    left: "Node"
    right: "Node"


@dataclass(frozen=True)
class Ternary:
    """Ternary conditional ``cond ? then : otherwise``."""

    condition: "Node"
    then_branch: "Node"
    else_branch: "Node"


Node = Union[IntLit, NRef, UnaryOp, BinaryOp, Ternary]


def evaluate_node(node: Node, n: int) -> int:
    """Evaluate ``node`` with the operand ``n`` bound to the given integer.

    Boolean results are returned as ``0`` / ``1`` to match C semantics.
    Raises ``EvaluationError`` on division/modulo by zero.
    """
    if isinstance(node, IntLit):
        return node.value
    if isinstance(node, NRef):
        return n
    if isinstance(node, UnaryOp):
        return _eval_unary(node, n)
    if isinstance(node, BinaryOp):
        return _eval_binary(node, n)
    if isinstance(node, Ternary):
        cond = evaluate_node(node.condition, n)
        if cond:
            return evaluate_node(node.then_branch, n)
        return evaluate_node(node.else_branch, n)
    raise EvaluationError(f"unknown AST node type: {type(node).__name__}")


def _eval_unary(node: UnaryOp, n: int) -> int:
    operand_value = evaluate_node(node.operand, n)
    if node.op == "!":
        return 1 if operand_value == 0 else 0
    if node.op == "-":
        return -operand_value
    if node.op == "+":
        return operand_value
    raise EvaluationError(f"unknown unary operator: {node.op!r}")


def _eval_binary(node: BinaryOp, n: int) -> int:
    op = node.op
    if op == "&&":
        return 1 if evaluate_node(node.left, n) and evaluate_node(node.right, n) else 0
    if op == "||":
        return 1 if evaluate_node(node.left, n) or evaluate_node(node.right, n) else 0
    left = evaluate_node(node.left, n)
    right = evaluate_node(node.right, n)
    handler = _BINARY_HANDLERS.get(op)
    if handler is None:
        raise EvaluationError(f"unknown binary operator: {op!r}")
    return handler(left, right)


def _div(left: int, right: int) -> int:
    if right == 0:
        raise EvaluationError("integer division by zero")
    # C truncated integer division.
    quotient = abs(left) // abs(right)
    return -quotient if (left < 0) ^ (right < 0) else quotient


def _mod(left: int, right: int) -> int:
    if right == 0:
        raise EvaluationError("integer modulo by zero")
    # C truncated modulo: sign of result matches dividend.
    remainder = abs(left) % abs(right)
    return -remainder if left < 0 else remainder


_BINARY_HANDLERS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": _div,
    "%": _mod,
    "==": lambda a, b: 1 if a == b else 0,
    "!=": lambda a, b: 1 if a != b else 0,
    "<": lambda a, b: 1 if a < b else 0,
    "<=": lambda a, b: 1 if a <= b else 0,
    ">": lambda a, b: 1 if a > b else 0,
    ">=": lambda a, b: 1 if a >= b else 0,
}
