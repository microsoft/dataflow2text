from dataclasses import dataclass
from typing import Generic

from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.dataflow.schema import TSchema, Unit
from dataflow2text.dataflow.type_name import TypeName

@dataclass
class Yield(Generic[TSchema], BaseFunction[Unit]):
    output: BaseFunction[TSchema]
    def _call_impl(self) -> Unit: ...
    def reveal_type(self) -> TypeName: ...
