from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema, String


@dataclass(frozen=True)
class PersonName(NullaryStructSchema):
    name: String

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "PersonName":
        schema = json_obj.get("schema")
        assert schema == "PersonName"

        underlying = json_obj.get("underlying")
        assert isinstance(underlying, str)

        return PersonName(name=String(underlying))
