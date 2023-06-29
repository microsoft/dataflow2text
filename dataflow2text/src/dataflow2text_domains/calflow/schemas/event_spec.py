from dataclasses import dataclass

from dataflow2text.dataflow.schema import List, NullaryStructSchema, String
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase


@dataclass(frozen=True)
class EventSpec(NullaryStructSchema):
    subject: String
    start: DateTime
    end: DateTime
    location: LocationKeyphrase
    attendees: List[Attendee]
