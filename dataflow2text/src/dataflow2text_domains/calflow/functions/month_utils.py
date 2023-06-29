from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.helpers.date_helpers import get_today
from dataflow2text_domains.calflow.schemas.month import Month


@function
def toMonth(month: Long) -> Month:
    return Month(month.inner)


@function
def NextMonth() -> Month:
    today = get_today().to_python_date()
    next_month = today.month + 1
    if next_month == 13:
        next_month = 1
    return Month(next_month)
