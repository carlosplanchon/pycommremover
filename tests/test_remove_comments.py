"""Tests for pycommremover."""

import ast

from pycommremover import (
    remove_comments,
    remove_comments_and_docstrings,
    remove_docstrings,
)


def _parses(src: str) -> bool:
    """True if ``src`` is syntactically valid Python."""
    try:
        ast.parse(src)
        return True
    except SyntaxError:
        return False


# --- remove_comments: line comments -----------------------------------------


def test_trailing_line_comment_is_removed():
    assert remove_comments("x = 1  # a comment") == "x = 1"


def test_full_line_comment_becomes_blank():
    assert remove_comments("# a comment\ny = 2") == "\ny = 2"


def test_hash_inside_double_quoted_string_is_kept():
    src = 'url = "http://example.com#section"'
    assert remove_comments(src) == src


def test_hash_inside_single_quoted_string_is_kept():
    src = "s = 'a # b'"
    assert remove_comments(src) == src


def test_hash_inside_call_argument_is_kept():
    src = 'print("# not a comment")'
    assert remove_comments(src) == src


def test_hash_inside_fstring_is_kept():
    src = 'label = f"value #{n}"'
    assert remove_comments(src) == src


# --- remove_comments: block comments (bare non-docstring strings) ------------


def test_standalone_block_comment_is_removed():
    src = 'x = 1\n"""a block comment"""\ny = 2'
    assert remove_comments(src) == "x = 1\n\ny = 2"


def test_block_comment_only_in_block_gets_pass():
    src = 'if cond:\n    """just a note"""'
    out = remove_comments(src)
    assert out == "if cond:\n    pass"
    assert _parses(out)


# --- remove_comments: docstrings and real strings are kept ------------------


def test_remove_comments_keeps_module_docstring():
    src = '"""Module docstring."""\nimport os'
    assert remove_comments(src) == src


def test_remove_comments_keeps_function_docstring():
    src = 'def f():\n    """doc"""\n    return 1'
    assert remove_comments(src) == src


def test_triple_quoted_assignment_is_kept():
    src = 'sql = """SELECT * FROM t"""\nx = 1'
    assert remove_comments(src) == src


def test_triple_quoted_argument_is_kept():
    src = 'run("""SELECT 1""")'
    assert remove_comments(src) == src


def test_bare_fstring_is_kept():
    # A bare f-string can have side effects, so it is never removed.
    src = 'f"""{compute()}"""'
    assert remove_comments(src) == src


# --- remove_docstrings ------------------------------------------------------


def test_module_docstring_is_removed():
    src = '"""Module docstring."""\nimport os'
    assert remove_docstrings(src) == "\nimport os"


def test_function_docstring_is_removed():
    src = 'def f():\n    """doc"""\n    return 1'
    assert remove_docstrings(src) == "def f():\n\n    return 1"


def test_class_docstring_is_removed():
    src = 'class C:\n    """doc"""\n    x = 1'
    assert remove_docstrings(src) == "class C:\n\n    x = 1"


def test_multiline_docstring_is_removed():
    src = 'def g():\n    """\n    line one\n    line two\n    """\n    return 2'
    out = remove_docstrings(src)
    assert out == "def g():\n\n\n\n\n    return 2"
    assert _parses(out)


def test_docstring_only_function_gets_pass():
    src = 'def stub():\n    """Just docs."""'
    out = remove_docstrings(src)
    assert out == "def stub():\n    pass"
    assert _parses(out)


def test_single_line_docstring_only_function_gets_pass():
    src = 'def stub(): """docs"""'
    out = remove_docstrings(src)
    assert out == "def stub(): pass"
    assert _parses(out)


def test_remove_docstrings_keeps_comments():
    src = "x = 1  # keep me"
    assert remove_docstrings(src) == src


def test_remove_docstrings_keeps_non_docstring_block_string():
    src = 'x = 1\n"""not a docstring"""'
    assert remove_docstrings(src) == src


# --- remove_comments_and_docstrings -----------------------------------------


def test_combined_removes_everything():
    src = 'def f():\n    """doc"""\n    x = 1  # c\n    """note"""\n    return x'
    out = remove_comments_and_docstrings(src)
    kept = [line for line in out.splitlines() if line.strip()]
    assert kept == ["def f():", "    x = 1", "    return x"]
    assert _parses(out)


def test_combined_stub_gets_pass():
    src = 'def stub():\n    """docs"""  # trailing'
    out = remove_comments_and_docstrings(src)
    assert out == "def stub():\n    pass"
    assert _parses(out)


# --- general properties -----------------------------------------------------


def test_code_without_comments_is_unchanged():
    src = "def add(a, b):\n    return a + b"
    assert remove_comments(src) == src
    assert remove_docstrings(src) == src


def test_remove_comments_is_idempotent():
    src = 'x = 1  # c\n"""block"""\ny = "keep # me"\n'
    once = remove_comments(src)
    assert remove_comments(once) == once


def test_composition_matches_combined():
    src = 'def f():\n    """doc"""\n    x = 1  # c\n    """note"""\n    return x'
    assert remove_comments(remove_docstrings(src)) == remove_comments_and_docstrings(
        src
    )


def test_readme_example():
    text = (
        '\nprint("First line")\n\n"""\n\nprint("Commented line.")\n\n'
        "'''\nprint(\"Commented line 2.\")\n\nprint(\"Commented line 3.\")\n\n"
        "# Single line comment 1.\n'''\n\n# Single line comment.\n"
        'print("Commented line 4.")\n\n"""\n\n# Single line comment 2.\n\n'
        'print("Commented line 5")\n'
    )
    out = remove_comments(text)
    kept = [line for line in out.splitlines() if line.strip()]
    assert kept == ['print("First line")', 'print("Commented line 5")']
