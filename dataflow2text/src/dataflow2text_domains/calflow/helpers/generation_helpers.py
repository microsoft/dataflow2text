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

from dataflow2text.dataflow.function import BaseFunction, Get, GetAttr, StringCtor
from dataflow2text.dataflow.schema import (
    Boolean,
    Interval,
    List,
    Long,
    Number,
    Option,
    String,
    StructAttribute,
    Unit,
)
from dataflow2text_domains.calflow.schemas.attendance_response import AttendanceResponse
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.join_event_command import JoinEventCommand
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.person_name import PersonName
from dataflow2text_domains.calflow.schemas.query_event_response import (
    QueryEventResponse,
)
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.response_status import ResponseStatus
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)
from dataflow2text_domains.calflow.schemas.time import Time
from dataflow2text_domains.calflow.schemas.update_event_response import (
    UpdateEventResponse,
)
from dataflow2text_domains.calflow.schemas.year import Year

DTYPE_ATTENDANCE_RESPONSE = AttendanceResponse.dtype_ctor()
DTYPE_ATTENDEE = Attendee.dtype_ctor()
DTYPE_BOOLEAN = Boolean.dtype_ctor()
DTYPE_DATE = Date.dtype_ctor()
DTYPE_DATE_TIME = DateTime.dtype_ctor()
DTYPE_DAY_OF_WEEK = DayOfWeek.dtype_ctor()
DTYPE_DURATION = Duration.dtype_ctor()
DTYPE_EVENT = Event.dtype_ctor()
DTYPE_LOCATION_KEYPHRASE = LocationKeyphrase.dtype_ctor()
DTYPE_LONG = Long.dtype_ctor()
DTYPE_MONTH = Month.dtype_ctor()
DTYPE_NUMBER = Number.dtype_ctor()
DTYPE_PERSON_NAME = PersonName.dtype_ctor()
DTYPE_QUERY_EVENT_RESPONSE = QueryEventResponse.dtype_ctor()
DTYPE_RECIPIENT = Recipient.dtype_ctor()
DTYPE_RESPONSE_STATUS = ResponseStatus.dtype_ctor()
DTYPE_RESPONSE_STATUS_TYPE = ResponseStatusType.dtype_ctor()
DTYPE_STRING = String.dtype_ctor()
DTYPE_TIME = Time.dtype_ctor()
DTYPE_UPDATE_EVENT_RESPONSE = UpdateEventResponse.dtype_ctor()
DTYPE_YEAR = Year.dtype_ctor()
DTYPE_UNIT = Unit.dtype_ctor()
DTYPE_JOIN_EVENT_COMMAND = JoinEventCommand.dtype_ctor()

DTYPE_INTERVAL_DATE = Interval.dtype_ctor(Date.dtype_ctor())
DTYPE_INTERVAL_TIME = Interval.dtype_ctor(Time.dtype_ctor())
DTYPE_INTERVAL_DATE_TIME = Interval.dtype_ctor(DateTime.dtype_ctor())

DTYPE_LIST_ATTENDEE = List.dtype_ctor(Attendee.dtype_ctor())

DTYPE_CONSTRAINT_DATE = Constraint.dtype_ctor(DTYPE_DATE)
DTYPE_CONSTRAINT_DATE_TIME = Constraint.dtype_ctor(DTYPE_DATE_TIME)
DTYPE_CONSTRAINT_EVENT = Constraint.dtype_ctor(DTYPE_EVENT)
DTYPE_CONSTRAINT_LIST_ATTENDEE = Constraint.dtype_ctor(DTYPE_LIST_ATTENDEE)
DTYPE_CONSTRAINT_LOCATION_KEYPHRASE = Constraint.dtype_ctor(DTYPE_LOCATION_KEYPHRASE)
DTYPE_CONSTRAINT_RECIPIENT = Constraint.dtype_ctor(DTYPE_RECIPIENT)
DTYPE_CONSTRAINT_STRING = Constraint.dtype_ctor(DTYPE_STRING)
DTYPE_CONSTRAINT_TIME = Constraint.dtype_ctor(DTYPE_TIME)

DTYPE_OPTION_LOCATION_KEYPHRASE = Option.dtype_ctor(DTYPE_LOCATION_KEYPHRASE)


def get_subject_from_event(event: BaseFunction[Event]) -> BaseFunction[String]:
    return GetAttr(StructAttribute("subject", String.dtype_ctor()), event)


def strip_string(string: BaseFunction[String]) -> BaseFunction:
    return StringCtor(string.__value__.inner.strip())


def get_attendees_from_event(event: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("attendees", DTYPE_LIST_ATTENDEE), event)


def get_person_name_from_recipient(
    recipient: BaseFunction[Recipient],
) -> BaseFunction[PersonName]:
    return GetAttr(
        StructAttribute("name", DTYPE_PERSON_NAME),
        recipient,
    )


def get_recipient_from_attendee(
    attendee: BaseFunction[Attendee],
) -> BaseFunction[Recipient]:
    return GetAttr(
        StructAttribute("recipient", DTYPE_RECIPIENT),
        attendee,
    )


def get_name_from_person_name(
    person_name: BaseFunction[PersonName],
) -> BaseFunction[String]:
    return GetAttr(StructAttribute("name", DTYPE_STRING), person_name)


def get_first_name_from_name(
    name: BaseFunction[String], lowercase: bool = False
) -> BaseFunction[String]:
    first_name = name.__value__.inner.split(" ")[0]
    if lowercase:
        first_name = first_name.lower()
    return StringCtor(first_name)


def get_response_from_response_status(status: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("response", ResponseStatusType.dtype_ctor()), status)


def get_response_status_from_attendee(attendee: BaseFunction) -> BaseFunction:
    return get_response_from_response_status(
        GetAttr(
            StructAttribute("status", ResponseStatus.dtype_ctor()),
            attendee,
        ),
    )


def get_search_results(search: BaseFunction) -> BaseFunction:
    return GetAttr(
        StructAttribute("results", List.dtype_ctor(Event.dtype_ctor())), search
    )


def get_start_from_event(event: BaseFunction[Event]) -> BaseFunction[DateTime]:
    return GetAttr[Event, DateTime](
        StructAttribute("start", DateTime.dtype_ctor()), event
    )


def get_end_from_event(event: BaseFunction[Event]) -> BaseFunction[DateTime]:
    return GetAttr[Event, DateTime](
        StructAttribute("end", DateTime.dtype_ctor()), event
    )


def get_date_from_datetime(datetime: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("date", Date.dtype_ctor()), datetime)


def get_time_from_datetime(datetime: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("time", Date.dtype_ctor()), datetime)


def get_month_from_date(date: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("month", Month.dtype_ctor()), date)


def get_dow_from_date(date: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("dayOfWeek", DayOfWeek.dtype_ctor()), date)


def get_day_from_date(date: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("day", Day.dtype_ctor()), date)


def get_year_from_date(date: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("year", Year.dtype_ctor()), date)


def get_inner_of_type_long(value: BaseFunction) -> BaseFunction:
    return GetAttr(StructAttribute("inner", Long.dtype_ctor()), value)


def get_inner_from_option(option: BaseFunction) -> BaseFunction:
    return Get(option)


def stringify_time(time: BaseFunction[Time], include_am_pm: bool) -> BaseFunction:
    if include_am_pm:
        fmt = "%l:%M %p"
    else:
        fmt = "%l:%M"
    return StringCtor(time.__value__.to_python_time().strftime(fmt))
