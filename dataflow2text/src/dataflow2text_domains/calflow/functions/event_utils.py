# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
