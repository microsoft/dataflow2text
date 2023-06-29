from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, List, Unit
from dataflow2text_domains.calflow.schemas.attendance_response import AttendanceResponse
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.respond_comment import RespondComment
from dataflow2text_domains.calflow.schemas.response_should_send import RespondShouldSend
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)


@function
def EventAttendance(
    event: Event,
    response: ResponseStatusType = ResponseStatusType.Null(),
    comment: RespondComment = RespondComment(""),
    sendResponse: RespondShouldSend = RespondShouldSend(True),
) -> AttendanceResponse:
    """Allows a user to update their event attendance (ie: accept, decline, tentative) and suggest new times when they
    are not the organizer, including sending a comment/message to the organizer.

    Currently the method simply return the new `AttendanceResponse` without any API call.
    """
    return AttendanceResponse(status=response)


@function
def ForwardEventWrapper(event: Event, recipients: List[Recipient]) -> Unit:
    """Forwards an event or initiates an update if the user is the organizer and there were 0 attendees on the event.
    This is the core forward macro, with the other 2 calling this macro after some input formatting.

    Currently the method simply return a `Unit` without any API call.
    """
    return Unit()


@function
def IsTeamsMeeting(event: Event) -> Boolean:
    """Returns True if the Event passed in includes a Teams meeting link."""
    return Boolean(event.teamsMeetingLink is not None)
