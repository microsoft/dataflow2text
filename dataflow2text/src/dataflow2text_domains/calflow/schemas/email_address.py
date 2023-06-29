from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema, String


@dataclass(frozen=True)
class EmailAddress(NullaryStructSchema):
    address: String

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "EmailAddress":
        schema = json_obj.get("schema")
        assert schema == "EmailAddress"
        underlying = json_obj.get("underlying")
        assert underlying is not None

        address = String.from_typed_json(underlying.get("address"))
        return EmailAddress(address=address)
