# pycommremover

[![CI](https://github.com/carlosplanchon/pycommremover/actions/workflows/ci.yml/badge.svg)](https://github.com/carlosplanchon/pycommremover/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pycommremover.svg)](https://pypi.org/project/pycommremover/)
[![Python versions](https://img.shields.io/pypi/pyversions/pycommremover.svg)](https://pypi.org/project/pycommremover/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/carlosplanchon/pycommremover)

*Python library to remove comments and docstrings from Python source code.*

It analyses the code with the standard-library `tokenize` and `ast` modules,
so a `#` inside a string is never mistaken for a comment and real string
values (assignments, call arguments, f-strings) are never touched. Line
numbers of the remaining code are preserved.

## Why three functions?
At the language level these are different things, so they are removed
separately:

| Construct | Example | Runtime effect | Removed by |
|---|---|---|---|
| **Line comment** | `x = 1  # note` | none (discarded by the tokenizer) | `remove_comments` |
| **Block comment** | a lone `"""note"""` statement | none (a discarded no-op) | `remove_comments` |
| **Docstring** | first string of a module/class/function | kept as `__doc__`, seen by `help()`/`doctest` | `remove_docstrings` |

`remove_comments` is **behaviour-preserving** (it only deletes no-ops and
keeps docstrings). `remove_docstrings` changes `__doc__`, so it is opt-in.
`remove_comments_and_docstrings` does both in one pass.

When removing a string that is a block's only statement (e.g. `def f():
"""doc"""`), a `pass` is inserted so the result stays valid Python.

## Installation
### Install with uv:
```
uv add pycommremover
```

## Usage
```python
import pycommremover

src = '''
def greet(name):
    """Return a greeting."""          # docstring: kept by remove_comments
    msg = f"Hi, {name}"  # build it   # line comment: removed
    """a block comment"""             # block comment: removed
    return msg
'''

# Line + block comments gone, docstring kept:
print(pycommremover.remove_comments(src))

# Only the docstring gone:
print(pycommremover.remove_docstrings(src))

# Everything gone:
print(pycommremover.remove_comments_and_docstrings(src))
```

The input must be syntactically valid Python.

## Development
The `dev` dependency group (installed automatically by `uv run`) provides pytest:
```
uv run pytest
```
