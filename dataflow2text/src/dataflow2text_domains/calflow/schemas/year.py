from dataclasses import dataclass
from functools import total_ordering
from typing import Any, Dict

from dataflow2text.dataflow.schema import Number, PrimitiveSchema


@total_ordering
@dataclass(frozen=True)
class Year(PrimitiveSchema):
    inner: int

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Year":
        number = Number.from_typed_json(json_obj)
        return Year(inner=int(number.inner))

    def __lt__(self, other) -> bool:
        if not isinstance(other, Year):
            raise ValueError(f"Cannot compare {self} with {other}.")
        return self.inner < other.inner
