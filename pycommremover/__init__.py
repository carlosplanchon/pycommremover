#!/usr/bin/env python3
"""Remove comments and docstrings from Python source code.

At the language level these are three different constructs, so the library
keeps them apart:

* **Line comments** -- ``#`` comments. The tokenizer discards them; no runtime
  effect.
* **Block comments** -- bare triple-quoted string statements that are *not*
  docstrings. Python has no block-comment syntax, so a lone string is the
  idiom; it evaluates to a discarded no-op.
* **Docstrings** -- the string literal in the first statement of a module,
  class or function. Unlike the two above it survives into ``__doc__`` and is
  visible to ``help()``, ``doctest`` and IDEs.

:func:`remove_comments` deletes line and block comments only (both no-ops), so
it is behaviour-preserving and keeps docstrings. :func:`remove_docstrings`
deletes docstrings and therefore *does* change ``__doc__``.
:func:`remove_comments_and_docstrings` does both in a single pass.

Correctness comes from analysing the source with the standard-library
``tokenize`` and ``ast`` modules: a ``#`` inside a string is never mistaken
for a comment, and a real string value (an assignment, a call argument, an
f-string) is never removed. The input must be syntactically valid Python.
"""

import ast
import io
import tokenize


__all__ = [
    "remove_comments",
    "remove_docstrings",
    "remove_comments_and_docstrings",
]


# (start_row, start_col, end_row, end_col); rows are 1-indexed, cols 0-indexed,
# matching what both ``tokenize`` and ``ast`` report.
Span = tuple[int, int, int, int]

# AST nodes whose first statement may be a docstring.
_DOCSTRING_OWNERS = (
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
)


def _comment_spans(text: str) -> list[Span]:
    """Span of every ``#`` line comment."""
    spans: list[Span] = []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.COMMENT:
            spans.append((*tok.start, *tok.end))
    return spans


def _is_string_statement(node: ast.AST) -> bool:
    """True if ``node`` is a bare string-literal statement."""
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def _string_removals(
    text: str, *, docstrings: bool | None
) -> tuple[list[Span], list[tuple[int, int]]]:
    """Find the bare string statements to remove.

    ``docstrings`` selects which ones: ``True`` only docstrings, ``False`` only
    non-docstring block comments, ``None`` every bare string statement.

    Returns the spans to blank out and the ``(row, col)`` positions where a
    ``pass`` must be inserted -- those are strings whose removal would leave an
    otherwise empty block (``def f(): "doc"``), which would be a syntax error.
    """
    tree = ast.parse(text)

    doc_ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, _DOCSTRING_OWNERS):
            if node.body and _is_string_statement(node.body[0]):
                doc_ids.add(id(node.body[0]))

    spans: list[Span] = []
    remove_ids: set[int] = set()
    for node in ast.walk(tree):
        if not _is_string_statement(node):
            continue
        if docstrings is not None and (id(node) in doc_ids) != docstrings:
            continue
        remove_ids.add(id(node))
        value = node.value
        spans.append(
            (value.lineno, value.col_offset, value.end_lineno, value.end_col_offset)
        )

    pass_positions: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            continue  # an empty module is still valid; no ``pass`` needed.
        for _field, value in ast.iter_fields(node):
            if (
                isinstance(value, list)
                and len(value) == 1
                and isinstance(value[0], ast.stmt)
                and id(value[0]) in remove_ids
            ):
                stmt = value[0]
                pass_positions.append((stmt.lineno, stmt.col_offset))

    return spans, pass_positions


def _apply(
    text: str,
    spans: list[Span],
    pass_positions: list[tuple[int, int]],
) -> str:
    """Blank ``spans``, insert ``pass`` where needed, then trim dead line ends.

    A line is ``rstrip``-ped only when a removal reached its end -- that is the
    only whitespace we made dead. Anything we did not blank is returned
    verbatim, so trailing whitespace *inside* a preserved (multi-line) string
    is never altered, even when the removal shares the line via ``;``.
    """
    lines = text.split("\n")
    rstrip_rows: set[int] = set()

    for srow, scol, erow, ecol in spans:
        for row in range(srow, erow + 1):
            line = lines[row - 1]
            start = scol if row == srow else 0
            end = ecol if row == erow else len(line)
            lines[row - 1] = line[:start] + " " * (end - start) + line[end:]
            if end == len(line):  # removal reached the end of the line
                rstrip_rows.add(row)

    # After blanking, the string's characters are spaces; drop ``pass`` in.
    for row, col in pass_positions:
        line = lines[row - 1]
        lines[row - 1] = line[:col] + "pass" + line[col + 4:]
        rstrip_rows.add(row)

    return "\n".join(
        line.rstrip() if row in rstrip_rows else line
        for row, line in enumerate(lines, start=1)
    )


def remove_comments(text: str) -> str:
    """Return ``text`` with line and block comments removed, docstrings kept.

    Behaviour-preserving: only ``#`` comments and non-docstring string
    statements -- both no-ops at runtime -- are deleted. Line numbers of the
    remaining code are preserved.
    """
    spans, passes = _string_removals(text, docstrings=False)
    return _apply(text, _comment_spans(text) + spans, passes)


def remove_docstrings(text: str) -> str:
    """Return ``text`` with docstrings removed, comments kept.

    This changes ``__doc__`` (and what ``help()``/``doctest`` see), which is
    why it is separate from :func:`remove_comments`.
    """
    spans, passes = _string_removals(text, docstrings=True)
    return _apply(text, spans, passes)


def remove_comments_and_docstrings(text: str) -> str:
    """Return ``text`` with comments, block comments and docstrings removed.

    A single-pass equivalent of applying both :func:`remove_comments` and
    :func:`remove_docstrings`.
    """
    spans, passes = _string_removals(text, docstrings=None)
    return _apply(text, _comment_spans(text) + spans, passes)
