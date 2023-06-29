from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class AttendeeType(PrimitiveSchema):
    inner: str

    @classmethod
    def Required(cls):
        return cls("Required")

    @classmethod
    def Optional(cls):
        return cls("Optional")

    @classmethod
    def Resource(cls):
        return cls("Resource")

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "AttendeeType":
        schema_ = json_obj.get("schema")
        assert schema_ == "AttendeeType"
        underlying = json_obj.get("underlying")

        if underlying == "Required":
            return AttendeeType.Required()

        if underlying == "Optional":
            return AttendeeType.Optional()

        if underlying == "Resource":
            return AttendeeType.Resource()

        raise ValueError(f"Unknown attendee type: {underlying}")
