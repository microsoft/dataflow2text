from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)


@dataclass(frozen=True)
class ResponseStatus(NullaryStructSchema):
    response: ResponseStatusType

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "ResponseStatus":
        schema = json_obj.get("schema")
        assert schema == "ResponseStatus"
        underlying = json_obj.get("underlying")
        assert underlying is not None

        return ResponseStatus(
            response=ResponseStatusType.from_typed_json(underlying.get("response"))
        )
