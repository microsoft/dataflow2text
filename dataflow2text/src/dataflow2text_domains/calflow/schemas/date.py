import datetime
from dataclasses import dataclass, field
from functools import total_ordering
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.year import Year


@total_ordering
@dataclass
class Date(NullaryStructSchema):
    year: Year
    month: Month
    day: Day
    dayOfWeek: DayOfWeek = field(init=False, repr=False)

    def __post_init__(self):
        self.dayOfWeek = DayOfWeek(self.to_python_date().weekday())

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Date":
        schema = json_obj.get("schema")
        assert schema == "Date"
        underlying = json_obj.get("underlying")

        return Date(
            year=Year.from_typed_json(underlying.get("year")),
            month=Month.from_typed_json(underlying.get("month")),
            day=Day.from_typed_json(underlying.get("day")),
        )

    def to_python_date(self) -> datetime.date:
        return datetime.date(
            year=int(self.year.inner),
            month=self.month.inner,
            day=int(self.day.inner),
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Date):
            raise ValueError(f"Cannot compare {self} with {other}.")

        return self.to_python_date() < other.to_python_date()
