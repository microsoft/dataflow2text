from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, TComparableSchema, TSchema


@function
def IsGreaterThan(x: TComparableSchema, y: TComparableSchema) -> Boolean:
    return Boolean(x > y)


@function
def IsLessThan(x: TComparableSchema, y: TComparableSchema) -> Boolean:
    return Boolean(x < y)


@function
def IsGreaterEqual(x: TComparableSchema, y: TComparableSchema) -> Boolean:
    return Boolean(x >= y)


@function
def IsLessEqual(x: TComparableSchema, y: TComparableSchema) -> Boolean:
    return Boolean(x <= y)


@function
def IsEqual(x: TSchema, y: TSchema) -> Boolean:
    return Boolean(x == y)
