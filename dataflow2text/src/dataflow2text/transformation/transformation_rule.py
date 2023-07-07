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

from dataclasses import dataclass
from importlib import import_module
from inspect import getmembers
from pkgutil import walk_packages
from typing import Callable, Iterator, Optional, Set

from dataflow2text.dataflow.function import BaseFunction


@dataclass(frozen=True)
class TransformationRule:
    """A transformation rule to convert a dataflow computation to another when matched."""

    name: str
    body: Callable[[BaseFunction], Optional[BaseFunction]]

    def run(self, c: BaseFunction) -> Optional[BaseFunction]:
        return self.body(c)


def transformation(func: Callable[[BaseFunction], Optional[BaseFunction]]):
    """A decorator to convert a Python function to a TransformationRule."""

    # TODO: It would be useful to validate the signature of the Python function.

    return TransformationRule(
        # TODO: Either change the type annotation of `func` or create the name properly when
        #  `func.__module__` and/or `func.__qualname__` is not defined.
        name=f"{func.__module__}.{func.__qualname__}",
        body=func,
    )


def get_transformation_rules_from_module(
    module, seen_transformations: Set[TransformationRule]
) -> Iterator[TransformationRule]:
    for _, member in getmembers(module):
        if isinstance(member, TransformationRule):
            if member in seen_transformations:
                continue
            seen_transformations.add(member)
            yield member


def get_transformation_rules(*packages) -> Iterator[TransformationRule]:
    seen_transformations: Set[TransformationRule] = set()
    for package in packages:
        for _, module_name, _ in walk_packages(
            package.__path__, prefix=package.__name__ + "."
        ):
            module = import_module(module_name)
            for schema in get_transformation_rules_from_module(
                module, seen_transformations
            ):
                yield schema
