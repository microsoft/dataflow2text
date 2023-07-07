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

from dataclasses import dataclass, field
from typing import Any, Dict

from dataflow2text.dataflow.schema import (
    Boolean,
    List,
    Long,
    NullaryStructSchema,
    Option,
    String,
)
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.email_address import EmailAddress
from dataflow2text_domains.calflow.schemas.event_id import EventId
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase
from dataflow2text_domains.calflow.schemas.person import DamonStraeter
from dataflow2text_domains.calflow.schemas.person_name import PersonName
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.response_status import ResponseStatus
from dataflow2text_domains.calflow.schemas.sensitivity import Sensitivity
from dataflow2text_domains.calflow.schemas.show_as_status import ShowAsStatus

# The `organizer` is a required field in CalFlow 2.0 but the preamble does not always have this field.
# When the `organizer` is populated, we trust the preamble.
# Otherwise, when the `isOrganizer` is true, we hard-code the default organizer to be the same as `CurrentUser`;
# when the `isOrganizer` is false, we use a dummy value.
DEFAULT_ORGANIZER = Recipient.from_person(DamonStraeter)
DUMMY_ORGANIZER = Recipient(
    name=PersonName(String("")),
    emailAddress=Option.from_value(EmailAddress(String(""))),
)


@dataclass
class Event(NullaryStructSchema):
    id: EventId
    subject: String
    created: DateTime
    lastModified: DateTime
    start: DateTime
    end: DateTime
    location: Option[LocationKeyphrase]
    isAllDay: Boolean
    isCancelled: Boolean
    allowNewTimeProposals: Boolean
    isOrganizer: Boolean
    showAs: ShowAsStatus
    responseRequested: Boolean
    responseStatus: ResponseStatus
    organizer: Recipient
    attendees: List[Attendee]
    teamsMeetingLink: Option[String]
    sensitivity: Sensitivity
    duration: Duration = field(init=False, repr=False)
    isOneOnOne: Boolean = field(init=False, repr=False)

    def __post_init__(self):
        # =================
        # set self.duration
        # =================
        duration_py = self.end.to_python_datetime() - self.start.to_python_datetime()
        self.duration = Duration(
            seconds=Long(duration_py.days * 86400 + duration_py.seconds),
            nanoseconds=Long(duration_py.microseconds * 1000),
        )

        # =================
        # set self.isOneOnOne
        # =================
        if len(self.attendees) != 2:
            self.isOneOnOne = Boolean(False)
        else:
            self.isOneOnOne = Boolean(
                self.organizer.emailAddress.get().address
                in {
                    attendee.recipient.emailAddress.get().address
                    for attendee in self.attendees.inner
                }
            )

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Event":
        schema = json_obj.get("schema")
        assert schema == "Event", schema
        underlying = json_obj.get("underlying")
        assert underlying is not None

        attendees_obj = underlying.get("attendees")
        assert attendees_obj.get("schema") == "List[Attendee]"
        attendees_underlying = attendees_obj.get("underlying")
        assert isinstance(attendees_underlying, list)

        location_obj = underlying.get("location")
        location: Option[LocationKeyphrase]
        if location_obj is None:
            location = Option(type_arg=LocationKeyphrase.dtype_ctor(), inner=None)
        else:
            location = Option.from_value(
                LocationKeyphrase.from_typed_json(location_obj)
            )

        is_organizer = Boolean.from_typed_json(underlying.get("isOrganizer"))

        organizer_obj = underlying.get("organizer")
        if organizer_obj is None:
            if is_organizer.inner:
                organizer = DEFAULT_ORGANIZER
            else:
                organizer = DUMMY_ORGANIZER
        else:
            organizer = Recipient.from_typed_json(organizer_obj)

        if len(attendees_underlying) > 0:
            attendees = List.from_value(
                [
                    Attendee.from_typed_json(attendee_obj)
                    for attendee_obj in attendees_underlying
                ]
            )
        else:
            attendees = List(type_arg=Attendee.dtype_ctor(), inner=[])

        teams_meeting_link_str = underlying.get("teamsMeetingLink")
        teams_meeting_link: Option[String]
        if teams_meeting_link_str is None:
            teams_meeting_link = Option[String](
                type_arg=String.dtype_ctor(), inner=None
            )
        else:
            teams_meeting_link = Option.from_value(
                String.from_typed_json(teams_meeting_link_str)
            )

        return Event(
            id=EventId.from_typed_json(underlying.get("id")),
            subject=String.from_typed_json(underlying.get("subject")),
            created=DateTime.from_typed_json(underlying.get("created")),
            lastModified=DateTime.from_typed_json(underlying.get("lastModified")),
            start=DateTime.from_typed_json(underlying.get("start")),
            end=DateTime.from_typed_json(underlying.get("end")),
            location=location,
            isAllDay=Boolean.from_typed_json(underlying.get("isAllDay")),
            isCancelled=Boolean.from_typed_json(underlying.get("isCancelled")),
            allowNewTimeProposals=Boolean.from_typed_json(
                underlying.get("allowNewTimeProposals")
            ),
            isOrganizer=is_organizer,
            showAs=ShowAsStatus.from_typed_json(underlying.get("showAs")),
            responseRequested=Boolean.from_typed_json(
                underlying.get("responseRequested")
            ),
            responseStatus=ResponseStatus.from_typed_json(
                underlying.get("responseStatus")
            ),
            organizer=organizer,
            attendees=attendees,
            teamsMeetingLink=teams_meeting_link,
            sensitivity=Sensitivity.from_typed_json(underlying.get("sensitivity")),
        )
