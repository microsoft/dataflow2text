from dataclasses import dataclass
from typing import Generic, TypeVar

from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.dataflow.schema import BaseSchema, TSchema
from dataflow2text.dataflow.type_name import TypeName

_T = TypeVar("_T", bound=BaseSchema)
_R = TypeVar("_R", bound=BaseSchema)

@dataclass
class do(Generic[_T, _R], BaseFunction[_R]):
    arg1: BaseFunction[_T]
    arg2: BaseFunction[_R]
    def _call_impl(self) -> _R: ...
    def reveal_type(self) -> TypeName: ...
