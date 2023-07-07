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

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, List, Number, TSchema
from dataflow2text_domains.calflow.schemas.constraint import Constraint


@function
def andConstraint(
    c1: Constraint[TSchema], c2: Constraint[TSchema]
) -> Constraint[TSchema]:
    def predicate(x: TSchema) -> bool:
        return c1.allows(x) and c2.allows(x)

    return Constraint(type_arg=c1.type_arg, underlying=predicate)


@function
def orConstraint(
    constraint1: Constraint[TSchema], constraint2: Constraint[TSchema]
) -> Constraint[TSchema]:
    def predicate(x: TSchema) -> bool:
        return constraint1.allows(x) or constraint2.allows(x)

    return Constraint(type_arg=constraint1.type_arg, underlying=predicate)


@function
def allows(constraint: Constraint[TSchema], value: TSchema) -> Boolean:
    return Boolean(inner=constraint.allows(value))


@function
def negate(constraint: Constraint[TSchema]) -> Constraint[TSchema]:
    def predicate(x: TSchema) -> bool:
        return not constraint.allows(x)

    return Constraint(type_arg=constraint.type_arg, underlying=predicate)


@function
def exists(constraint: Constraint[TSchema]) -> Constraint[List[TSchema]]:
    def predicate(x: List[TSchema]) -> bool:
        for item in x.inner:
            if constraint.allows(item):
                return True
        return False

    return Constraint(
        type_arg=List.dtype_ctor(constraint.type_arg), underlying=predicate
    )


@function
def listSize(
    constraint: Constraint[Number], typeConstraint: Constraint[List[TSchema]]
) -> Constraint[List[TSchema]]:
    def predicate(x: List[TSchema]) -> bool:
        return constraint.allows(Number(inner=len(x.inner)))

    return Constraint(type_arg=typeConstraint.type_arg, underlying=predicate)
