from dataclasses import dataclass

from dataflow2text.dataflow.schema import List, NullaryStructSchema, String
from dataflow2text_domains.calflow.schemas.attendee_partial import AttendeePartial


@dataclass(frozen=True)
class CreateRequestPartial(NullaryStructSchema):
    subject: String
    attendeesIncludes: List[AttendeePartial]
