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

from datetime import timedelta

from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_date_to_calflow_date,
    convert_python_datetime_to_calflow_datetime,
)
from dataflow2text_domains.calflow.helpers.date_helpers import get_today, get_tomorrow
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.period_duration import PeriodDuration
from dataflow2text_domains.calflow.schemas.time import Time


@function
def NextTime(time: Time) -> DateTime:
    now = get_current_datetime()
    if time < now.time:
        return DateTime(get_tomorrow(), time, now.timeZone)
    else:
        return DateTime(get_today(), time, now.timeZone)


@function
def Now() -> DateTime:
    return get_current_datetime()


@function
def PeriodDurationBeforeDateTime(
    dateTime: DateTime, periodDuration: PeriodDuration
) -> DateTime:
    """Returns a DateTime before the supplied dateTime adjusted by the supplied periodDuration."""
    datetime_py = dateTime.to_python_datetime()
    new_datetime_py = datetime_py - periodDuration.to_python_relativedelta()
    return convert_python_datetime_to_calflow_datetime(new_datetime_py)


@function
def adjustByPeriodDuration(
    datetime: DateTime, periodDuration: PeriodDuration
) -> DateTime:
    datetime_py = datetime.to_python_datetime()
    new_datetime_py = datetime_py + periodDuration.to_python_relativedelta()
    return convert_python_datetime_to_calflow_datetime(new_datetime_py)


@function
def DateAtTimeWithDefaults(date: Date, time: Time) -> DateTime:
    """Uses current TZ when building the DT."""
    current_datetime = get_current_datetime()
    return DateTime(
        date=date,
        time=time,
        timeZone=current_datetime.timeZone,
    )


@function
def TimeBeforeDateTime(dateTime: DateTime, time: Time) -> DateTime:
    if time < dateTime.time:
        return DateTime(date=dateTime.date, time=time, timeZone=dateTime.timeZone)

    prev_day_py = dateTime.to_python_datetime() - timedelta(days=1)
    return DateTime(
        date=convert_python_date_to_calflow_date(prev_day_py.date()),
        time=time,
        timeZone=dateTime.timeZone,
    )


@function
def TimeAfterDateTime(dateTime: DateTime, time: Time) -> DateTime:
    if time > dateTime.time:
        return DateTime(date=dateTime.date, time=time, timeZone=dateTime.timeZone)

    next_day_py = dateTime.to_python_datetime() + timedelta(days=1)
    return DateTime(
        date=convert_python_date_to_calflow_date(next_day_py.date()),
        time=time,
        timeZone=dateTime.timeZone,
    )
