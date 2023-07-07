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

from typing import TypeVar

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import BaseSchema
from dataflow2text_domains.calflow.errors.unable_to_implement_error import (
    UnableToImplementError,
)
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint

_T = TypeVar("_T", bound=BaseSchema)
_R = TypeVar("_R", bound=BaseSchema)


@function
def NewClobber(
    intension: CalflowIntension[_R],
    slotConstraint: Constraint[CalflowIntension[_T]],
    value: CalflowIntension[_T],
) -> CalflowIntension[_R]:
    raise UnableToImplementError()


@function
def refer(constraint: Constraint[CalflowIntension[_T]]) -> CalflowIntension[_T]:
    raise UnableToImplementError()


@function
def ClobberWrapper(
    oldLocation: Constraint[CalflowIntension[Constraint[_T]]], new: Constraint[_T]
) -> _R:  # type: ignore
    raise UnableToImplementError()


@function
def NewClobberWrapper(oldArg: Constraint[CalflowIntension[_T]], newArg: _T) -> _R:  # type: ignore
    raise UnableToImplementError()
