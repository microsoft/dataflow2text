from typing import Generic, Optional

from dataflow2text.dataflow.schema import BaseSchema, TSchema
from dataflow2text.dataflow.type_name import TypeName


class CalflowIntension(Generic[TSchema], BaseSchema):
    def __init__(self, underlying: Optional[TSchema]):
        self._underlying: Optional[TSchema] = underlying

    @property
    def underlying(self) -> Optional[TSchema]:
        return self._underlying

    @property
    def dtype(self) -> TypeName:
        return self.dtype_ctor(self._underlying.dtype)
