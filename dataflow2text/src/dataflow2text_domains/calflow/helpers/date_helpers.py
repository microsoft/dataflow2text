import calendar
import datetime
from typing import cast

import convertdate
from convertdate import gregorian, holidays

from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_date_to_calflow_date,
)
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.holiday import Holiday
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.period import Period
from dataflow2text_domains.calflow.schemas.year import Year


def get_today() -> Date:
    current_datetime = get_current_datetime()
    return current_datetime.date


def get_yesterday() -> Date:
    today = get_today().to_python_date()
    yesterday = today + datetime.timedelta(days=-1)
    return convert_python_date_to_calflow_date(yesterday)


def get_tomorrow() -> Date:
    today = get_today().to_python_date()
    tomorrow = today + datetime.timedelta(days=1)
    return convert_python_date_to_calflow_date(tomorrow)


def adjust_by_period(date: Date, period: Period) -> Date:
    python_date = date.to_python_date()
    delta = period.to_python_relativedelta()
    new_python_date = cast(datetime.date, python_date + delta)
    return convert_python_date_to_calflow_date(new_python_date)


def previous_dow(date: Date, dow: DayOfWeek) -> Date:
    curr_jd_day = gregorian.to_jd(
        date.year.inner,
        date.month.inner,
        date.day.inner,
    )
    target_jd_day = convertdate.utils.previous_weekday(dow.inner, curr_jd_day)
    year, month, day = gregorian.from_jd(target_jd_day)
    return Date(year=Year(year), month=Month(month), day=Day(day))


def previous_or_same_dow(date: Date, dow: DayOfWeek) -> Date:
    if date.dayOfWeek == dow:
        return date
    return previous_dow(date, dow)


def next_dow(date: Date, dow: DayOfWeek) -> Date:
    curr_jd_day = gregorian.to_jd(date.year.inner, date.month.inner, date.day.inner)
    target_jd_day = convertdate.utils.next_weekday(dow.inner, curr_jd_day)
    year, month, day = gregorian.from_jd(target_jd_day)
    return Date(
        year=Year(year),
        month=Month(month),
        day=Day(day),
    )


def next_or_same_dow(date: Date, dow: DayOfWeek) -> Date:
    if date.dayOfWeek == dow:
        return date
    return next_dow(date, dow)


def month_day(month: Month, day: Long) -> Date:
    # We may need to return the nearest/next date instead of just using the current year.
    curr_datetime = get_current_datetime()
    return Date(year=curr_datetime.date.year, month=month, day=Day(day.inner))


def next_or_same_month_day(month: Month, day: Day) -> Date:
    today = get_today()
    if month != today.month:
        return month_day(month=month, day=Long(day.inner))

    return Date(year=today.year, month=month, day=day)


def last_day_of_month(month: Month) -> Date:
    raise NotImplementedError()


def last_date_of_month_in_year(month: Month, year: Year) -> Date:
    _, num_days = calendar.monthrange(year.inner, month.inner)
    return Date(
        year=year,
        month=month,
        day=Day(num_days),
    )


def period_before_date(date: Date, period: Period) -> Date:
    neg_period = Period(
        Long(-period.years.inner), Long(-period.months.inner), Long(-period.days.inner)
    )
    return adjust_by_period(date, neg_period)


def holiday_year(holiday: Holiday, year: Year) -> Date:
    month: int
    day: int
    if holiday == Holiday.Easter():
        _year, month, day = holidays.easter(year.inner)
    elif holiday == Holiday.Halloween():
        _year, month, day = holidays.halloween(year.inner)
    elif holiday == Holiday.LaborDay():
        _year, month, day = holidays.labor_day(year.inner)
    elif holiday == Holiday.MemorialDay():
        _year, month, day = holidays.memorial_day(year.inner)
    elif holiday == Holiday.MothersDay():
        _year, month, day = holidays.mothers_day(year.inner)
    elif holiday == Holiday.NewYearsDay():
        _year, month, day = holidays.new_years(year.inner)
    elif holiday == Holiday.NewYearsEve():
        _year, month, day = holidays.new_years_eve(year.inner)
    elif holiday == Holiday.Thanksgiving():
        _year, month, day = holidays.thanksgiving(year.inner)
    elif holiday == Holiday.ValentinesDay():
        _year, month, day = holidays.valentines_day(year.inner)
    elif holiday == Holiday.VeteransDay():
        _year, month, day = holidays.veterans_day(year.inner)
    else:
        raise ValueError(f"Unknown holiday: {holiday}")

    return Date(year=year, month=Month(month), day=Day(day))
