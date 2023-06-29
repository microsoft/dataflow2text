from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Number
from dataflow2text_domains.calflow.helpers.period_helpers import to_days, to_weeks
from dataflow2text_domains.calflow.schemas.period import Period


@function
def toDays(days: Number) -> Period:
    return to_days(days)


@function
def toWeeks(weeks: Number) -> Period:
    return to_weeks(weeks)


@function
def toMonths(months: Number) -> Period:
    return Period(months=months.to_long())


@function
def toYears(years: Number) -> Period:
    return Period(years=years.to_long())


@function
def addPeriods(x: Period, y: Period) -> Period:
    raise NotImplementedError()
