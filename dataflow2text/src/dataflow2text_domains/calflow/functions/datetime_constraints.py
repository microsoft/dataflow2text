from datetime import timedelta

from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_datetime_to_calflow_datetime,
)
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.date_time_range_constraint import (
    DateTimeRangeConstraint,
)
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.period_duration import PeriodDuration
from dataflow2text_domains.calflow.schemas.time import Time


@function
def DateTimeAndConstraint(
    dateTime1: DateTime, dateTime2: DateTime
) -> DateTimeRangeConstraint:
    start_datetime = min(dateTime1, dateTime2)
    end_datetime = max(dateTime1, dateTime2)

    return DateTimeRangeConstraint(
        start_datetime=start_datetime, end_datetime=end_datetime
    )


@function
def DateTimeAndConstraintBetweenEvents(
    event1: Event, event2: Event
) -> DateTimeRangeConstraint:
    if event1.end == event2.start or event2.end == event1.start:
        raise ValueError("Events are adjacent")
    # 2 possibilities:
    # e1:   s[      ]e       |       s[     ]e
    # e2:        s[     ]e   |   s[     ]e
    if event1.start <= event2.end and event2.start <= event1.end:
        raise ValueError("Events are overlapping")

    if event1.start < event2.start:
        start_datetime = event1.end
        end_datetime = event2.start
    else:
        start_datetime = event2.end
        end_datetime = event1.start

    return DateTimeRangeConstraint(
        start_datetime=start_datetime, end_datetime=end_datetime
    )


@function
def DateTimeConstraint(
    constraint: Constraint[Time], date: Date
) -> Constraint[DateTime]:
    def predicate(dt: DateTime):
        return dt.date == date and constraint.allows(dt.time)

    return Constraint(type_arg=DateTime.dtype_ctor(), underlying=predicate)


@function
def DateTimeFromDowConstraint(
    dowConstraint: Constraint[DayOfWeek], time: Time
) -> Constraint[DateTime]:
    def predicate(dt: DateTime):
        return dowConstraint.allows(dt.date.dayOfWeek) and dt.time == time

    return Constraint(type_arg=DateTime.dtype_ctor(), underlying=predicate)


@function
def NextPeriodDuration(periodDuration: PeriodDuration) -> DateTimeRangeConstraint:
    """Returns a constraint from now to the `periodDuration` after now."""
    start_datetime_py = get_current_datetime().to_python_datetime()
    end_datetime_py = start_datetime_py + periodDuration.to_python_relativedelta()
    return DateTimeRangeConstraint(
        start_datetime=convert_python_datetime_to_calflow_datetime(start_datetime_py),
        end_datetime=convert_python_datetime_to_calflow_datetime(end_datetime_py),
    )


@function
def OnDateBeforeTime(date: Date, time: Time) -> Constraint[DateTime]:
    def predicate(dt: DateTime):
        return dt.date == date and dt.time < time

    return Constraint(type_arg=DateTime.dtype_ctor(), underlying=predicate)


@function
def OnDateAfterTime(date: Date, time: Time) -> Constraint[DateTime]:
    def predicate(dt: DateTime):
        return dt.date == date and dt.time >= time

    return Constraint(type_arg=DateTime.dtype_ctor(), underlying=predicate)


@function
def AroundDateTime(dateTime: DateTime) -> DateTimeRangeConstraint:
    """Returns a DateTimeRangeConstraint for datetime within +/- 1 hour around the specified `dateTime`."""
    datetime_py = dateTime.to_python_datetime()
    start_datetime_py = datetime_py - timedelta(hours=1)
    end_datetime_py = datetime_py + timedelta(hours=1)
    return DateTimeRangeConstraint(
        start_datetime=convert_python_datetime_to_calflow_datetime(start_datetime_py),
        end_datetime=convert_python_datetime_to_calflow_datetime(end_datetime_py),
    )


@function
def Later() -> Constraint[DateTime]:
    def predicate(dt: DateTime):
        return dt > get_current_datetime()

    return Constraint(type_arg=DateTime.dtype_ctor(), underlying=predicate)
