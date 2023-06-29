from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.response_status import ResponseStatus
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)


@function
def AttendeeFromEvent(event: Event, recipient: Recipient) -> Attendee:
    for attendee in event.attendees.inner:
        if attendee.recipient == recipient:
            return attendee
    raise ValueError(f"Cannot find {recipient.name} in the event {event.id}.")


@function
def AttendeeResponseStatus(attendee: Attendee) -> ResponseStatus:
    return attendee.status


@function
def ResponseWrapper(attendee: Attendee, response: ResponseStatusType) -> Boolean:
    raise NotImplementedError()
