from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import Number, PrimitiveSchema


@dataclass(frozen=True)
class Day(PrimitiveSchema):
    inner: int

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Day":
        number = Number.from_typed_json(json_obj)
        return Day(inner=int(number.inner))
