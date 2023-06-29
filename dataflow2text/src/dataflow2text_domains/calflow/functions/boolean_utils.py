from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean


@function
def Or(x: Boolean, y: Boolean) -> Boolean:
    return Boolean(x.inner or y.inner)


@function
def And(x: Boolean, y: Boolean) -> Boolean:
    return Boolean(x.inner or y.inner)


@function
def Not(x: Boolean) -> Boolean:
    return Boolean(not x.inner)
