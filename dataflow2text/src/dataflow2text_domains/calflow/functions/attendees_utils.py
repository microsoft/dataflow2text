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

from typing import Set, cast

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import List
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.attendee_type import AttendeeType
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.email_address import EmailAddress
from dataflow2text_domains.calflow.schemas.person import Person
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)

_ListAttendeeTypeName: TypeName = List.dtype_ctor(Attendee.dtype_ctor())


@function
def AttendeesWithResponse(
    attendees: List[Attendee], response: ResponseStatusType
) -> List[Attendee]:
    attendee: Attendee
    return List(
        type_arg=Attendee.dtype_ctor(),
        inner=[
            attendee
            for attendee in attendees.inner
            if attendee.status.response == response
        ],
    )


@function
def AttendeesWithNotResponse(
    attendees: List[Attendee], response: ResponseStatusType
) -> List[Attendee]:
    attendee: Attendee
    return List(
        type_arg=Attendee.dtype_ctor(),
        inner=[
            attendee
            for attendee in attendees.inner
            if attendee.status.response != response
        ],
    )


@function
def AttendeeListHasRecipient(recipient: Recipient) -> Constraint[List[Attendee]]:
    def predicate(attendees: List[Attendee]) -> bool:
        for attendee in attendees.inner:
            if attendee.recipient == recipient:
                return True
        return False

    return Constraint(type_arg=_ListAttendeeTypeName, underlying=predicate)


@function
def AttendeeListHasRecipientWithType(
    recipient: Recipient, attendeeType: AttendeeType
) -> Constraint[List[Attendee]]:
    def predicate(attendees: List[Attendee]) -> bool:
        for attendee in attendees.inner:
            if attendee.recipient == recipient and attendee.type == attendeeType:
                return True
        return False

    return Constraint(type_arg=_ListAttendeeTypeName, underlying=predicate)


@function
def AttendeeListHasRecipientConstraint(
    recipientConstraint: Constraint[Recipient],
) -> Constraint[List[Attendee]]:
    def predicate(attendees: List[Attendee]) -> bool:
        for attendee in attendees.inner:
            if recipientConstraint.allows(attendee.recipient):
                return True
        return False

    return Constraint(type_arg=_ListAttendeeTypeName, underlying=predicate)


@function
def AttendeeListExcludesRecipient(
    recipient: Constraint[Recipient],
) -> Constraint[List[Attendee]]:
    def predicate(attendees: List[Attendee]) -> bool:
        for attendee in attendees.inner:
            if recipient.allows(attendee.recipient):
                return False
        return True

    return Constraint(type_arg=_ListAttendeeTypeName, underlying=predicate)


@function
def AttendeeListHasPeople(people: List[Person]) -> Constraint[List[Attendee]]:

    # We use email address as the unique ID of a `Person`.
    people_email_addresses: Set[EmailAddress] = {
        cast(Person, person).emailAddress for person in people.inner
    }

    def predicate(attendees: List[Attendee]) -> bool:
        attendee_email_addresses = {
            cast(Attendee, attendee).recipient.emailAddress.get()
            for attendee in attendees.inner
        }
        return len(people_email_addresses - attendee_email_addresses) == 0

    return Constraint(type_arg=_ListAttendeeTypeName, underlying=predicate)


@function
def AttendeeListHasPeopleAnyOf(people: List[Person]) -> Constraint[List[Attendee]]:

    # We use email address as the unique ID of a `Person`.
    people_email_addresses: Set[EmailAddress] = {
        cast(Person, person).emailAddress for person in people.inner
    }

    def predicate(attendees: List[Attendee]) -> bool:
        for attendee in attendees.inner:
            if attendee.recipient.emailAddress in people_email_addresses:
                return True
        return False

    return Constraint(type_arg=_ListAttendeeTypeName, underlying=predicate)
