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
