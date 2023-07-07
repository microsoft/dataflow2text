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
from typing import Callable, Generic

from dataflow2text.dataflow.schema import (
    BaseSchema,
    Interval,
    TComparableSchema,
    TSchema,
)
from dataflow2text.dataflow.type_name import TypeName


@dataclass
class Constraint(Generic[TSchema], BaseSchema):
    """The schema for constraints.

    Note we cannot use `@dataclass(frozen=True)` the type of `underlying` is Callable.
    See https://github.com/python/mypy/issues/5485#issuecomment-888953325
    """

    type_arg: TypeName
    underlying: Callable[[TSchema], bool]

    def allows(self, value: TSchema) -> bool:
        return self.underlying(value)  # type: ignore

    @property
    def dtype(self):
        return self.dtype_ctor(self.type_arg)


class WithinIntervalConstraint(
    Generic[TComparableSchema], Constraint[TComparableSchema]
):
    """The schema for constraints that check whether a value is within the interval.

    Note this schema's dataflow type is still `Constraint[T]` instead of `WithinIntervalConstraint[T]`
    since dataflow does not allow subtyping.

    TODO: Currently this schema is not used. We may want to replace the *RangeConstraint with this schema in future.
    """

    def __init__(self, interval: Interval[TComparableSchema]):
        def predicate(x: TComparableSchema) -> bool:
            return interval.lower <= x <= interval.upper

        self.interval = interval
        super().__init__(type_arg=self.interval.dtype, underlying=predicate)

    @classmethod
    def dtype_ctor(cls, *type_args: TypeName) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(*type_args)

    @property
    def dtype(self) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(self.interval.dtype)
