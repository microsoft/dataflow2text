"""Factory methods for creating dataflow values.

These correspond to the `apply` methods (e.g., `Day.apply`) in Lispress/Express.
"""
from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, Long, Option, String, TSchema
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase
from dataflow2text_domains.calflow.schemas.path import Path
from dataflow2text_domains.calflow.schemas.period import Period
from dataflow2text_domains.calflow.schemas.period_duration import PeriodDuration
from dataflow2text_domains.calflow.schemas.person_name import PersonName
from dataflow2text_domains.calflow.schemas.respond_comment import RespondComment
from dataflow2text_domains.calflow.schemas.response_should_send import RespondShouldSend
from dataflow2text_domains.calflow.schemas.year import Year


@function
def Day_apply(value: Long) -> Day:
    return Day(value.inner)


@function
def LocationKeyphrase_apply(inner: String) -> LocationKeyphrase:
    return LocationKeyphrase(inner.inner)


@function
def Path_apply(inner: String) -> Path:
    return Path(inner.inner)


@function
def PeriodDuration_apply(
    period: Period = Period(), duration: Duration = Duration()
) -> PeriodDuration:
    return PeriodDuration(period, duration)


@function
def PersonName_apply(name: String) -> PersonName:
    return PersonName(name)


@function
def RespondComment_apply(value: String) -> RespondComment:
    return RespondComment(value.inner)


@function
def RespondShouldSend_apply(value: Boolean) -> RespondShouldSend:
    return RespondShouldSend(value.inner)


@function
def Year_apply(value: Long) -> Year:
    return Year(value.inner)


@function
def Option_apply(value: TSchema) -> Option[TSchema]:
    return Option.from_value(value)
