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

from typing import Optional

from dataflow2text.dataflow.schema import Interval
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_datetime_to_calflow_datetime,
)
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.time_zone import TimeZone


def astimezone(date_time: DateTime, time_zone: TimeZone) -> DateTime:
    date_time_py = date_time.to_python_datetime()
    time_zone_py = time_zone.to_python_timezone()
    new_date_time_py = date_time_py.astimezone(time_zone_py)
    # We may need to handle daylight saving.
    # new_date_time_py -= new_date_time_py.dst()
    return convert_python_datetime_to_calflow_datetime(new_date_time_py)


def localize_date_time_interval(interval: Interval[DateTime]) -> Interval[DateTime]:  # type: ignore
    current = get_current_datetime()
    start_local = astimezone(interval.lower, current.timeZone)
    end_local = astimezone(interval.upper, current.timeZone)
    return Interval(lower=start_local, upper=end_local)  # type: ignore


def get_date_time_interval_between_events(
    event1: Event, event2: Event
) -> Optional[Interval[DateTime]]:  # type: ignore
    if event1.end < event2.start:
        return Interval(lower=event1.end, upper=event2.start)  # type: ignore

    if event2.end < event1.start:
        return Interval(lower=event2.end, upper=event1.start)  # type: ignore

    return None
