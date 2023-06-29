from dataflow2text.dataflow.schema import Long, Number
from dataflow2text_domains.calflow.schemas.period import Period


def to_days(days: Number) -> Period:
    return Period(days=days.to_long())


def to_weeks(weeks: Number) -> Period:
    return Period(days=Long(int(weeks.inner) * 7))
