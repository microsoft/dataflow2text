from dataclasses import dataclass

from dataflow2text.dataflow.schema import List, Long, NullaryStructSchema, String
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.time import Time


@dataclass(frozen=True)
class FindMeetingTimesServiceRequest(NullaryStructSchema):
    attendees: List[Attendee]
    timeRanges: List[Constraint[Time]]
    meetingDuration: String
    minimumAttendeePercentage: Long
    locationConstraint: String
    maxCandidates: Long
