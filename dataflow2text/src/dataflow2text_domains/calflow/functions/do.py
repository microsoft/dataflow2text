from typing import TypeVar

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import BaseSchema

_T = TypeVar("_T", bound=BaseSchema)
_R = TypeVar("_R", bound=BaseSchema)


@function
def do(arg1: _T, arg2: _R) -> _R:
    return arg2
