import calendar
import dataclasses
from datetime import timedelta

from convertdate import julian
from dateutil.relativedelta import relativedelta

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long, Number, Option
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_date_to_calflow_date,
)
from dataflow2text_domains.calflow.helpers.date_helpers import (
    last_day_of_month,
    month_day,
    next_dow,
    next_or_same_dow,
    next_or_same_month_day,
    period_before_date,
    previous_or_same_dow,
)
from dataflow2text_domains.calflow.helpers.date_range_constraint_helpers import (
    full_month_of_month,
    next_period,
    week_of_date,
    weekend_of_date,
)
from dataflow2text_domains.calflow.helpers.period_helpers import to_weeks
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_range_constraint import (
    DateRangeConstraint,
)
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.period import Period
from dataflow2text_domains.calflow.schemas.year import Year


@function
def FullMonthofMonth(
    month: Month, year: Option[Year] = Option(Year.dtype_ctor(), None)
) -> DateRangeConstraint:
    return full_month_of_month(month, year)


@function
def FullMonthofLastMonth() -> DateRangeConstraint:
    current_date_py = get_current_datetime().date.to_python_date()
    last_month_py = current_date_py - relativedelta(months=1)
    return full_month_of_month(
        month=Month(last_month_py.month),
        year=Option.from_value(Year(last_month_py.year)),
    )


@function
def FullMonthofPreviousMonth(month: Month) -> DateRangeConstraint:
    current_date = get_current_datetime().date
    if month.inner < current_date.month.inner:
        return full_month_of_month(
            month, Option(type_arg=Year.dtype_ctor(), inner=None)
        )

    return full_month_of_month(
        month=month, year=Option.from_value(Year(current_date.year.inner - 1))
    )


@function
def FullYearofYear(year: Year) -> DateRangeConstraint:
    start_date = Date(year=year, month=Month.January(), day=Day(1))
    end_date = Date(year=year, month=Month.December(), day=Day(31))
    return DateRangeConstraint(start_date=start_date, end_date=end_date)


@function
def LastWeekendOfMonth(month: Month) -> DateRangeConstraint:
    month_end = last_day_of_month(month)
    prev_sunday = previous_or_same_dow(month_end, DayOfWeek.Sunday())
    return weekend_of_date(prev_sunday)


@function
def MonthDayToDay(month: Month, num1: Day, num2: Day) -> DateRangeConstraint:
    return DateRangeConstraint(
        start_date=month_day(month=month, day=Long(num1.inner)),
        end_date=month_day(month=month, day=Long(num2.inner)),
    )


@function
def NumberWeekFromEndOfMonth(number: Long, month: Month) -> DateRangeConstraint:
    assert 0 < number.inner < 5
    return week_of_date(
        date=period_before_date(
            period=to_weeks(Number(number.inner - 1)), date=last_day_of_month(month)
        )
    )


@function
def NumberWeekOfMonth(number: Long, month: Month) -> DateRangeConstraint:
    current_date = get_current_datetime().date
    if current_date.month.inner < month.inner:
        year = current_date.year.inner
    else:
        year = current_date.year.inner + 1
    weeks = julian.monthcalendar(year, month.inner)
    target_week = weeks[number.inner - 1]
    start_day = next(day for day in target_week if day is not None)
    end_day = next(day for day in reversed(target_week) if day is not None)
    start_date = Date(year=current_date.year, month=month, day=Day(start_day))
    end_date = Date(year=current_date.year, month=month, day=Day(end_day))
    return DateRangeConstraint(start_date=start_date, end_date=end_date)


@function
def LastWeekNew() -> DateRangeConstraint:
    """Returns a DateRangeConstraint for dates in last week starting from Sunday and ending on Saturday."""
    current_date_py = get_current_datetime().date.to_python_date()
    last_week_py = current_date_py - relativedelta(weeks=1)
    start_date_py = last_week_py - timedelta(days=last_week_py.weekday() + 1)
    end_date_py = start_date_py + timedelta(days=6)
    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(start_date_py),
        end_date=convert_python_date_to_calflow_date(end_date_py),
    )


@function
def NextWeekList() -> DateRangeConstraint:
    """Returns a DateRangeConstraint for dates in next week starting from Sunday and ending on Saturday."""
    current_date_py = get_current_datetime().date.to_python_date()
    next_week_py = current_date_py + relativedelta(weeks=1)
    start_date_py = next_week_py - timedelta(days=next_week_py.weekday() + 1)
    end_date_py = start_date_py + timedelta(days=6)
    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(start_date_py),
        end_date=convert_python_date_to_calflow_date(end_date_py),
    )


@function
def NextWeekend() -> DateRangeConstraint:
    current_date_py = get_current_datetime().date.to_python_date()
    current_weekday_py = current_date_py.weekday()
    if current_weekday_py in (5, 6):
        next_week_py = current_date_py + relativedelta(weeks=1)
        next_saturday_py = (
            next_week_py - timedelta(days=current_weekday_py) + timedelta(days=5)
        )
    else:
        next_saturday_py = (
            current_date_py - timedelta(days=current_weekday_py) + timedelta(days=5)
        )
    next_sunday_py = next_saturday_py + timedelta(days=1)
    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(next_saturday_py),
        end_date=convert_python_date_to_calflow_date(next_sunday_py),
    )


@function
def ThisWeek() -> DateRangeConstraint:
    """Returns a DateRangeConstraint for dates in this week starting from Sunday and ending on Saturday."""
    current_date = get_current_datetime().date
    current_date_py = current_date.to_python_date()
    start_date_py = current_date_py - timedelta(days=current_date_py.weekday() + 1)
    end_date_py = start_date_py + timedelta(days=6)
    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(start_date_py),
        end_date=convert_python_date_to_calflow_date(end_date_py),
    )


