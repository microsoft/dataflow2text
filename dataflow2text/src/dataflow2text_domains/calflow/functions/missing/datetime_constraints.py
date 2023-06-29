from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.period_duration import PeriodDuration


@function
def LessThanFromStructDateTime(
    dateTimeConstraint: Constraint[DateTime],
) -> Constraint[DateTime]:
    raise NotImplementedError()


@function
def GreaterThanFromStructDateTime(
    dateTimeConstraint: Constraint[DateTime],
) -> Constraint[DateTime]:
    raise NotImplementedError()


@function
def LastDuration(periodDuration: PeriodDuration) -> Constraint[DateTime]:
    raise NotImplementedError()
