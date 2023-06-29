# The filename is `calflow_yield.py` since `yield.py` is not allowed.
from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import TSchema, Unit


@function
def Yield(output: TSchema) -> Unit:
    return Unit()
