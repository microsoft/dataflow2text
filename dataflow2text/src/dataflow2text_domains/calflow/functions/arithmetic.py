from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Number


@function
def Plus(x: Number, y: Number) -> Number:
    return Number(x.inner + y.inner)


@function
def Minus(x: Number, y: Number) -> Number:
    return Number(x.inner - y.inner)
