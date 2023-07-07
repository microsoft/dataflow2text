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

import calendar
import datetime
from dataclasses import replace

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.schemas.date_time import Date, DateTime, Time
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.period import Period
from dataflow2text_domains.calflow.schemas.period_duration import PeriodDuration
from dataflow2text_domains.calflow.schemas.year import Year


def _toSeconds(time: Time) -> int:
    # ignore nanos
    return time.hour.inner * 60 * 60 + time.minute.inner * 60 + time.second.inner


def _periodBetween(start: Date, end: Date) -> Period:
    # non-trivial and untested, probably wrong
    pyStart = start.to_python_date()
    delta = end.to_python_date() - pyStart
    years = delta.days // 365
    rest = delta.days - years * 365
    same_year_date = replace(
        start, year=Year(start.year.inner + years)
    ).to_python_date() + datetime.timedelta(days=rest)

    months = end.month.inner - same_year_date.month
    days = end.day.inner - same_year_date.month
    if end.day.inner < same_year_date.day:
        months -= 1
        days += calendar.monthrange(same_year_date.year, same_year_date.month)[1]
    return Period(Long(years), Long(months), Long(days))


def _periodDurationBetween(
    startDateTime: DateTime, endDateTime: DateTime
) -> PeriodDuration:
    startDate = startDateTime.date
    endDate = endDateTime.date
    period = _periodBetween(startDate, endDate)
    startTime = startDateTime.time
    endTime = endDateTime.time

    duration = Duration(seconds=Long(_toSeconds(endTime) - _toSeconds(startTime)))
    return PeriodDuration(period, duration)


@function
def periodDurationBetween(
    startDateTime: DateTime, endDateTime: DateTime
) -> PeriodDuration:
    return _periodDurationBetween(startDateTime, endDateTime)


@function
def TimeSinceEvent(event: Event) -> PeriodDuration:
    now = get_current_datetime()
    if event.start > now:
        return _periodDurationBetween(now, event.start)
    if event.end < now:
        return _periodDurationBetween(event.end, now)
    return PeriodDuration(Period(), Duration(Long(0)))


@function
def addPeriodDurations(x: PeriodDuration, y: PeriodDuration) -> PeriodDuration:
    raise NotImplementedError()
