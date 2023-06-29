from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long, Number


@function
def Earliest() -> Long:
    return Long(1)


@function
def Latest() -> Long:
    return Long(-1)


@function
def BottomResult() -> Long:
    return Long(-1)


@function
def TopResult() -> Long:
    return Long(1)


@function
def Acouple() -> Long:
    return Long(2)


@function
def Afew() -> Long:
    return Long(3)


@function
def longToNum(long: Long) -> Number:
    return Number(long.inner)
