# pigeon

Zero-dependency POSIX gettext-style `Plural-Forms` parser and evaluator.

`pigeon` is for `.po`/`.mo` tooling, translation checks, and any place where you
need to evaluate the C-like plural expression stored in a gettext header. It is
not a CLDR plural-rules implementation.

## Install

From a repository checkout:

```bash
python -m pip install -e .
```

## Quick Start

```python
import pigeon

compiled = pigeon.parse("nplurals=2; plural=(n != 1);")

compiled.nplurals        # 2
compiled.evaluate(1)     # 0
compiled.evaluate(7)     # 1

pigeon.select("ru", 21)  # 0
pigeon.select("ru", 5)   # 2
```

## API

- `parse(header)` parses a full `Plural-Forms` header.
- `parse_expression(expr)` parses just the plural expression.
- `evaluate(compiled, n)` returns the plural index for a compiled form.
- `select(locale, n)` evaluates a built-in locale rule.
- `forms_for(locale)` returns the built-in header for a locale.
- `available_locales()` lists built-in locale keys.
- `PluralFormError`, `ParseError`, `EvaluationError`, and
  `UnknownLocaleError` make failure modes explicit.

## Grammar

The parser implements the C-style subset accepted by GNU gettext:
integer literals, the operand `n`, `! + - * / % == != < <= > >= && ||`,
parentheses, and ternary `cond ? then : else` expressions.

CLDR categories such as `zero`, `one`, `few`, `many`, decimal operands, and
language-specific rule synthesis are outside this library's scope.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## License

MIT - see [LICENSE](./LICENSE).
