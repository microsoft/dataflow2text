import dataclasses

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.helpers.conversions import convert_time_to_datetime
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.time import Time
from dataflow2text_domains.calflow.schemas.time_range_constraint import (
    TimeRangeConstraint,
)


@function
def Early() -> Constraint[Time]:
    def predicate(time: Time) -> bool:
        return time < Time(hour=Long(10))

    return Constraint(type_arg=Time.dtype_ctor(), underlying=predicate)


@function
def Late() -> Constraint[Time]:
    def predicate(time: Time) -> bool:
        return time > Time(hour=Long(15))

    return Constraint(type_arg=Time.dtype_ctor(), underlying=predicate)


@function
def Morning() -> TimeRangeConstraint:
    return TimeRangeConstraint(
        start_time=Time(hour=Long(6), minute=Long(0)),
        end_time=Time(hour=Long(11), minute=Long(59), second=Long(59)),
    )


@function
def LateMorning() -> TimeRangeConstraint:
    return TimeRangeConstraint(
        start_time=Time(hour=Long(10), minute=Long(0)),
        end_time=Time(hour=Long(11), minute=Long(59), second=Long(59)),
    )


@function
def Afternoon() -> TimeRangeConstraint:
    return TimeRangeConstraint(
        start_time=Time(hour=Long(12), minute=Long(0)),
        end_time=Time(hour=Long(16), minute=Long(59), second=Long(59)),
    )


@function
def LateAfternoon() -> TimeRangeConstraint:
    return TimeRangeConstraint(
        start_time=Time(hour=Long(15), minute=Long(20)),
        end_time=Time(hour=Long(16), minute=Long(59), second=Long(59)),
    )


@function
def Evening() -> TimeRangeConstraint:
    return TimeRangeConstraint(
        start_time=Time(hour=Long(17), minute=Long(0)),
        end_time=Time(hour=Long(20), minute=Long(29), second=Long(59)),
    )


@function
def Night() -> TimeRangeConstraint:
    return TimeRangeConstraint(
        start_time=Time(hour=Long(17), minute=Long(0)),
        end_time=Time(hour=Long(23), minute=Long(59), second=Long(59)),
    )


@function
def EarlyTimeRange(timeRange: TimeRangeConstraint) -> Constraint[Time]:
    def predicate(time: Time) -> bool:
        """Returns True if `time` is in the first 3rd of the range [start, end]."""
        if not timeRange.allows(time):
            return False

        start_time_py = timeRange.start_time.to_python_time()
        start_datetime_py = convert_time_to_datetime(start_time_py)
        end_time_py = timeRange.end_time.to_python_time()
        end_datetime_py = convert_time_to_datetime(end_time_py)
        target_time_py = time.to_python_time()
        target_datetime_py = convert_time_to_datetime(target_time_py)
        num_total_microseconds = (end_datetime_py - start_datetime_py).microseconds + 1
        num_microseconds = (target_datetime_py - start_datetime_py).microseconds + 1
        return num_microseconds <= num_total_microseconds / 3

    return Constraint(type_arg=Time.dtype_ctor(), underlying=predicate)


@function
def LateTimeRange(timeRange: TimeRangeConstraint) -> Constraint[Time]:
    def predicate(time: Time) -> bool:
        """Returns True if `time` is in the last 3rd of the range [start, end]."""
        if not timeRange.allows(time):
            return False

        start_time_py = timeRange.start_time.to_python_time()
        start_datetime_py = convert_time_to_datetime(start_time_py)
        end_time_py = timeRange.end_time.to_python_time()
        end_datetime_py = convert_time_to_datetime(end_time_py)
        target_time_py = time.to_python_time()
        target_datetime_py = convert_time_to_datetime(target_time_py)
        num_total_microseconds = (end_datetime_py - start_datetime_py).microseconds + 1
        num_microseconds = (target_datetime_py - start_datetime_py).microseconds + 1
        return num_microseconds <= 2 * num_total_microseconds / 3

    return Constraint(type_arg=Time.dtype_ctor(), underlying=predicate)


@function
def TimeAround(time: Time) -> TimeRangeConstraint:
    """Returns a TimeRangeConstraint for time within +/- 1 hour around the specified `time`."""
    if time.hour.inner <= 1 or time.hour.inner >= 23:
        raise ValueError(f"Cannot create a TimeAround constraint for {time}.")

    return TimeRangeConstraint(
        start_time=dataclasses.replace(time, hour=Long(time.hour.inner - 1)),
        end_time=dataclasses.replace(time, hour=Long(time.hour.inner + 1)),
    )


@function
def TimeToTime(time1: Time, time2: Time) -> TimeRangeConstraint:
    """Returns a range for the given time."""
    if time1 < time2:
        start_time = time1
        end_time = time2
    else:
        start_time = time2
        end_time = time1
    return TimeRangeConstraint(start_time=start_time, end_time=end_time)
