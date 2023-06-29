from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.time import Time


@dataclass(frozen=True)
class OpenPeriod(NullaryStructSchema):
    open_day: DayOfWeek
    open_time: Time
    close_day: DayOfWeek
    close_time: Time
