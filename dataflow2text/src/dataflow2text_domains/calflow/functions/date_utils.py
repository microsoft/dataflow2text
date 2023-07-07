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

import datetime
import typing
from typing import Optional, Tuple, cast

import convertdate
from convertdate import gregorian
from dateutil.relativedelta import relativedelta

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_date_to_calflow_date,
)
from dataflow2text_domains.calflow.helpers.date_helpers import (
    adjust_by_period,
    get_today,
    get_tomorrow,
    holiday_year,
    last_day_of_month,
    month_day,
    next_dow,
    next_or_same_dow,
    next_or_same_month_day,
    period_before_date,
    previous_dow,
    previous_or_same_dow,
)
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_range_constraint import (
    DateRangeConstraint,
)
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.holiday import Holiday
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.period import Period
from dataflow2text_domains.calflow.schemas.year import Year


@function
def adjustByPeriod(date: Date, period: Period) -> Date:
    return adjust_by_period(date, period)


@function
def PeriodBeforeDate(date: Date, period: Period) -> Date:
    return period_before_date(date, period)


@function
def Today() -> Date:
    return get_today()


@function
def Yesterday() -> Date:
    today = get_today().to_python_date()
    yesterday = today + datetime.timedelta(days=-1)
    return convert_python_date_to_calflow_date(yesterday)


@function
def Tomorrow() -> Date:
    return get_tomorrow()


@function
def NextDOW(dow: DayOfWeek) -> Date:
    curr_datetime = get_current_datetime()
    curr_date = curr_datetime.date
    curr_jd_day = gregorian.to_jd(
        curr_date.year.inner,
        curr_date.month.inner,
        curr_date.day.inner,
    )
    target_jd_day = convertdate.utils.next_weekday(dow.inner, curr_jd_day)
    year, month, day = gregorian.from_jd(target_jd_day)
    return Date(year=Year(year), month=Month(month), day=Day(day))


@function
def DowOfWeekNew(dow: DayOfWeek, week: Constraint[Date]) -> Date:
    week = cast(DateRangeConstraint, week)
    start_py = week.start_date.to_python_date()
    end_py = week.end_date.to_python_date()
    duration_days = (end_py - start_py).days

    # this is the logic implemented in the DCE macro library; I'm suspicious
    # (especially of the second case)
    if duration_days < 3:
        return next_or_same_dow(week.start_date, dow)
    if dow == DayOfWeek.Sunday():
        return week.start_date
    return next_or_same_dow(week.start_date, dow)


@function
def nextDayOfWeek(date: Date, day: DayOfWeek) -> Date:
    return next_dow(date, day)


@function
def nextOrSameDayOfWeek(date: Date, dow: DayOfWeek) -> Date:
    return next_or_same_dow(date, dow)


@function
def previousDayOfWeek(date: Date, day: DayOfWeek) -> Date:
    return previous_dow(date, day)


@function
def previousOrSameDayOfWeek(date: Date, dow: DayOfWeek) -> Date:
    return previous_or_same_dow(date, dow)


@function
def ClosestDayOfWeek(date: Date, dow: DayOfWeek) -> Date:
    curr_date = date.to_python_date()
    target_dow = dow.inner
    if curr_date.weekday() == target_dow:
        return date

    for days in range(1, 8):
        prev = curr_date - datetime.timedelta(days=days)
        if prev.weekday() == target_dow:
            return convert_python_date_to_calflow_date(prev)
        curr = curr_date + datetime.timedelta(days=days)
        if curr.weekday() == target_dow:
            return convert_python_date_to_calflow_date(curr)

    raise RuntimeError("Unexpected error in ClosestDayOfWeek.")


@function
def MDY(day: Long, month: Month, year: Year) -> Date:
    return Date(year=year, month=month, day=Day(day.inner))


@function
def MD(day: Long, month: Month) -> Date:
    return month_day(month=month, day=day)


@function
def nextMonthDay(date: Date, month: Month, day: Long) -> Date:
    if date.month.inner < month.inner:
        return Date(year=date.year, month=month, day=Day(day.inner))

    if date.month == month and date.day.inner < day.inner:
        return Date(year=date.year, month=month, day=Day(day.inner))

    return Date(year=Year(date.year.inner + 1), month=month, day=Day(day.inner))


@function
def nextOrSameMonthDay(month: Month, day: Day) -> Date:
    return next_or_same_month_day(month, day)


@function
def previousMonthDay(date: Date, month: Month, day: Day) -> Date:
    if date.month.inner > month.inner:
        return Date(year=date.year, month=month, day=day)

    if date.month == month and date.day.inner > day.inner:
        return Date(year=date.year, month=month, day=day)

    return Date(year=Year(date.year.inner - 1), month=month, day=day)


@function
def ClosestDay(date: Date, day: Day) -> Date:
    # If `curr_month` is `datetime(2020, 3, 31)`, then `last_month` would be `datetime(2020, 2, 29)`
    # and `next_month` would be `datetime(2020, 4, 30)`.
    curr_month = date.to_python_date()
    last_month = curr_month - relativedelta(month=1)
    next_month = curr_month + relativedelta(month=1)

    def _try_create_date(year: int, month: int) -> Optional[datetime.date]:
        try:
            new_date = datetime.date(
                year=year,
                month=month,
                day=int(day.inner),
            )
        except ValueError:
            return None
        return new_date

    date_on_last_month = _try_create_date(last_month.year, last_month.month)
    date_on_curr_month = _try_create_date(curr_month.year, curr_month.month)
    date_on_next_month = _try_create_date(next_month.year, next_month.month)
    possible_dates_with_delta: typing.List[Tuple[datetime.date, int]] = [
        (d, relativedelta(d, curr_month).days)
        for d in [date_on_last_month, date_on_curr_month, date_on_next_month]
        if d is not None
    ]
    closest_day, _delta = min(possible_dates_with_delta, key=lambda x: abs(x[1]))
    closest_day = cast(datetime.date, closest_day)
    return convert_python_date_to_calflow_date(closest_day)


@function
def LastDayOfMonth(month: Month) -> Date:
    return last_day_of_month(month)


@function
def nextDayOfMonth(date: Date, day: Long) -> Date:
    if date.day.inner < day.inner:
        # If this new date is invalid, we should throw an exception.
        return Date(year=date.year, month=date.month, day=Day(day.inner))

    python_date = date.to_python_date()
    next_month = python_date + relativedelta(months=1)
    return Date(
        year=Year(next_month.year),
        month=Month(next_month.month),
        day=Day(day.inner),
    )


@function
def HolidayYear(holiday: Holiday, year: Year) -> Date:
    return holiday_year(holiday, year)


@function
def NextHolidayFromToday(holiday: Holiday) -> Date:
    curr_datetime = get_current_datetime()
    holiday_in_curr_year = holiday_year(holiday, curr_datetime.date.year)
    if holiday_in_curr_year > curr_datetime.date:
        return holiday_in_curr_year
    holiday_in_next_year = holiday_year(
        holiday, Year(curr_datetime.date.year.inner + 1)
    )
    return holiday_in_next_year
