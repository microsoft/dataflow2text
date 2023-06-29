import fnmatch
from typing import Iterator

from importlib_resources.abc import Traversable


def find_all_matching(
    root: Traversable, pattern: str, recursive: bool = True
) -> Iterator[Traversable]:
    """Returns all files under `root` which match `pattern`.

    `pattern` is a glob-style pattern used by `fnmatch`.
    If `recursive` is True, the search will be performed recursively in all subdirectories.
    """
    assert root.is_dir()
    stack = list(root.iterdir())

    while stack:
        node = stack.pop()
        if node.is_file() and fnmatch.fnmatch(node.name, pattern):
            yield node
        if recursive and node.is_dir():
            stack.extend(node.iterdir())
