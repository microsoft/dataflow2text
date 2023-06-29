from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long


@function
def NumberOrdinal(number: Long) -> Long:
    raise NotImplementedError()
