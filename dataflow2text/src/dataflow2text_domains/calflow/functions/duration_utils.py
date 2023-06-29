from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long, Number
from dataflow2text_domains.calflow.schemas.duration import Duration


@function
def toHours(hours: Number) -> Duration:
    return Duration(seconds=Long(int(hours.inner) * 60 * 60))


@function
def toMinutes(minutes: Number) -> Duration:
    return Duration(seconds=Long(int(minutes.inner) * 60))


@function
def toSeconds(seconds: Number) -> Duration:
    return Duration(seconds=seconds.to_long())


@function
def addDurations(x: Duration, y: Duration) -> Duration:
    return Duration(seconds=Long(x.seconds.inner + y.seconds.inner))


@function
def subtractDurations(x: Duration, y: Duration) -> Duration:
    return Duration(seconds=Long(x.seconds.inner - y.seconds.inner))
