from dataclasses import dataclass

from dateutil.relativedelta import relativedelta

from dataflow2text.dataflow.schema import Long, NullaryStructSchema
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.period import Period


@dataclass(frozen=True)
class PeriodDuration(NullaryStructSchema):
    period: Period = Period()
    duration: Duration = Duration(seconds=Long(0))

    def to_python_relativedelta(self):
        return relativedelta(
            years=int(self.period.years.inner),
            months=int(self.period.months.inner),
            days=int(self.period.days.inner),
            seconds=int(self.duration.seconds.inner),
            microseconds=int(self.duration.nanoseconds.inner / 1000),
        )