@function
def ThisWeekend() -> DateRangeConstraint:
    current_date_py = get_current_datetime().date.to_python_date()
    this_saturday_py = (
        current_date_py - timedelta(days=current_date_py.weekday()) + timedelta(days=5)
    )
    this_sunday_py = this_saturday_py + timedelta(days=1)
    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(this_saturday_py),
        end_date=convert_python_date_to_calflow_date(this_sunday_py),
    )


@function
def WeekOfDateNew(date: Date) -> DateRangeConstraint:
    return week_of_date(date)


@function
def WeekendOfDate(date: Date) -> DateRangeConstraint:
    return weekend_of_date(date)


@function
def WeekendOfMonth(num: Long, month: Month) -> DateRangeConstraint:
    first_saturday = next_or_same_dow(
        next_or_same_month_day(month=month, day=Day(1)), DayOfWeek.Saturday()
    )
    return weekend_of_date(first_saturday)


@function
def SeasonSpring() -> DateRangeConstraint:
    current_date = get_current_datetime().date
    start_date = Date(year=current_date.year, month=Month.March(), day=Day(1))
    end_date = Date(year=current_date.year, month=Month.May(), day=Day(31))
    if end_date < current_date:
        next_year = Year(current_date.year.inner + 1)
        start_date = dataclasses.replace(start_date, year=next_year)
        end_date = dataclasses.replace(end_date, year=next_year)
    return DateRangeConstraint(start_date=start_date, end_date=end_date)


@function
def SeasonSummer() -> DateRangeConstraint:
    current_date = get_current_datetime().date
    start_date = Date(year=current_date.year, month=Month.June(), day=Day(1))
    end_date = Date(year=current_date.year, month=Month.August(), day=Day(31))
    if end_date < current_date:
        next_year = Year(current_date.year.inner + 1)
        start_date = dataclasses.replace(start_date, year=next_year)
        end_date = dataclasses.replace(end_date, year=next_year)
    return DateRangeConstraint(start_date=start_date, end_date=end_date)


@function
def SeasonFall() -> DateRangeConstraint:
    current_date = get_current_datetime().date
    start_date = Date(year=current_date.year, month=Month.September(), day=Day(1))
    end_date = Date(year=current_date.year, month=Month.November(), day=Day(30))
    if end_date < current_date:
        next_year = Year(current_date.year.inner + 1)
        start_date = dataclasses.replace(start_date, year=next_year)
        end_date = dataclasses.replace(end_date, year=next_year)
    return DateRangeConstraint(start_date=start_date, end_date=end_date)


@function
def SeasonWinter() -> DateRangeConstraint:
    current_date = get_current_datetime().date
    start_date = Date(year=current_date.year, month=Month.December(), day=Day(1))
    next_year_value = int(current_date.year.inner) + 1
    _, num_days = calendar.monthrange(next_year_value, Month.February().inner)
    end_date = Date(
        year=Year(next_year_value), month=Month.February(), day=Day(num_days)
    )
    return DateRangeConstraint(start_date=start_date, end_date=end_date)


@function
def EarlyDateRange(dateRange: DateRangeConstraint) -> DateRangeConstraint:
    """Returns a DateRangeConstraint for dates in the first 3rd of the range [start, end]."""
    start_date_py = dateRange.start_date.to_python_date()
    end_date_py = dateRange.end_date.to_python_date()
    num_total_days = (end_date_py - start_date_py).days + 1
    new_start_date_py = start_date_py + relativedelta(days=int(num_total_days / 3))
    new_start_date = convert_python_date_to_calflow_date(new_start_date_py)
    return DateRangeConstraint(start_date=new_start_date, end_date=dateRange.end_date)


@function
def LateDateRange(dateRange: DateRangeConstraint) -> DateRangeConstraint:
    """Returns a DateRangeConstraint for dates in the last 3rd of the range [start, end]."""
    start_date_py = dateRange.start_date.to_python_date()
    end_date_py = dateRange.end_date.to_python_date()
    num_total_days = (end_date_py - start_date_py).days + 1
    new_start_date_py = start_date_py + relativedelta(days=int(2 * num_total_days / 3))
    new_start_date = convert_python_date_to_calflow_date(new_start_date_py)
    return DateRangeConstraint(start_date=new_start_date, end_date=dateRange.end_date)


@function
def LastPeriod(period: Period) -> DateRangeConstraint:
    end_date_py = get_current_datetime().date.to_python_date()
    start_date_py = end_date_py - period.to_python_relativedelta()
    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(start_date_py),
        end_date=convert_python_date_to_calflow_date(end_date_py),
    )


@function
def NextPeriod(period: Period) -> DateRangeConstraint:
    return next_period(period)


@function
def DateAndConstraint(date1: Date, date2: Date) -> DateRangeConstraint:
    return DateRangeConstraint(date1, date2)


@function
def DowToDowOfWeek(
    day1: DayOfWeek, day2: DayOfWeek, week: DateRangeConstraint
) -> DateRangeConstraint:
    range_start = next_dow(week.start_date, day1)
    range_end = next_dow(range_start, day2)
    return DateRangeConstraint(range_start, range_end)


@function
def Future() -> DateRangeConstraint:
    """Returns a DateRangeConstraint for dates in 1 week from today."""
    return next_period(to_weeks(Number(1)))
