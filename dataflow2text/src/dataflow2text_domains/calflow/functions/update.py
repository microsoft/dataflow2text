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
from dataflow2text.dataflow.schema import Boolean, List, Option, String
from dataflow2text_domains.calflow.errors.calflow_runtime_error import (
    EventNotFoundError,
    UpdateEventOrganizedByOtherUserError,
)
from dataflow2text_domains.calflow.functions.person_utils import CurrentUser
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.event_helpers import get_event
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.email_address import EmailAddress
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.event_id import EventId
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase
from dataflow2text_domains.calflow.schemas.person_name import PersonName
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.response_status import ResponseStatus
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)
from dataflow2text_domains.calflow.schemas.sensitivity import Sensitivity
from dataflow2text_domains.calflow.schemas.show_as_status import ShowAsStatus
from dataflow2text_domains.calflow.schemas.update_commit_event import UpdateCommitEvent
from dataflow2text_domains.calflow.schemas.update_event_response import (
    UpdateEventResponse,
)


@function
def UpdateCommitEventWrapper(event: UpdateCommitEvent) -> UpdateEventResponse:
    # TODO: Currently returning a dummy value.
    current_date_time = get_current_datetime()
    return UpdateEventResponse(
        item=Event(
            id=event.id,
            subject=String(""),
            created=current_date_time,
            lastModified=current_date_time,
            start=current_date_time,
            end=current_date_time,
            location=Option(LocationKeyphrase.dtype_ctor(), None),
            isAllDay=Boolean(False),
            isCancelled=Boolean(False),
            allowNewTimeProposals=Boolean(False),
            isOrganizer=Boolean(False),
            showAs=ShowAsStatus.Unknown(),
            responseRequested=Boolean(False),
            responseStatus=ResponseStatus(ResponseStatusType.Null()),
            organizer=Recipient(
                PersonName(String("")), Option(EmailAddress.dtype_ctor(), None)
            ),
            attendees=List(Attendee.dtype_ctor(), []),
            teamsMeetingLink=Option(String.dtype_ctor(), None),
            sensitivity=Sensitivity.Normal(),
        )
    )


@function
def UpdatePreflightEventWrapper(
    # pylint: disable=redefined-builtin
    id: EventId,
    update: Constraint[Event],
) -> UpdateCommitEvent:
    event = get_event(id)
    if event is None:
        raise EventNotFoundError(id.inner)

    if event.organizer != Recipient.from_person(CurrentUser().__value__):
        raise UpdateEventOrganizedByOtherUserError()

    # Currently it does not preserve the `update` argument.
    return UpdateCommitEvent(id=id)
