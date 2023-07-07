# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from typing import Any, Callable, Iterable, Iterator, Optional, Sequence, TypeVar

_A = TypeVar("_A")
_N = TypeVar("_N", int, float)
_T1 = TypeVar("_T1")


def identity(x: _A) -> _A:
    """Returns `x`."""
    return x


def mean(xs: Iterable[_N]) -> float:
    """Numerically-stable streaming average. O(1) memory."""
    result = 0.0
    for n, x in enumerate(iter(xs)):
        d = 1 / (1 + n)
        result += x * d - result * d
    return result


class IteratorGenerator(Iterable[_T1]):
    """
    A wrapper around a function that returns an iterator. Calling iter() on
    one of these allows you to "reset" the iterator returned by the function.
    """

    def __init__(self, f: Callable[[], Iterator[_T1]]):
        self.f = f

    def __iter__(self) -> Iterator[_T1]:
        yield from self.f()


def bisect_right(
    lst: Sequence[_A],
    elem: _A,
    key: Callable[[_A], Any] = identity,
    begin: int = 0,
    end: Optional[int] = None,
):
    """Similar to bisect.bisect_right in the standard library, but with a key function.

    Locates the insertion point for `elem` in `lst` to maintain sorted order.
    If `elem` is already present in `lst`, then the insertion point will be after (to the right of) any existing entries.

    The `key` argument has the same meaning as that of `max`, `min`, and `sorted` in the standard library.
    When we need to compare two elements `x` and `y`, we compare `key(x)` and `key(y)`.
    """
    assert begin >= 0
    if end is None:
        end = len(lst)
    else:
        assert end <= len(lst)

    while begin < end:
        mid = (begin + end) // 2
        if key(elem) < key(lst[mid]):
            end = mid
        else:
            begin = mid + 1
    return begin
