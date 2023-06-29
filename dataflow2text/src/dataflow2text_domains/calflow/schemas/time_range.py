from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.date_time import DateTime


@dataclass(frozen=True)
class TimeRange(NullaryStructSchema):
    start: DateTime
    end: DateTime
