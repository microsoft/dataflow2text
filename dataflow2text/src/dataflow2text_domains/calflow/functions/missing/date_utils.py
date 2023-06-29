from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.holiday import Holiday
from dataflow2text_domains.calflow.schemas.month import Month


@function
def previousDayOfMonth(date: Date, day: Long) -> Date:
    raise NotImplementedError()


@function
def ClosestMonthDayToDate(day: Day, month: Month, date: Date) -> Date:
    raise NotImplementedError()


@function
def nextHoliday(date: Date, holiday: Holiday) -> Date:
    raise NotImplementedError()


@function
def previousHoliday(date: Date, holiday: Holiday) -> Date:
    raise NotImplementedError()
