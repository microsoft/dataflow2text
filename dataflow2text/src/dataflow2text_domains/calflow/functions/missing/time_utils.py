from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.schemas.time import Time


@function
def Breakfast() -> Time:
    raise NotImplementedError()


@function
def Dinner() -> Time:
    raise NotImplementedError()


@function
def Midnight() -> Time:
    raise NotImplementedError()
