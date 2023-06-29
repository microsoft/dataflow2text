from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.attendee_type import AttendeeType
from dataflow2text_domains.calflow.schemas.person_name import PersonName


@dataclass(frozen=True)
class AttendeePartial(NullaryStructSchema):
    name: PersonName
    type: AttendeeType
