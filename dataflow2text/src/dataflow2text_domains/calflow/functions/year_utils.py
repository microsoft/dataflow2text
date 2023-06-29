from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.helpers.date_helpers import get_today
from dataflow2text_domains.calflow.schemas.year import Year


@function
def LastYear() -> Year:
    today = get_today()
    return Year(today.year.inner - 1)


@function
def ThisYear() -> Year:
    today = get_today()
    return Year(today.year.inner)


@function
def NextYear() -> Year:
    today = get_today()
    return Year(today.year.inner + 1)


@function
def toFourDigitYear(number: Long) -> Year:
    assert 0 <= number.inner <= 9999
    return Year(number.inner)
