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

import itertools
import typing
from importlib import import_module
from inspect import getmembers, isclass
from pkgutil import walk_packages
from typing import Dict, Generic, Iterable, Iterator, Optional, Set, Type, Union

from dataflow2text.dataflow.library_utils import safe_build_dict
from dataflow2text.dataflow.schema import (
    BaseSchema,
    Boolean,
    Dynamic,
    List,
    Long,
    Number,
    Option,
    String,
    Unit,
)
from dataflow2text.dataflow.type_name import TypeName

# pylint: disable=protected-access
BoundSchema = Union[Type[BaseSchema], typing._GenericAlias]  # type: ignore


class SchemaLibrary:
    def __init__(self, schemas: Iterable[Type[BaseSchema]]):
        self._schemas: Dict[str, Type[BaseSchema]] = safe_build_dict(
            schemas, lambda x: x.dtype_base()
        )

    def get(self, type_name: TypeName) -> Optional[BoundSchema]:
        """Returns the concrete schema of the given `type_name`.

        The base and type args of the `type_name` are bound to concrete schemas.
        When the `type_name` has non-empty type args, a `typing._GenericAlias` (e.g., `List[String]`) is returned.
        Otherwise, a schema class is returned.

        We may consider using `pkgutil.resolve_name` and rename this method to `resolve`, i.e., it resolves a TypeName
        to a concrete schema.
        """

        base_schema = self.get_base(type_name)
        if base_schema is None:
            return None

        if len(type_name.type_args) == 0:
            return base_schema

        # Ignore mypy check. See https://github.com/python/typeshed/issues/3983
        assert issubclass(base_schema, Generic), base_schema  # type: ignore

        arg_schemas = []
        for type_arg in type_name.type_args:
            arg_schema = self.get(type_arg)
            if arg_schema is None:
                return None
            arg_schemas.append(arg_schema)

        # See `Generic.__class_getitem__`, which returns a `typing._GenericAlias`.
        return base_schema[tuple(arg_schemas)]  # type: ignore

    def get_base(self, type_name: TypeName) -> Optional[Type[BaseSchema]]:
        """Returns the schema for the base of the given `type_name`."""

        return self._schemas.get(type_name.base)

    def __add__(self, other):
        if not isinstance(other, SchemaLibrary):
            raise ValueError(f"Cannot add {self} with {other}.")

        return SchemaLibrary(
            itertools.chain(self._schemas.values(), other._schemas.values())
        )


BUILTIN_SCHEMA_LIBRARY = SchemaLibrary(
    [Unit, String, Boolean, Long, Number, Option, List, Dynamic]
)


def get_schemas(package) -> Iterator[Type[BaseSchema]]:
    seen_schemas: Set[Type[BaseSchema]] = set()
    for _, module_name, _ in walk_packages(
        package.__path__, prefix=package.__name__ + "."
    ):
        module = import_module(module_name)
        for _, member in getmembers(module):
            if isclass(member) and issubclass(member, BaseSchema):
                if member in seen_schemas:
                    continue
                seen_schemas.add(member)
                yield member
