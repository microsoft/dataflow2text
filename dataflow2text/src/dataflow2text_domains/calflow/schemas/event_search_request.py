from dataclasses import dataclass

from dataflow2text.dataflow.schema import (
    Boolean,
    List,
    NullaryStructSchema,
    Number,
    Option,
    String,
)
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.time_zone import TimeZone


@dataclass(frozen=True)
class EventSearchRequest(NullaryStructSchema):
    timeZone: TimeZone
    subject: String
    attendees: List[Attendee]
    start: Option[DateTime]
    end: Option[DateTime]
    sort: Option[Boolean]
    limit: Option[Number]
    isOneOnOne: Boolean
    isAllDay: Boolean
    allowCancelled: Boolean
