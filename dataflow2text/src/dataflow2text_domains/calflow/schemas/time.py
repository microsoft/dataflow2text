import datetime
from dataclasses import dataclass
from functools import total_ordering
from typing import Any, Dict

from dataflow2text.dataflow.schema import Long, NullaryStructSchema, Number


@total_ordering
@dataclass(frozen=True)
class Time(NullaryStructSchema):
    hour: Long = Long(0)
    minute: Long = Long(0)
    second: Long = Long(0)
    nanosecond: Long = Long(0)

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Time":
        schema = json_obj.get("schema")
        assert schema == "Time"
        underlying = json_obj.get("underlying")

        hour = Number.from_typed_json(underlying.get("hour"))
        minute = Number.from_typed_json(underlying.get("minute"))
        second = Number.from_typed_json(underlying.get("second"))
        nanosecond = Number.from_typed_json(underlying.get("nanosecond"))

        return Time(
            hour=hour.to_long(),
            minute=minute.to_long(),
            second=second.to_long(),
            nanosecond=nanosecond.to_long(),
        )

    def to_python_time(self) -> datetime.time:
        return datetime.time(
            hour=int(self.hour.inner),
            minute=int(self.minute.inner),
            second=int(self.second.inner),
            microsecond=int(self.nanosecond.inner / 1000),
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Time):
            raise ValueError(f"cannot compare{self} with {other}.")

        return self.to_python_time() < other.to_python_time()
