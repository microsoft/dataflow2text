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

from typing import cast

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Number, String
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.date_helpers import adjust_by_period
from dataflow2text_domains.calflow.helpers.period_helpers import to_days
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_range_constraint import (
    DateRangeConstraint,
)
from dataflow2text_domains.calflow.schemas.date_time import DateTime, TimeZone
from dataflow2text_domains.calflow.schemas.date_time_range_constraint import (
    DateTimeRangeConstraint,
)
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.period import Period
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.time import Time
from dataflow2text_domains.calflow.schemas.time_range_constraint import (
    TimeRangeConstraint,
)


def _overlap(start1, end1, start2, end2) -> bool:
    """Returns true if the range (start1, end1) overlap with (start2, end2)."""
    return end1 >= start2 and end2 >= start1


def _event_on_date(date: Date, event: Constraint[Event]) -> Constraint[Event]:
    # We may need to change this to ev.start <= date and ev.end >= date.
    def predicate(ev: Event) -> bool:
        return ev.start.date == date and event.allows(ev)

    return Constraint(
        type_arg=Event.dtype_ctor(),
        underlying=predicate,
    )


def _event_during_range_time(
    event: Constraint[Event], timeRange: TimeRangeConstraint
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        if ev.start.date == ev.end.date:
            return _overlap(
                ev.start.time, ev.end.time, timeRange.start_time, timeRange.end_time
            ) and event.allows(ev)

        return not ev.start.time > timeRange.end_time and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventOnDate(date: Date, event: Constraint[Event]) -> Constraint[Event]:
    return _event_on_date(date, event)


@function
def EventSometimeOnDate(date: Date, event: Constraint[Event]) -> Constraint[Event]:
    return _event_on_date(date, event)


@function
def EventAtTime(event: Constraint[Event], time: Time) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return ev.start.time.to_python_time() == time.to_python_time() and event.allows(
            ev
        )

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventOnDateTime(dateTime: DateTime, event: Constraint[Event]) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        # Need to use `to_python_datetime` so we can normalize the timezone.
        return (
            ev.start.to_python_datetime() == dateTime.to_python_datetime()
            and event.allows(ev)
        )

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventOnDateBeforeTime(
    date: Date, event: Constraint[Event], time: Time
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return ev.start.date == date and ev.start.time <= time and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventOnDateAfterTime(
    date: Date, event: Constraint[Event], time: Time
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return ev.start.date == date and ev.start.time >= time and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventOnDateFromTimeToTime(
    date: Date, event: Constraint[Event], time1: Time, time2: Time
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        if ev.start.date != date:
            return False

        if time1 < time2:
            early_time = time1
            late_time = time2
        else:
            early_time = time2
            late_time = time1

        early_datetime = DateTime(
            date=date, time=early_time, timeZone=TimeZone(id=String("UTC"))
        )
        late_datetime = DateTime(
            date=date, time=late_time, timeZone=TimeZone(id=String("UTC"))
        )

        return (
            ev.start.date == date
            and _overlap(ev.start, ev.end, early_datetime, late_datetime)
            and event.allows(ev)
        )

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventBeforeDateTime(
    dateTime: DateTime, event: Constraint[Event]
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return ev.end <= dateTime and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventAfterDateTime(
    event: Constraint[Event], dateTime: DateTime
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return ev.start > dateTime and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventDuringRange(
    event: Constraint[Event],
    # pylint: disable=redefined-builtin
    range: DateRangeConstraint,
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return _overlap(
            ev.start.date, ev.end.date, range.start_date, range.end_date
        ) and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventDuringRangeTime(
    event: Constraint[Event], timeRange: TimeRangeConstraint
) -> Constraint[Event]:
    return _event_during_range_time(event, timeRange)


@function
def EventOnDateWithTimeRange(
    event: Constraint[Event], timeRange: TimeRangeConstraint
) -> Constraint[Event]:
    # It seems that all `EventOnDateWithTimeRange` would use `EventOnDate` as the first argument. We could do an assertion
    # here if needed.
    return _event_during_range_time(event, timeRange)


@function
def EventDuringRangeDateTime(
    event: Constraint[Event],
    # pylint: disable=redefined-builtin
    range: DateTimeRangeConstraint,
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return _overlap(
            ev.start, ev.end, range.start_datetime, range.end_datetime
        ) and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventBetweenEvents(
    event: Constraint[Event], event1: Event, event2: Event
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        if event1.start < event2.start:
            early_event = event1
            late_event = event2
        else:
            early_event = event2
            late_event = event1

        return (
            early_event.end <= ev.start
            and ev.end <= late_event.start
            and event.allows(ev)
        )

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventForRestOfToday(event: Constraint[Event]) -> Constraint[Event]:
    current_datetime = get_current_datetime()

    def predicate(ev: Event) -> bool:
        return ev.start >= current_datetime and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventAllDayOnDate(event: Constraint[Event], date: Date) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return ev.isAllDay.inner and ev.start.date == date and event.allows(ev)

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventAllDayDateUntilDate(
    endDate: Date, event: Constraint[Event], startDate: Date
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return (
            ev.start.date == startDate and ev.end.date == endDate and ev.isAllDay.inner
        )

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventAllDayStartingDateForPeriod(
    event: Constraint[Event], startDate: Date, period: Period
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        endDate = adjust_by_period(startDate, period)
        return (
            event.allows(ev)
            and ev.start.date == startDate
            and ev.end.date == endDate
            and ev.isAllDay.inner
        )

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventAllDayForDateRange(
    event: Constraint[Event], dateRange: Constraint[Date]
) -> Constraint[Event]:
    dateRange_ = cast(DateRangeConstraint, dateRange)
    newEnd = adjust_by_period(dateRange_.end_date, to_days(Number(1)))

    def predicate(ev: Event) -> bool:
        return (
            event.allows(ev)
            and ev.start == dateRange_.start_date
            and ev.end == newEnd
            and ev.isAllDay.inner
        )

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def SetOtherOrganizer(
    eventConstraint: Constraint[Event], recipient: Recipient
) -> Constraint[Event]:
    def predicate(ev: Event) -> bool:
        return not ev.isOrganizer and ev.organizer == recipient

    return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)


@function
def EventRescheduled(event: Constraint[Event]) -> Constraint[Event]:
    """This is a wrapper computation to indicate to reschedule an existing event.

    Since it does not provide a concrete event to be rescheduled, we define it as a constraint class instead of a method
    so the caller can determine how to interpret this constraint.
    """
    return event
