from dataclasses import dataclass

from dateutil.relativedelta import relativedelta

from dataflow2text.dataflow.schema import Long, NullaryStructSchema


@dataclass(frozen=True)
class Period(NullaryStructSchema):
    years: Long = Long(0)
    months: Long = Long(0)
    days: Long = Long(0)

    def to_python_relativedelta(self):
        return relativedelta(
            years=int(self.years.inner),
            months=int(self.months.inner),
            days=int(self.days.inner),
        )
