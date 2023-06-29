import datetime
from dataclasses import dataclass
from functools import total_ordering
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.time import Time
from dataflow2text_domains.calflow.schemas.time_zone import TimeZone


# Cannot inherit the `ComparableSchema` because mypy cannot recognize `@total_ordering` properly.
@total_ordering
@dataclass(frozen=True)
class DateTime(NullaryStructSchema):
    date: Date
    time: Time
    timeZone: TimeZone

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "DateTime":
        schema = json_obj.get("schema")
        assert schema == "DateTime"
        underlying = json_obj.get("underlying")

        return DateTime(
            date=Date.from_typed_json(underlying.get("date")),
            time=Time.from_typed_json(underlying.get("time")),
            timeZone=TimeZone.from_typed_json(underlying.get("timeZone")),
        )

    def to_python_datetime(self) -> datetime.datetime:
        return datetime.datetime(
            year=int(self.date.year.inner),
            month=self.date.month.inner,
            day=int(self.date.day.inner),
            hour=int(self.time.hour.inner),
            minute=int(self.time.minute.inner),
            second=int(self.time.second.inner),
            microsecond=int(self.time.nanosecond.inner / 1000),
            tzinfo=self.timeZone.to_python_timezone(),
        )

    def __eq__(self, other) -> bool:
        """Overwrites the default so the value is normalized based on timezone."""
        if not isinstance(other, DateTime):
            raise ValueError(f"Cannot compare {self} with {other}.")

        return self.to_python_datetime() == other.to_python_datetime()

    def __lt__(self, other) -> bool:
        if not isinstance(other, DateTime):
            raise ValueError(f"Cannot compare {self} with {other}.")

        return self.to_python_datetime() < other.to_python_datetime()
