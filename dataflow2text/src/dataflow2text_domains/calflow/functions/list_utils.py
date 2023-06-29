"""Helper functions for list."""
from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import List, Long, TSchema
from dataflow2text_domains.calflow.errors.calflow_runtime_error import (
    EmptyListError,
    ListIndexTooLargeError,
    NonSingletonListError,
)


@function
def singleton(
    # pylint: disable=redefined-builtin
    list: List[TSchema],
) -> TSchema:
    length = len(list)
    if length == 0:
        raise EmptyListError()

    if length > 1:
        raise NonSingletonListError()

    return list[0]


@function
def size(
    # pylint: disable=redefined-builtin
    list: List[TSchema],
) -> Long:
    return Long(len(list))


@function
def append(x: List[TSchema], y: TSchema) -> List[TSchema]:
    assert x.type_arg == y.dtype
    return List(type_arg=y.dtype, inner=x.inner + [y])


@function
def head(x: List[TSchema]) -> TSchema:
    if len(x) == 0:
        raise EmptyListError()

    return x[0]


@function
def tail(x: List[TSchema]) -> List[TSchema]:
    if len(x) == 0:
        raise EmptyListError()

    return List(type_arg=x.type_arg, inner=x.inner[1:])


@function
def last(x: List[TSchema]) -> TSchema:
    if len(x) == 0:
        raise EmptyListError()

    return x[-1]


@function
def get(x: List[TSchema], n: Long) -> TSchema:
    if len(x) <= n.inner:
        raise ListIndexTooLargeError(n.inner)

    return x[n.inner]


@function
def take(x: List[TSchema], n: Long) -> List[TSchema]:
    return List(type_arg=x.type_arg, inner=x.inner[: n.inner])


@function
def takeRight(x: List[TSchema], n: Long) -> List[TSchema]:
    offset = -n.inner
    return List(type_arg=x.type_arg, inner=x.inner[offset:])
