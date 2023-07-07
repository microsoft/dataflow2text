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

from dataflow2text.dataflow.function import BaseFunction, function
from dataflow2text.dataflow.schema import TSchema
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.path import Path


@function
def intension(extension: TSchema) -> CalflowIntension[TSchema]:
    return CalflowIntension(underlying=extension)


@function
def extensionConstraint(
    constraint: Constraint[TSchema],
) -> Constraint[CalflowIntension[TSchema]]:
    def predicate(x: CalflowIntension[TSchema]) -> bool:
        return constraint.allows(x.underlying)

    return Constraint(
        type_arg=CalflowIntension.dtype_ctor(constraint.type_arg),
        underlying=predicate,
    )


# pylint: disable=redefined-outer-name
@function
def Execute(intension: CalflowIntension[TSchema]) -> TSchema:
    if intension.underlying is None:
        raise ValueError(f"{intension.underlying} cannot be None.")

    return intension.underlying


@function
def QueryEventIntensionConstraint() -> Constraint[CalflowIntension[Constraint[Event]]]:
    pass


@dataclass(frozen=True)
class ActionIntensionConstraint(BaseFunction[Constraint[CalflowIntension[TSchema]]]):
    type_arg: TypeName

    def _call_impl(self):
        pass

    def reveal_type(self) -> TypeName:
        return Constraint.dtype_ctor(CalflowIntension.dtype_ctor(self.type_arg))


@dataclass(frozen=True)
class roleConstraint(BaseFunction[Constraint[CalflowIntension[TSchema]]]):
    """Returns a constraint of an intension.

    In Lispress/Express, the signature is
        def roleConstraint(path: Path): T

    In Python, we have to pass the type arg as an argument to the computation.
    Therefore, we cannot use the `@function` decorator.
    """

    type_arg: TypeName
    path: BaseFunction[Path]

    def _call_impl(self):
        def predicate(x: CalflowIntension[TSchema]) -> bool:
            return True

        return Constraint(
            type_arg=CalflowIntension.dtype_ctor(self.type_arg),
            underlying=predicate,
        )

    def reveal_type(self) -> TypeName:
        return Constraint.dtype_ctor(CalflowIntension.dtype_ctor(self.type_arg))
