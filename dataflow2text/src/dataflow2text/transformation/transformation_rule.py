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
