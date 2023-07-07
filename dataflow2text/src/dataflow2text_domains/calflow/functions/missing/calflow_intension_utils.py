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
from typing import TypeVar

from dataflow2text.dataflow.function import BaseFunction, function
from dataflow2text.dataflow.schema import BaseSchema, TSchema
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.errors.unable_to_implement_error import (
    UnableToImplementError,
)
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.path import Path

_T = TypeVar("_T", bound=BaseSchema)
_R = TypeVar("_R", bound=BaseSchema)


@function
def ReviseConstraint(
    rootLocation: CalflowIntension[_R],
    oldLocation: Constraint[CalflowIntension[Constraint[_T]]],
    new: Constraint[_T],
) -> CalflowIntension[_R]:
    raise UnableToImplementError()


@function
def cursorNext(
    constraint: Constraint[CalflowIntension[_T]],
) -> Constraint[CalflowIntension[_T]]:
    raise UnableToImplementError()


@function
def cursorPrevious(
    constraint: Constraint[CalflowIntension[_T]],
) -> Constraint[CalflowIntension[_T]]:
    raise UnableToImplementError()


@function
def PathAndTypeConstraint(
    path: Path, constraint: Constraint[CalflowIntension[_T]]
) -> Constraint[CalflowIntension[_T]]:
    raise UnableToImplementError()


@dataclass(frozen=True)
class ConstraintTypeIntension(
    BaseFunction[Constraint[CalflowIntension[Constraint[TSchema]]]]
):
    type_arg: TypeName

    def _call_impl(self) -> Constraint[CalflowIntension[Constraint[TSchema]]]:
        raise UnableToImplementError()

    def reveal_type(self) -> TypeName:
        return Constraint.dtype_ctor(
            CalflowIntension.dtype_ctor(Constraint.dtype_ctor(self.type_arg))
        )
