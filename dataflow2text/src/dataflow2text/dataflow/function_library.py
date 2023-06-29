import itertools
from importlib import import_module
from inspect import getmembers, isclass
from pkgutil import walk_packages
from typing import Dict, Iterable, Iterator, Optional, Set, Type

from dataflow2text.dataflow.function import (
    BaseFunction,
    BooleanCtor,
    EmptyListCtor,
    EmptyOptionCtor,
    Get,
    GetAttr,
    ListCtor,
    LongCtor,
    NumberCtor,
    OptionCtor,
    StringCtor,
    ValueCtor,
)
from dataflow2text.dataflow.library_utils import safe_build_dict


class FunctionLibrary:
    def __init__(self, functions: Iterable[Type[BaseFunction]]):
        self._functions: Dict[str, Type[BaseFunction]] = safe_build_dict(
            functions, lambda x: x.__name__
        )

    def get(self, key: str) -> Optional[Type[BaseFunction]]:
        """Returns the dataflow function for the given `key`."""
        return self._functions.get(key)

    def __add__(self, other):
        if not isinstance(other, FunctionLibrary):
            raise ValueError(f"Cannot add {self} with {other}.")

        return FunctionLibrary(
            itertools.chain(self._functions.values(), other._functions.values())
        )


BUILTIN_FUNCTION_LIBRARY = FunctionLibrary(
    [
        ValueCtor,
        GetAttr,
        Get,
        StringCtor,
        BooleanCtor,
        LongCtor,
        NumberCtor,
        ListCtor,
        EmptyListCtor,
        OptionCtor,
        EmptyOptionCtor,
    ]
)


def get_functions(*packages) -> Iterator[Type[BaseFunction]]:
    seen_functions: Set[Type[BaseFunction]] = set()
    for package in packages:
        for _, module_name, _ in walk_packages(
            package.__path__, prefix=package.__name__ + "."
        ):
            module = import_module(module_name)
            for schema in _get_functions_from_module(module, seen_functions):
                yield schema


def _get_functions_from_module(module, seen_functions) -> Iterator[Type[BaseFunction]]:
    for _, member in getmembers(module):
        if isclass(member):
            if member in seen_functions:
                continue
            seen_functions.add(member)

            if issubclass(member, BaseFunction):
                yield member
