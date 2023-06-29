from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.attendee_type import AttendeeType
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.response_status import ResponseStatus


@dataclass(frozen=True)
class Attendee(NullaryStructSchema):
    recipient: Recipient
    status: ResponseStatus
    type: AttendeeType

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Attendee":
        schema_ = json_obj.get("schema")
        assert schema_ == "Attendee"
        underlying = json_obj.get("underlying")
        assert underlying is not None

        return Attendee(
            recipient=Recipient.from_typed_json(underlying.get("recipient")),
            status=ResponseStatus.from_typed_json(underlying.get("status")),
            type=AttendeeType.from_typed_json(underlying.get("type")),
        )
