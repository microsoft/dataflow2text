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

# Adapted from https://stackoverflow.com/posts/2912455/revisions,
# but with type annotations added.
from typing import Any, Callable, DefaultDict, Iterable, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class KeyDefaultDict(DefaultDict[K, V]):
    """
    A version of defaultdict whose factory function that constructs a
    default value for a missing key takes that key as an argument.

    >>> d: KeyDefaultDict[int, str] = KeyDefaultDict(lambda k: "/" + str(k) + "/", {0: "zero"})
    >>> d[3] = 'three'
    >>> d[0]
    'zero'
    >>> d[3]
    'three'
    >>> d[4]
    '/4/'
    >>> dict(d)
    {0: 'zero', 3: 'three', 4: '/4/'}
    """

    def __init__(self, default_factory: Callable[[K], V], *args: Any, **kwargs: Any):
        super().__init__(None, *args, **kwargs)
        # store the default_factory in an attribute of a different name, to avoid an inheritance type error
        self.default_key_factory = default_factory

    def __missing__(self, key: K) -> V:
        """
        Overrides the central method of `defaultdict` with one that calls
        `default_key_factory` on `key` instead of calling `default_factory`
        on 0 args.
        """
        if self.default_key_factory is None:
            raise KeyError(key)
        ret = self[key] = self.default_key_factory(key)
        return ret

    def __repr__(self) -> str:
        """Prints `default_key_factory` instead of `default_factory`."""
        return f"{self.__class__.__name__}({self.default_key_factory}, {dict.__repr__(self)})"

    # pylint: disable=useless-super-delegation
    # To avoid E1136 (unsubscriptable-object) pylint errors at call sites
    def __getitem__(self, item: K) -> V:
        return super().__getitem__(item)

    # pylint: disable=useless-super-delegation
    # To avoid E1136 (unsubscriptable-object) pylint errors at call sites
    def __setitem__(self, key: K, value: V) -> None:
        return super().__setitem__(key, value)

    # pylint: disable=useless-super-delegation
    def items(self) -> Iterable[Tuple[K, V]]:  # type: ignore
        return super().items()
