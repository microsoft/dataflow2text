from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class EventId(PrimitiveSchema):
    inner: str

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "EventId":
        schema_ = json_obj.get("schema")
        assert schema_ == "EventId"
        underlying = json_obj.get("underlying")
        assert isinstance(underlying, str)
        return EventId(inner=underlying)
