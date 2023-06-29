from dataclasses import dataclass

from dataflow2text.dataflow.schema import Boolean, List, NullaryStructSchema
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.time import Time
from dataflow2text_domains.calflow.schemas.time_zone import TimeZone


@dataclass(frozen=True)
class FindMeetingTimesApiRequest(NullaryStructSchema):
    attendees: List[Attendee]
    timeRanges: List[Constraint[Time]]
    duration: Duration
    timeZome: TimeZone
    workingHoursFlag: Boolean
    now: DateTime
