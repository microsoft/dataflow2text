from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.event import Event


@dataclass(frozen=True)
class CreateEventResponse(NullaryStructSchema):
    item: Event

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "CreateEventResponse":
        schema = json_obj.get("schema")
        assert schema == "CreateEventResponse"
        underlying = json_obj.get("underlying")

        return CreateEventResponse(item=Event.from_typed_json(underlying.get("item")))
